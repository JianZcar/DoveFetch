import time
import asyncio
import threading
from pathlib import Path
from poplib import POP3_SSL
from imapclient import IMAPClient

from db import list_users, get_password

POP_HOST = IMAP_HOST = "disroot.org"
POLL_INTERVAL = 300


def setup_maildir(userid):
    """Ensure Maildir structure exists for a user"""
    maildir = Path("/mail") / userid
    for sub in ("cur", "new", "tmp"):
        (maildir / sub).mkdir(parents=True, exist_ok=True)
    return maildir


def save_to_maildir(maildir: Path, message_bytes):
    timestamp = int(time.time() * 1_000_000)
    filename = f"{timestamp}.eml"
    filepath = maildir / "new" / filename
    with open(filepath, "wb") as f:
        f.write(message_bytes)
    print(f"[Maildir:{maildir.name}] Saved mail → {filepath}")


def fetch_pop3(userid: str, password: str):
    maildir = setup_maildir(userid)
    try:
        pop = POP3_SSL(POP_HOST, timeout=30)
        pop.user(userid)
        pop.pass_(password)

        num_messages = len(pop.list()[1])
        if num_messages == 0:
            pop.quit()
            return

        print(f"[POP3:{userid}] {num_messages} messages found")
        for i in range(num_messages):
            _, lines, _ = pop.retr(i + 1)
            message_bytes = b"\n".join(lines)
            save_to_maildir(maildir, message_bytes)
            pop.dele(i + 1)

        print(f"[POP3:{userid}] Fetch + delete done")
        pop.quit()
    except Exception as e:
        print(f"[POP3:{userid}] Error: {e}")


async def idle_imap(userid: str, password: str):
    setup_maildir(userid)
    while True:
        try:
            with IMAPClient(IMAP_HOST, ssl=True) as client:
                client.login(userid, password)
                client.select_folder("INBOX")
                print(f"[IMAP:{userid}] Connected, entering IDLE mode...")

                while True:
                    client.idle()
                    responses = client.idle_check(timeout=30)
                    client.idle_done()

                    if responses:
                        print(f"[IMAP:{userid}] New mail detected!")
                        fetch_pop3(userid, password)

        except Exception as e:
            print(f"[IMAP:{userid}] Error: {e}, reconnecting in 10s")
            await asyncio.sleep(10)


def pop_poll_loop(userid: str, password: str):
    while True:
        fetch_pop3(userid, password)
        time.sleep(POLL_INTERVAL)


def run_fetcher(db_path: str, key: bytes):
    users = list_users(db_path, key)
    if not users:
        print("No users found")
        return

    for userid, _, enc_pw in users:
        password = get_password(db_path, userid, key)
        if password is None:
            continue
        threading.Thread(
            target=pop_poll_loop, args=(userid, password), daemon=True
        ).start()

    async def main_idle():
        tasks = []
        for userid, _, enc_pw in users:
            password = get_password(db_path, userid, key)
            if password is None:
                continue
            tasks.append(asyncio.create_task(idle_imap(userid, password)))
        await asyncio.gather(*tasks)

    asyncio.run(main_idle())
