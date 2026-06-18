"""Credential vault — real Fernet encryption round-trips (spec 13.2)."""
import pytest

from app.vault import Vault, VaultError, _key_from_secret


def _vault():
    return Vault(_key_from_secret("a-test-secret"))


def test_encrypt_decrypt_roundtrip():
    v = _vault()
    token = v.encrypt("super-secret-access-token")
    assert token != "super-secret-access-token"          # actually encrypted
    assert v.decrypt(token) == "super-secret-access-token"


def test_dict_roundtrip():
    v = _vault()
    secrets = {"client_id": "abc", "secret": "xyz", "access_token": "tok"}
    token = v.encrypt_dict(secrets)
    assert v.decrypt_dict(token) == secrets


def test_wrong_key_fails_closed():
    token = _vault().encrypt("x")
    other = Vault(_key_from_secret("different-secret"))
    with pytest.raises(VaultError):
        other.decrypt(token)


def test_from_config_derives_key_without_explicit_vault_key():
    v = Vault.from_config({"SECRET_KEY": "s"})
    assert v.decrypt(v.encrypt("hello")) == "hello"
