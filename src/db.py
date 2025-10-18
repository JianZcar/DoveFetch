import sqlite3
from passlib.hash import sha512_crypt
from cryptography.fernet import Fernet, InvalidToken


def create_db(path: str, key: bytes):
    f = Fernet(key)

    conn = sqlite3.connect(path)

    schema_users = """
    CREATE TABLE IF NOT EXISTS users (
        userid TEXT PRIMARY KEY,
        hashed_password TEXT NOT NULL,
        encrypted_password TEXT NOT NULL
    );
    """
    conn.execute(schema_users)

    schema_auth = """
    CREATE TABLE IF NOT EXISTS auth (
        master_key TEXT NOT NULL
    );
    """
    conn.execute(schema_auth)

    cursor = conn.execute("SELECT COUNT(*) FROM auth")
    if cursor.fetchone()[0] == 0:
        encrypted_auth = f.encrypt(b"auth").decode()
        conn.execute("INSERT INTO auth (master_key) VALUES (?)",
                     (encrypted_auth,))

    conn.commit()
    conn.close()
    print(f"Created (or verified) DB at: {path}")


def add_user(db_path: str, userid: str, password: str, key: bytes):
    f = Fernet(key)

    hashed = sha512_crypt.hash(password)
    prefix = "{SHA512-CRYPT}"
    hashed_stored = f"{prefix}{hashed}"

    encrypted_stored = f.encrypt(password.encode()).decode()

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO users (userid, hashed_password, encrypted_password) "
            "VALUES (?, ?, ?)",
            (userid, hashed_stored, encrypted_stored)
        )
        conn.commit()
        print(f"Added user {userid}")
    except sqlite3.IntegrityError:
        print(f"User {userid} already exists")
    finally:
        conn.close()


def list_users(db_path: str, key: bytes):
    f = Fernet(key)
    users = []

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT userid, hashed_password, encrypted_password "
        "FROM users "
        "ORDER BY userid"
    )

    for userid, hashed, enc in cursor:
        try:
            dec_pw = f.decrypt(enc.encode()).decode()
        except Exception:
            dec_pw = None
        users.append((userid, hashed, dec_pw))

    conn.close()
    return users


def delete_user(db_path: str, userid: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("DELETE FROM users WHERE userid = ?", (userid,))
    conn.commit()
    if cursor.rowcount:
        print(f"Deleted user {userid}")
    else:
        print(f"User {userid} not found")
    conn.close()


def get_password(db_path: str, userid: str, master_key: bytes) -> str | None:
    f = Fernet(master_key)
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT encrypted_password FROM users WHERE userid = ?", (userid,)
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    try:
        return f.decrypt(row[0].encode()).decode()
    except InvalidToken:
        print("Invalid master key")
        return None


def verify_key(db_path: str, key: bytes) -> bool:
    f = Fernet(key)
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT master_key FROM auth")
    stored = cursor.fetchone()[0]
    conn.close()
    try:
        return f.decrypt(stored.encode()) == b"auth"
    except InvalidToken:
        return False
