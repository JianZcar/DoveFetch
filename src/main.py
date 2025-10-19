import os
import sys
import threading

from shell import MailShell
from nginx import run_nginx
from stunnel import run_stunnel
from dovecot import run_dovecot
from fetcher import run_fetcher
from authproxy import run_authproxy
from db import create_db, verify_key
from utils.key import generate_key, key_from_string


def main():
    db_path = "/mail/sqlite.db"

    if os.path.exists(db_path):
        env_key = os.environ.get("KEY")
        if not env_key:
            sys.exit("KEY environment variable not set.")
        key = key_from_string(env_key)
        if not verify_key(db_path, key):
            sys.exit("Wrong key")

    else:
        key = generate_key()
        print(f"key: {key}")
        create_db(db_path, key)

    threading.Thread(target=run_fetcher, args=(
        db_path, key), daemon=True).start()
    run_dovecot()

    threading.Thread(
        target=run_authproxy, daemon=True).start()
    run_stunnel()
    run_nginx()

    MailShell(db_path, key).cmdloop()


if __name__ == "__main__":
    main()
