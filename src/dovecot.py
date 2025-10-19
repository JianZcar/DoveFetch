from pathlib import Path
import subprocess

from utils.templater import env_substitution


def generate_dovecot_conf():
    template_path = "dovecot.conf.template"
    output_path = "/etc/dovecot/dovecot.conf"
    env_substitution(template_path, output_path)


def run_dovecot():
    generate_dovecot_conf()
    Path("/mail/dovecot.log").touch(exist_ok=True)
    subprocess.Popen(
        ["sudo", "dovecot", "-c", "/etc/dovecot/dovecot.conf"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        start_new_session=True,
    )
