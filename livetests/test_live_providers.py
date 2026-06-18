"""Live provider smoke tests — validate each adapter against its REAL API.

These are OPT-IN and skipped unless the matching AW_LIVE_* env var (and credentials) are set,
so they never run in normal CI (`pytest` only collects tests/). Run explicitly:

    pytest livetests/                 # all configured providers
    pytest livetests/ -k plaid        # one provider

See livetests/README.md for the env vars each test needs.
"""
import os

import pytest


def need(*keys):
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        pytest.skip("set " + ", ".join(missing) + " to run this live test")


def test_live_plaid():
    need("AW_LIVE_PLAID", "PLAID_BASE_URL", "PLAID_CLIENT_ID", "PLAID_SECRET",
         "PLAID_ACCESS_TOKEN", "PLAID_ACCOUNT_REF")
    from app.providers.inputs import PlaidProvider
    from app.providers.base import ClientData, LinkedAccount
    p = PlaidProvider(base_url=os.environ["PLAID_BASE_URL"], secrets={
        "client_id": os.environ["PLAID_CLIENT_ID"], "secret": os.environ["PLAID_SECRET"],
        "access_token": os.environ["PLAID_ACCESS_TOKEN"]})
    out = p.collect(ClientData(accounts=[LinkedAccount("account:test", os.environ["PLAID_ACCOUNT_REF"])]))
    assert out.get("account:test") and out["account:test"].value


def test_live_schwab():
    need("AW_LIVE_SCHWAB", "SCHWAB_BASE_URL", "SCHWAB_ACCESS_TOKEN", "SCHWAB_ACCOUNT_REF")
    from app.providers.inputs import SchwabProvider
    from app.providers.base import ClientData, LinkedAccount
    p = SchwabProvider(base_url=os.environ["SCHWAB_BASE_URL"],
                       secrets={"access_token": os.environ["SCHWAB_ACCESS_TOKEN"]})
    out = p.collect(ClientData(accounts=[LinkedAccount("account:test", os.environ["SCHWAB_ACCOUNT_REF"])]))
    assert out.get("account:test") and out["account:test"].value


def test_live_rightcapital():
    need("AW_LIVE_RIGHTCAPITAL", "RC_BASE_URL", "RC_ACCESS_TOKEN", "RC_ACCOUNT_REF")
    from app.providers.inputs import RightCapitalProvider
    from app.providers.base import ClientData, LinkedAccount
    p = RightCapitalProvider(base_url=os.environ["RC_BASE_URL"],
                             secrets={"access_token": os.environ["RC_ACCESS_TOKEN"]})
    out = p.collect(ClientData(accounts=[LinkedAccount("account:test", os.environ["RC_ACCOUNT_REF"])]))
    assert out.get("account:test") and out["account:test"].value


def test_live_zillow():
    need("AW_LIVE_ZILLOW", "ZILLOW_BASE_URL", "ZILLOW_API_KEY", "ZILLOW_ADDRESS")
    from app.providers.inputs import ZillowProvider
    from app.providers.base import ClientData
    p = ZillowProvider(base_url=os.environ["ZILLOW_BASE_URL"],
                       secrets={"api_key": os.environ["ZILLOW_API_KEY"]})
    out = p.collect(ClientData(trust_address=os.environ["ZILLOW_ADDRESS"]))
    assert out.get("trust") and out["trust"].value


def test_live_pinnacle():
    need("AW_LIVE_PINNACLE", "PINNACLE_BASE_URL", "PINNACLE_ACCESS_TOKEN", "PINNACLE_ACCOUNT_REF")
    from app.providers.inputs import PinnacleProvider
    from app.providers.base import ClientData, LinkedAccount
    p = PinnacleProvider(base_url=os.environ["PINNACLE_BASE_URL"],
                         secrets={"access_token": os.environ["PINNACLE_ACCESS_TOKEN"]})
    out = p.collect(ClientData(accounts=[LinkedAccount("account:test", os.environ["PINNACLE_ACCOUNT_REF"])]))
    assert out.get("account:test") and out["account:test"].value


def test_live_precisefp():
    need("AW_LIVE_PRECISEFP", "PRECISEFP_BASE_URL", "PRECISEFP_ACCESS_TOKEN", "PRECISEFP_CLIENT_ID")
    from app.providers.inputs import PreciseFPProvider
    p = PreciseFPProvider(base_url=os.environ["PRECISEFP_BASE_URL"],
                          secrets={"access_token": os.environ["PRECISEFP_ACCESS_TOKEN"]})
    prof = p.fetch_profile(os.environ["PRECISEFP_CLIENT_ID"])
    assert isinstance(prof, dict) and prof


def test_live_dropbox():
    need("AW_LIVE_DROPBOX", "DROPBOX_BASE_URL", "DROPBOX_ACCESS_TOKEN")
    from app.providers.outputs import DropboxProvider
    p = DropboxProvider(base_url=os.environ["DROPBOX_BASE_URL"],
                        secrets={"access_token": os.environ["DROPBOX_ACCESS_TOKEN"]})
    res = p.upload("/aw-portal-livetest/smoke.txt", b"aw-portal live smoke test")
    assert res.get("path_display") or res.get("id")


def test_live_canva():
    need("AW_LIVE_CANVA", "CANVA_BASE_URL", "CANVA_ACCESS_TOKEN")
    from app.providers.outputs import CanvaProvider
    p = CanvaProvider(base_url=os.environ["CANVA_BASE_URL"],
                      secrets={"access_token": os.environ["CANVA_ACCESS_TOKEN"]})
    res = p.create_design("AW Portal live smoke", b"%PDF-1.4 minimal")
    assert res.get("design")


def test_live_llm():
    need("AW_LIVE_LLM", "ANTHROPIC_API_KEY")
    from app.agents.llm import LLMClient
    c = LLMClient(api_key=os.environ["ANTHROPIC_API_KEY"],
                  base_url=os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
                  model=os.environ.get("LLM_MODEL", "claude-opus-4-8"))
    out = c.extract_json("Return only a JSON object.", 'Respond with {"ok": 1}')
    assert isinstance(out, dict)
