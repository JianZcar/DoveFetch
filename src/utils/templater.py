import subprocess


def env_substitution(template_path: str, output_path: str) -> None:
    cmd = f"envsubst < {template_path} | sudo tee {output_path} > /dev/null"
    subprocess.run(cmd, shell=True, check=True)
