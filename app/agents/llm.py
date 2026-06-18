"""LLM client (spec 12). Real Anthropic Messages API contract; reports availability so
callers fall back to the deterministic path when no key is configured. No data is sent
to any model unless a key is explicitly set (spec 12.2)."""
from __future__ import annotations

import json
import re

import requests


class LLMUnavailable(Exception):
    pass


def _first_json(text: str) -> str:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("no JSON object in model output")
    return m.group(0)


class LLMClient:
    def __init__(self, api_key=None, base_url="https://api.anthropic.com",
                 model="claude-opus-4-8", session=None):
        self.api_key = api_key
        self.base_url = (base_url or "").rstrip("/")
        self.model = model
        self.session = session or requests.Session()

    @classmethod
    def from_config(cls, config, session=None):
        return cls(api_key=config.get("ANTHROPIC_API_KEY"),
                   base_url=config.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
                   model=config.get("LLM_MODEL", "claude-opus-4-8"), session=session)

    def available(self) -> bool:
        return bool(self.api_key)

    def extract_json(self, system: str, user: str, max_tokens: int = 1024) -> dict:
        if not self.available():
            raise LLMUnavailable("no ANTHROPIC_API_KEY configured")
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}
        body = {"model": self.model, "max_tokens": max_tokens, "system": system,
                "messages": [{"role": "user", "content": user}]}
        r = self.session.post(self.base_url + "/v1/messages", headers=headers,
                              json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        text = "".join(b.get("text", "") for b in data.get("content", [])
                       if b.get("type") == "text")
        return json.loads(_first_json(text))
