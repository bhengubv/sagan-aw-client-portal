"""AI agents (spec 12): anomaly flagging, deterministic + LLM extraction."""
import io

import pytest

from app.agents import anomaly, extraction
from app.agents.llm import LLMClient, LLMUnavailable


# ---- anomaly ----
def test_anomaly_flags_big_moves_only():
    prev = {"account:1": "100000", "trust": "450000", "account:2": "50000"}
    curr = {"account:1": "100500", "trust": "700000", "account:2": "50000"}  # trust +55%
    flags = anomaly.detect(prev, curr, labels={"trust": "Home value"})
    keys = [f["key"] for f in flags]
    assert keys == ["trust"]
    assert flags[0]["label"] == "Home value"
    assert "up" in flags[0]["reason"]


def test_anomaly_zero_to_nonzero():
    flags = anomaly.detect({"x": "0"}, {"x": "500"})
    assert flags[0]["reason"] == "was zero, now non-zero"


def test_anomaly_ignores_unknown_and_small_changes():
    assert anomaly.detect({"a": "100"}, {"a": "101"}) == []   # 1% < 50%
    assert anomaly.detect({}, {"a": "100"}) == []             # no prior


# ---- deterministic extraction ----
def test_extraction_from_text():
    text = (
        "Account ****1111  IRA            Balance: $11,000.00\n"
        "Roth IRA ****2222                Balance: $15,000.00\n"
        "Brokerage                        $50,000.00\n"
    )
    accounts = [
        {"field_key": "account:1", "label": "IRA", "last4": "1111", "type": "IRA"},
        {"field_key": "account:2", "label": "Roth IRA", "last4": "2222", "type": "Roth IRA"},
        {"field_key": "account:3", "label": "Brokerage", "last4": None, "type": "Brokerage"},
    ]
    by = {p["field_key"]: p["value"] for p in extraction.propose_balances(text, accounts)}
    assert by["account:1"] == "11000.00"
    assert by["account:2"] == "15000.00"
    assert by["account:3"] == "50000.00"


def test_extraction_reads_real_pdf_bytes():
    from reportlab.pdfgen import canvas as rc
    buf = io.BytesIO()
    c = rc.Canvas(buf)
    c.drawString(72, 720, "Account ****9999   Balance: $12,345.00")
    c.showPage()
    c.save()
    text = extraction.extract_text(buf.getvalue(), "stmt.pdf")
    assert "9999" in text
    props = extraction.propose_balances(text, [{"field_key": "account:9", "label": "X", "last4": "9999"}])
    assert props[0]["value"] == "12345.00"


def test_propose_uses_deterministic_without_key(app):
    with app.app_context():
        props, method = extraction.propose(
            "IRA ****1111 $11,000.00",
            [{"field_key": "account:1", "label": "IRA", "last4": "1111"}])
    assert method == "deterministic"
    assert props[0]["value"] == "11000.00"


# ---- LLM client (real contract, mocked transport) ----
class _Resp:
    status_code = 200

    def __init__(self, payload):
        self._p = payload

    def json(self):
        return self._p

    def raise_for_status(self):
        pass


class _FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.last = None

    def post(self, url, headers=None, json=None, timeout=None):
        self.last = {"url": url, "headers": headers, "json": json}
        return _Resp(self.payload)


def test_llm_extract_json_real_request_shape():
    payload = {"content": [{"type": "text",
                            "text": 'Result: {"account:1": 11000, "trust": 450000}'}]}
    sess = _FakeSession(payload)
    client = LLMClient(api_key="sk-test", model="claude-opus-4-8", session=sess)
    out = client.extract_json("system", "user")
    assert out == {"account:1": 11000, "trust": 450000}
    assert sess.last["url"].endswith("/v1/messages")
    assert sess.last["headers"]["x-api-key"] == "sk-test"
    assert sess.last["headers"]["anthropic-version"] == "2023-06-01"
    assert sess.last["json"]["model"] == "claude-opus-4-8"


def test_llm_unavailable_without_key():
    with pytest.raises(LLMUnavailable):
        LLMClient(api_key=None).extract_json("s", "u")


def test_propose_uses_llm_when_key_present(app):
    payload = {"content": [{"type": "text", "text": '{"account:1": 11000}'}]}
    sess = _FakeSession(payload)
    with app.app_context():
        app.config["ANTHROPIC_API_KEY"] = "sk-test"
        props, method = extraction.propose(
            "garbled text with no parseable balances",
            [{"field_key": "account:1", "label": "IRA", "last4": "1111"}], session=sess)
    assert method == "llm"
    assert props[0]["value"] == "11000"
