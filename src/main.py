import os
import sys
import time
import threading

from db import create_db, verify_key
from shell import MailShell
from dovecot import run_dovecot
from fetcher import run_fetcher
from utils.key import generate_key, key_from_string


def main():
    global FETCHER_RUNNING
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

    time.sleep(10)

    MailShell(db_path, key).cmdloop()


if __name__ == "__main__":
    main()
