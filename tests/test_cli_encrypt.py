"""Tests for the encrypt CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envswitch.cli_encrypt import cmd_encrypt
from envswitch.encrypt import generate_key, encrypt_value


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def enc_key():
    return generate_key()


def invoke(runner, *args, **kwargs):
    return runner.invoke(cmd_encrypt, *args, **kwargs)


def test_keygen_outputs_key(runner):
    result = invoke(runner, ["keygen"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 10


def test_lock_profile_success(runner, enc_key):
    profiles = {"dev": {"SECRET": "mysecret", "HOST": "localhost"}}
    with patch("envswitch.cli_encrypt.load_profiles", return_value=profiles), \
         patch("envswitch.cli_encrypt.save_profiles") as mock_save:
        result = invoke(runner, ["lock", "dev", "--key", enc_key])
        assert result.exit_code == 0
        assert "encrypted" in result.output
        saved = mock_save.call_args[0][0]
        assert saved["dev"]["SECRET"].startswith("enc:")
        assert saved["dev"]["HOST"].startswith("enc:")


def test_lock_profile_selective_keys(runner, enc_key):
    profiles = {"dev": {"SECRET": "mysecret", "HOST": "localhost"}}
    with patch("envswitch.cli_encrypt.load_profiles", return_value=profiles), \
         patch("envswitch.cli_encrypt.save_profiles") as mock_save:
        result = invoke(runner, ["lock", "dev", "--key", enc_key, "--only", "SECRET"])
        assert result.exit_code == 0
        saved = mock_save.call_args[0][0]
        assert saved["dev"]["SECRET"].startswith("enc:")
        assert saved["dev"]["HOST"] == "localhost"


def test_lock_profile_not_found(runner, enc_key):
    with patch("envswitch.cli_encrypt.load_profiles", return_value={}):
        result = invoke(runner, ["lock", "ghost", "--key", enc_key])
        assert result.exit_code != 0
        assert "not found" in result.output


def test_unlock_profile_success(runner, enc_key):
    encrypted_val = "enc:" + encrypt_value("mysecret", enc_key)
    profiles = {"dev": {"SECRET": encrypted_val, "HOST": "localhost"}}
    with patch("envswitch.cli_encrypt.load_profiles", return_value=profiles), \
         patch("envswitch.cli_encrypt.save_profiles") as mock_save:
        result = invoke(runner, ["unlock", "dev", "--key", enc_key])
        assert result.exit_code == 0
        assert "decrypted" in result.output
        saved = mock_save.call_args[0][0]
        assert saved["dev"]["SECRET"] == "mysecret"
        assert saved["dev"]["HOST"] == "localhost"


def test_unlock_profile_not_found(runner, enc_key):
    with patch("envswitch.cli_encrypt.load_profiles", return_value={}):
        result = invoke(runner, ["unlock", "ghost", "--key", enc_key])
        assert result.exit_code != 0
        assert "not found" in result.output


def test_unlock_wrong_key_shows_error(runner, enc_key):
    other_key = generate_key()
    encrypted_val = "enc:" + encrypt_value("mysecret", enc_key)
    profiles = {"dev": {"SECRET": encrypted_val}}
    with patch("envswitch.cli_encrypt.load_profiles", return_value=profiles), \
         patch("envswitch.cli_encrypt.save_profiles"):
        result = invoke(runner, ["unlock", "dev", "--key", other_key])
        assert result.exit_code != 0
        assert "Error" in result.output
