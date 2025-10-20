import subprocess
from pathlib import Path


def run_nginx():
    log_path = Path("/mail/nginx.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("a")

    subprocess.Popen(
        ["nginx", "-g", "daemon off;"],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        close_fds=True,
        start_new_session=True,
    )
