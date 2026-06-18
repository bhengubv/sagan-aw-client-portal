"""Provider interface + real HTTP plumbing (spec 6.1, 8.7, 11).

Input providers implement collect() -> {field_key: FieldValue}. They make REAL HTTP
calls to the provider's API (a live URL in production, the bundled sandbox in dev).
Output providers (Dropbox, Canva) push generated reports out.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import requests

DEFAULT_TIMEOUT = 15


class ProviderError(Exception):
    pass


@dataclass
class FieldValue:
    key: str
    value: str
    source: str                # provider name, e.g. "plaid"
    is_fresh: bool = True       # provider-reported staleness
    as_of: str = ""


@dataclass
class LinkedAccount:
    field_key: str             # "account:5"
    external_ref: str          # the provider's account id
    has_cash: bool = False
    cash_field_key: str = ""


@dataclass
class ClientData:
    """Plain snapshot handed to a provider (keeps providers decoupled from the ORM)."""
    accounts: list = field(default_factory=list)   # LinkedAccount for THIS provider
    trust_address: str = ""
    extras: dict = field(default_factory=dict)


class Provider:
    name = "base"

    def __init__(self, base_url="", secrets=None, session=None):
        self.base_url = (base_url or "").rstrip("/")
        self.secrets = secrets or {}
        self.session = session or requests.Session()

    # ---- input providers override this ----
    def collect(self, data: ClientData) -> dict:
        raise NotImplementedError

    # ---- HTTP helpers ----
    def _post(self, path, **kw):
        try:
            r = self.session.post(self.base_url + path, timeout=DEFAULT_TIMEOUT, **kw)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            raise ProviderError(f"{self.name} POST {path} failed: {e}") from e

    def _get(self, path, **kw):
        try:
            r = self.session.get(self.base_url + path, timeout=DEFAULT_TIMEOUT, **kw)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            raise ProviderError(f"{self.name} GET {path} failed: {e}") from e
