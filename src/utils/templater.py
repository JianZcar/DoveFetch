import subprocess


def env_substitution(template_path: str, output_path: str) -> None:
    cmd = f"envsubst < {template_path} > {output_path}"
    subprocess.run(cmd, shell=True, check=True)
