from pathlib import Path
import subprocess


def run_dovecot():
    Path("/mail/dovecot.log").touch(exist_ok=True)
    subprocess.Popen(
        ["dovecot", "-c", "/etc/dovecot/dovecot.conf"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        start_new_session=True,
    )
