import os
import time
import asyncio
import threading
from pathlib import Path
from poplib import POP3_SSL
from imapclient import IMAPClient

# === CONFIGURATION ===
MAILDIR = Path("/mail")
POP_HOST = "disroot.org"
IMAP_HOST = "disroot.org"

POP_USER = IMAP_USER = os.environ.get("EMAIL")
POP_PASS = IMAP_PASS = os.environ.get("EMAIL_PASS")

POLL_INTERVAL = 300

# === SETUP MAILDIR ===
for sub in ("cur", "new", "tmp"):
    (MAILDIR / sub).mkdir(parents=True, exist_ok=True)


def save_to_maildir(message_bytes):
    """Save message into Maildir/new"""
    timestamp = int(time.time() * 1000000)
    filename = f"{timestamp}.eml"
    filepath = MAILDIR / "new" / filename
    with open(filepath, "wb") as f:
        f.write(message_bytes)
    print(f"[Maildir] Saved mail → {filepath}")


def fetch_pop3():
    """Fetch messages via POP3, save locally, and delete them."""
    try:
        pop = POP3_SSL(POP_HOST, timeout=30)
        pop.user(POP_USER)
        pop.pass_(POP_PASS)

        num_messages = len(pop.list()[1])

        if num_messages == 0:
            pop.quit()
            return

        print(f"[POP3] {num_messages} messages found")
        for i in range(num_messages):
            _, lines, _ = pop.retr(i + 1)
            message_bytes = b"\n".join(lines)
            save_to_maildir(message_bytes)
            pop.dele(i + 1)

        print("[POP3] Fetch + delete done")
        pop.quit()
    except Exception as e:
        print(f"[POP3] Error: {e}")


async def idle_imap():
    """Use IMAP IDLE to wait for new messages in real time."""
    while True:
        try:
            with IMAPClient(IMAP_HOST, ssl=True) as client:
                client.login(IMAP_USER, IMAP_PASS)
                client.select_folder("INBOX")
                print("[IMAP] Connected, entering IDLE mode...")

                while True:
                    client.idle()
                    responses = client.idle_check(timeout=30)
                    client.idle_done()

                    if responses:
                        print("[IMAP] New mail detected!")
                        fetch_pop3()

        except Exception as e:
            print(f"[IMAP] Error: {e}, reconnecting in 10s")
            await asyncio.sleep(10)


def pop_poll_loop():
    """Regular polling fallback."""
    while True:
        fetch_pop3()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    threading.Thread(target=pop_poll_loop, daemon=True).start()
    asyncio.run(idle_imap())
