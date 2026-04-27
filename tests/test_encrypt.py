"""Tests for envswitch.encrypt module."""

import pytest
from envswitch.encrypt import (
    generate_key,
    encrypt_value,
    decrypt_value,
    encrypt_profile,
    decrypt_profile,
    EncryptError,
)


@pytest.fixture
def key():
    return generate_key()


def test_generate_key_is_string(key):
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_decrypt_roundtrip(key):
    original = "super_secret_value"
    token = encrypt_value(original, key)
    assert decrypt_value(token, key) == original


def test_encrypt_value_differs_from_original(key):
    value = "mysecret"
    assert encrypt_value(value, key) != value


def test_decrypt_wrong_key_raises(key):
    other_key = generate_key()
    token = encrypt_value("hello", key)
    with pytest.raises(EncryptError, match="Decryption failed"):
        decrypt_value(token, other_key)


def test_invalid_key_raises():
    with pytest.raises(EncryptError, match="Invalid encryption key"):
        encrypt_value("value", "not-a-valid-key")


def test_encrypt_profile_all_keys(key):
    profile = {"DB_PASS": "secret", "API_KEY": "abc123"}
    encrypted = encrypt_profile(profile, key)
    for k, v in encrypted.items():
        assert v.startswith("enc:")


def test_encrypt_profile_selective_keys(key):
    profile = {"DB_PASS": "secret", "HOST": "localhost"}
    encrypted = encrypt_profile(profile, key, keys_to_encrypt=["DB_PASS"])
    assert encrypted["DB_PASS"].startswith("enc:")
    assert encrypted["HOST"] == "localhost"


def test_decrypt_profile_roundtrip(key):
    profile = {"DB_PASS": "secret", "HOST": "localhost"}
    encrypted = encrypt_profile(profile, key)
    decrypted = decrypt_profile(encrypted, key)
    assert decrypted == profile


def test_decrypt_profile_skips_non_encrypted(key):
    profile = {"HOST": "localhost", "PORT": "5432"}
    result = decrypt_profile(profile, key)
    assert result == profile


def test_decrypt_profile_mixed(key):
    profile = {"SECRET": "enc:" + encrypt_value("topsecret", key), "HOST": "localhost"}
    result = decrypt_profile(profile, key)
    assert result["SECRET"] == "topsecret"
    assert result["HOST"] == "localhost"
