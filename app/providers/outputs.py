"""Output provider adapters (spec 8.5, 8.10): push generated reports out."""
from __future__ import annotations

import json

from .base import Provider, ProviderError, DEFAULT_TIMEOUT
import requests


class DropboxProvider(Provider):
    """Dropbox content API /files/upload — auto-save generated reports."""
    name = "dropbox"

    def upload(self, path: str, data: bytes) -> dict:
        headers = {
            "Authorization": f"Bearer {self.secrets.get('access_token', '')}",
            "Dropbox-API-Arg": json.dumps({"path": path, "mode": "overwrite", "autorename": True}),
            "Content-Type": "application/octet-stream",
        }
        try:
            r = self.session.post(self.base_url + "/2/files/upload", headers=headers,
                                  data=data, timeout=DEFAULT_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            raise ProviderError(f"dropbox upload failed: {e}") from e


class CanvaProvider(Provider):
    """Canva Connect API — upload the PDF as an asset and open an editable design."""
    name = "canva"

    def create_design(self, title: str, pdf_bytes: bytes) -> dict:
        headers = {"Authorization": f"Bearer {self.secrets.get('access_token', '')}"}
        try:
            up = self.session.post(self.base_url + "/v1/asset-uploads", headers=headers,
                                   data=pdf_bytes, timeout=DEFAULT_TIMEOUT)
            up.raise_for_status()
            asset = up.json()
            asset_id = (asset.get("asset") or {}).get("id") or asset.get("id")
            r = self.session.post(self.base_url + "/v1/designs", headers=headers,
                                  json={"title": title, "asset_id": asset_id},
                                  timeout=DEFAULT_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            raise ProviderError(f"canva export failed: {e}") from e
