"""Encryption support for sensitive profile values using Fernet symmetric encryption."""

import base64
import os
from cryptography.fernet import Fernet, InvalidToken


class EncryptError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def generate_key() -> str:
    """Generate a new Fernet key, returned as a string."""
    return Fernet.generate_key().decode()


def _get_fernet(key: str) -> Fernet:
    try:
        return Fernet(key.encode())
    except Exception:
        raise EncryptError(f"Invalid encryption key.")


def encrypt_value(value: str, key: str) -> str:
    """Encrypt a plaintext string value. Returns base64-encoded ciphertext."""
    f = _get_fernet(key)
    return f.encrypt(value.encode()).decode()


def decrypt_value(token: str, key: str) -> str:
    """Decrypt a ciphertext token back to plaintext."""
    f = _get_fernet(key)
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken:
        raise EncryptError("Decryption failed: invalid token or wrong key.")


def encrypt_profile(profile: dict, key: str, keys_to_encrypt: list[str] | None = None) -> dict:
    """Return a new profile dict with specified (or all) values encrypted."""
    result = {}
    for k, v in profile.items():
        if keys_to_encrypt is None or k in keys_to_encrypt:
            result[k] = "enc:" + encrypt_value(v, key)
        else:
            result[k] = v
    return result


def decrypt_profile(profile: dict, key: str) -> dict:
    """Return a new profile dict with all enc:-prefixed values decrypted."""
    result = {}
    for k, v in profile.items():
        if isinstance(v, str) and v.startswith("enc:"):
            result[k] = decrypt_value(v[4:], key)
        else:
            result[k] = v
    return result
