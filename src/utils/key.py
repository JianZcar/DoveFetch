from cryptography.fernet import Fernet


def generate_key() -> str:
    return Fernet.generate_key().decode()


def key_from_string(key_str: str) -> bytes:
    return key_str.encode()
