import subprocess


def run_dovecot():
    subprocess.Popen(
        ["dovecot", "-c", "/etc/dovecot/dovecot.conf"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        start_new_session=True,
    )
