import os
import ssl
import time
import asyncio
import threading
import logging

from pathlib import Path
from poplib import POP3_SSL
from imapclient import IMAPClient

from db import list_users, get_password

# Default hosts
DEFAULT_POP_HOST = DEFAULT_IMAP_HOST = "disroot.org"


CTX = ssl.create_default_context()
CTX.check_hostname = True
CTX.verify_mode = ssl.CERT_REQUIRED

KNOWN_SERVER = {
    "disroot.org": ("disroot.org", "disroot.org"),
}

POLL_INTERVAL = 300
STOP_EVENT = threading.Event()

LOG_PATH = "/mail/fetcher.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("fetcher")


def setup_maildir(userid):
    maildir = Path("/mail") / userid
    indexdir = Path("/mail") / "indexes" / userid

    for folder in ("cur", "new", "tmp"):
        (maildir / folder).mkdir(parents=True, exist_ok=True)

    for folder in (".Drafts", ".INBOX", ".Sent"):
        folder_path = indexdir / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        for filename in ("dovecot.index",
                         "dovecot.index.cache",
                         "dovecot.index.log"):
            file_path = folder_path / filename
            file_path.touch(exist_ok=True)

    for filename in ("dovecot.list.index.log",
                     "dovecot.mailbox.log"):
        file_path = indexdir / filename
        file_path.touch(exist_ok=True)

    return maildir


def save_to_maildir(maildir: Path, message_bytes):
    timestamp = int(time.time() * 1_000_000)
    filename = f"{timestamp}.eml"
    filepath = maildir / "new" / filename
    with open(filepath, "wb") as f:
        f.write(message_bytes)
    logger.info(f"[Maildir:{maildir.name}] Saved mail → {filepath}")


def _hosts_for_user(userid: str):
    if "@" not in userid:
        return DEFAULT_POP_HOST, DEFAULT_IMAP_HOST
    _, domain = userid.rsplit("@", 1)
    hosts = KNOWN_SERVER.get(domain)
    return hosts[0], hosts[1]


def fetch_pop3(userid: str, password: str, pop_host: str = None):
    maildir = setup_maildir(userid)
    try:
        pop_host = pop_host or DEFAULT_POP_HOST
        pop = POP3_SSL(pop_host, timeout=30, context=CTX)
        pop.user(userid)
        pop.pass_(password)

        num_mails = len(pop.list()[1])
        if num_mails == 0:
            pop.quit()
            return

        logger.info(f"[POP3:{userid}] {num_mails} mails found")
        for i in range(num_mails):
            _, lines, _ = pop.retr(i + 1)
            message_bytes = b"\n".join(lines)
            save_to_maildir(maildir, message_bytes)
            pop.dele(i + 1)

        logger.info(f"[POP3:{userid}] Fetch + delete done")
        pop.quit()
    except Exception as e:
        logger.error(f"[POP3:{userid}] Error: {e}")


async def idle_imap(userid: str, password: str, imap_host: str = None):
    setup_maildir(userid)
    while not STOP_EVENT.is_set():
        try:
            imap_host = imap_host or DEFAULT_IMAP_HOST
            with IMAPClient(imap_host, ssl=True,
                            ssl_context=CTX) as client:
                client.login(userid, password)
                client.select_folder("INBOX")
                logger.info(f"[IMAP:{userid}] Connected")

                while not STOP_EVENT.is_set():
                    client.idle()
                    responses = client.idle_check(timeout=5)
                    client.idle_done()

                    if responses:
                        logger.info(f"[IMAP:{userid}] New mail detected!")
                        pop_host, _ = _hosts_for_user(userid)
                        fetch_pop3(userid, password, pop_host=pop_host)

        except Exception as e:
            logger.warning(f"[IMAP:{userid}] Error: {e}, reconnecting in 10s")
            await asyncio.sleep(10)


def pop_poll_loop(userid: str, password: str, pop_host: str):
    while not STOP_EVENT.is_set():
        try:
            fetch_pop3(userid, password, pop_host=pop_host)
        except Exception as e:
            logger.error(f"[POP3:{userid}] fetch error: {e}")
        STOP_EVENT.wait(POLL_INTERVAL)


def run_fetcher(db_path: str, key: bytes):
    Path("/mail/fetcher.log").touch(exist_ok=True)
    while True:
        if STOP_EVENT.is_set():
            time.sleep(1)
            continue

        users = list_users(db_path, key)
        if not users:
            logger.info("No users found")
            return

        for userid, _, enc_pw in users:
            password = get_password(db_path, userid, key)
            if password is None:
                continue
            pop_host, imap_host = _hosts_for_user(userid)
            threading.Thread(
                target=pop_poll_loop, args=(
                    userid, password, pop_host), daemon=True
            ).start()

        async def main_idle():
            tasks = []
            for userid, _, enc_pw in users:
                password = get_password(db_path, userid, key)
                if password is None:
                    continue
                pop_host, imap_host = _hosts_for_user(userid)
                tasks.append(
                    asyncio.create_task(
                        idle_imap(userid, password, imap_host=imap_host))
                )
            if tasks:
                await asyncio.gather(*tasks)

        asyncio.run(main_idle())
        STOP_EVENT.wait()


def start_fetcher():
    STOP_EVENT.clear()
    print("Fetcher stop signal cleared")
    logger.info("Fetcher stop signal cleared")


def stop_fetcher():
    STOP_EVENT.set()
    print("Fetcher stop signal sent.")
    logger.info("Fetcher stop signal sent.")
