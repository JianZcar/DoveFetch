import subprocess


def run_stunnel():
    subprocess.Popen(
        ["stunnel", "/etc/stunnel/stunnel.conf"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        start_new_session=True,
    )
