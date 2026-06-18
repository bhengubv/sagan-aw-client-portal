"""Credential vault (spec 6.2, 11, 13.2).

Real symmetric encryption (Fernet/AES-128-CBC + HMAC) for provider credentials at rest.
The key comes from VAULT_KEY (a urlsafe-base64 Fernet key) in production; for local/dev it
is derived deterministically from SECRET_KEY so the vault is functional out of the box.
"""
from __future__ import annotations

import base64
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken


class VaultError(Exception):
    pass


def _key_from_secret(secret: str) -> bytes:
    """Derive a valid 32-byte urlsafe-base64 Fernet key from an arbitrary secret."""
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


class Vault:
    def __init__(self, key: bytes):
        self._f = Fernet(key)

    @classmethod
    def from_config(cls, config) -> "Vault":
        key = config.get("VAULT_KEY")
        if key:
            key = key.encode() if isinstance(key, str) else key
        else:
            key = _key_from_secret(config.get("SECRET_KEY", "dev-only-change-me"))
        return cls(key)

    def encrypt(self, plaintext: str) -> str:
        return self._f.encrypt(plaintext.encode("utf-8")).decode("ascii")

    def decrypt(self, token: str) -> str:
        try:
            return self._f.decrypt(token.encode("ascii")).decode("utf-8")
        except InvalidToken as e:
            raise VaultError("could not decrypt credential (wrong key?)") from e

    # Convenience for JSON credential blobs.
    def encrypt_dict(self, data: dict) -> str:
        return self.encrypt(json.dumps(data, separators=(",", ":")))

    def decrypt_dict(self, token: str) -> dict:
        return json.loads(self.decrypt(token))


def get_vault() -> "Vault":
    from flask import current_app
    return Vault.from_config(current_app.config)
