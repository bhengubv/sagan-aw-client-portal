"""Each input/output adapter, driven end-to-end through the real sandbox (spec 11)."""
import requests
import pytest

from app.providers.inputs import (PlaidProvider, SchwabProvider, RightCapitalProvider,
                                   ZillowProvider, PinnacleProvider, PreciseFPProvider)
from app.providers.outputs import DropboxProvider, CanvaProvider
from app.providers.base import ClientData, LinkedAccount, ProviderError


def test_plaid_adapter(sandbox_session):
    p = PlaidProvider(base_url="http://sb/plaid", secrets={"access_token": "t"}, session=sandbox_session)
    out = p.collect(ClientData(accounts=[
        LinkedAccount("account:9", "plaid-roth", has_cash=True, cash_field_key="account_cash:9")]))
    assert out["account:9"].value == "15000"
    assert out["account:9"].source == "plaid"
    assert out["account_cash:9"].value == "316"


def test_schwab_adapter_maps_account_and_investment(sandbox_session):
    p = SchwabProvider(base_url="http://sb/schwab",
                       secrets={"access_token": "t", "investment_account_ref": "schwab-brokerage"},
                       session=sandbox_session)
    out = p.collect(ClientData(accounts=[LinkedAccount("account:5", "schwab-401k")]))
    assert out["account:5"].value == "9000"
    assert out["investment_account_balance"].value == "15000"


def test_rightcapital_adapter(sandbox_session):
    p = RightCapitalProvider(base_url="http://sb/rightcapital", secrets={"access_token": "t"},
                             session=sandbox_session)
    out = p.collect(ClientData(accounts=[LinkedAccount("account:1", "rc-ira")]))
    assert out["account:1"].value == "11000"
    assert out["account:1"].is_fresh is True


def test_zillow_adapter(sandbox_session):
    p = ZillowProvider(base_url="http://sb/zillow", secrets={"api_key": "k"}, session=sandbox_session)
    out = p.collect(ClientData(trust_address="123 Sample St, Austin TX"))
    assert out["trust"].value == "450000"


def test_zillow_adapter_no_address_returns_empty(sandbox_session):
    p = ZillowProvider(base_url="http://sb/zillow", session=sandbox_session)
    assert p.collect(ClientData()) == {}


def test_pinnacle_adapter(sandbox_session):
    p = PinnacleProvider(base_url="http://sb/pinnacle",
                         secrets={"access_token": "t", "private_reserve_ref": "pinnacle-reserve"},
                         session=sandbox_session)
    out = p.collect(ClientData())
    assert out["private_reserve_balance"].value == "75000"


def test_precisefp_profile_import(sandbox_session):
    p = PreciseFPProvider(base_url="http://sb/precisefp", secrets={"access_token": "t"},
                          session=sandbox_session)
    prof = p.fetch_profile("sample-1")
    assert prof["ssn_last4"] == "1234"
    assert prof["spouse"]["ssn_last4"] == "5678"


def test_dropbox_upload(sandbox_session):
    p = DropboxProvider(base_url="http://sb/dropbox", secrets={"access_token": "t"}, session=sandbox_session)
    res = p.upload("/reports/r.pdf", b"PDFBYTES")
    assert res["path_display"] == "/reports/r.pdf"


def test_canva_export(sandbox_session):
    p = CanvaProvider(base_url="http://sb/canva", secrets={"access_token": "t"}, session=sandbox_session)
    res = p.create_design("Quarterly Report", b"PDF")
    assert "edit_url" in res["design"]["urls"]


def test_provider_degrades_on_unreachable_host():
    # A real connection to a closed port -> ProviderError (graceful fallback to manual).
    p = ZillowProvider(base_url="http://127.0.0.1:9", secrets={}, session=requests.Session())
    with pytest.raises(ProviderError):
        p.collect(ClientData(trust_address="x"))
