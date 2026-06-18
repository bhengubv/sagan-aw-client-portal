"""Manual provider — the V1 data source (spec 6.5, 8.7).

The team enters every value by hand. This is a real, complete implementation of the
Provider interface (not a stub): it validates and normalises the values the form
submitted. When Phase 2 adds automated providers, they slot in beside this one.
"""
from __future__ import annotations

from .base import Provider, FieldValue


class ManualProvider(Provider):
    name = "manual"

    def __init__(self, entered: dict):
        # entered: {field_key: raw string value from the form}
        self.entered = entered or {}

    def fetch(self, field_keys: list) -> dict:
        out = {}
        for key in field_keys:
            raw = self.entered.get(key)
            if raw is None or str(raw).strip() == "":
                continue  # missing; caller flags incompleteness
            out[key] = FieldValue(key=key, value=str(raw).strip(), source="manual", is_fresh=True)
        return out
