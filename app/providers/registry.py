"""Provider registry: build configured adapters from stored credentials."""
from __future__ import annotations

from .inputs import (PlaidProvider, SchwabProvider, RightCapitalProvider,
                     ZillowProvider, PinnacleProvider, PreciseFPProvider)
from .outputs import DropboxProvider, CanvaProvider

INPUT_PROVIDERS = {c.name: c for c in [PlaidProvider, SchwabProvider, RightCapitalProvider,
                                       ZillowProvider, PinnacleProvider, PreciseFPProvider]}
OUTPUT_PROVIDERS = {c.name: c for c in [DropboxProvider, CanvaProvider]}
ALL_PROVIDERS = {**INPUT_PROVIDERS, **OUTPUT_PROVIDERS}


def build_provider(cred, vault):
    """Instantiate a provider from a ProviderCredential row, decrypting its secrets."""
    cls = ALL_PROVIDERS.get(cred.provider)
    if not cls:
        return None
    secrets = vault.decrypt_dict(cred.encrypted_token) if cred.encrypted_token else {}
    return cls(base_url=cred.base_url or "", secrets=secrets)
