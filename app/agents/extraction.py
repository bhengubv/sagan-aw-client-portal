"""Statement extraction agent (spec 8.8, 12).

Reads an uploaded statement (PDF or text) and PROPOSES balances for human confirmation —
it never auto-commits to a report. The deterministic extractor genuinely parses the text
(account number / type near a money amount); an LLM is used only if a key is configured.
"""
from __future__ import annotations

import re

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover
    fitz = None

from flask import current_app

from .llm import LLMClient

MONEY_RE = re.compile(r"\$?\s*([0-9](?:[0-9,]*)(?:\.[0-9]{2})?)")


def extract_text(data: bytes, filename="") -> str:
    """Plain text from a PDF or text upload."""
    if data[:4] == b"%PDF" and fitz is not None:
        doc = fitz.open(stream=data, filetype="pdf")
        return "\n".join(p.get_text() for p in doc)
    return data.decode("utf-8", errors="ignore")


def _amount(s: str) -> str:
    return s.replace(",", "")


def propose_balances(text: str, accounts: list) -> list:
    """Deterministic proposals.

    accounts: [{field_key, label, last4, type}]
    returns:  [{field_key, label, value, confidence, evidence}]
    """
    proposals = []
    lines = [ln for ln in text.splitlines() if ln.strip()]
    for acc in accounts:
        best = None
        for ln in lines:
            conf = 0.0
            if acc.get("last4") and str(acc["last4"]) in ln:
                conf = 0.9
            elif acc.get("type") and str(acc["type"]).lower() in ln.lower():
                conf = 0.6
            if conf:
                m = MONEY_RE.findall(ln)
                if m:
                    cand = {"field_key": acc["field_key"], "label": acc.get("label", acc["field_key"]),
                            "value": _amount(m[-1]), "confidence": conf, "evidence": ln.strip()[:120]}
                    if best is None or conf > best["confidence"]:
                        best = cand
                    if conf >= 0.9:
                        break
        if best:
            proposals.append(best)
    return proposals


def propose(text: str, accounts: list, session=None):
    """Return (proposals, method). Uses the LLM when available, else deterministic."""
    client = LLMClient.from_config(current_app.config, session=session)
    if client.available():
        try:
            system = ("You extract account balances from a financial statement. "
                      "Return ONLY a JSON object mapping field_key to a numeric balance.")
            spec = "\n".join(f"{a['field_key']}: {a.get('label')} (last4 {a.get('last4')})"
                             for a in accounts)
            user = f"Accounts:\n{spec}\n\nStatement:\n{text[:6000]}"
            data = client.extract_json(system, user)
            out = [{"field_key": k, "label": k, "value": str(v), "confidence": 0.95,
                    "evidence": "extracted by LLM"} for k, v in data.items()]
            if out:
                return out, "llm"
        except Exception:  # noqa: BLE001  (any LLM issue -> deterministic fallback)
            pass
    return propose_balances(text, accounts), "deterministic"
