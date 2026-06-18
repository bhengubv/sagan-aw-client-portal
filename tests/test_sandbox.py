"""The provider sandbox implements each provider's contract (spec 11)."""


def test_health(sandbox_client):
    assert sandbox_client.get("/healthz").get_json()["status"] == "ok"


def test_plaid_contract(sandbox_client):
    r = sandbox_client.post("/plaid/accounts/balance/get", json={"access_token": "t"})
    accts = r.get_json()["accounts"]
    assert any(a["account_id"] == "plaid-roth" for a in accts)
    assert accts[0]["balances"]["current"] is not None


def test_schwab_contract(sandbox_client):
    r = sandbox_client.get("/schwab/trader/v1/accounts")
    accts = r.get_json()["accounts"]
    assert accts[0]["securitiesAccount"]["currentBalances"]["liquidationValue"] is not None


def test_rightcapital_contract(sandbox_client):
    assert sandbox_client.post("/rightcapital/v1/sync").status_code == 200
    accts = sandbox_client.get("/rightcapital/v1/accounts").get_json()["accounts"]
    assert accts[0]["id"] == "rc-ira"


def test_zillow_contract(sandbox_client):
    r = sandbox_client.get("/zillow/zestimate", query_string={"address": "123 Sample St, Austin TX"})
    assert r.get_json()["zestimate"] == 450000


def test_pinnacle_contract(sandbox_client):
    r = sandbox_client.get("/pinnacle/v1/accounts/balances")
    assert r.get_json()["balances"][0]["account_ref"] == "pinnacle-reserve"


def test_precisefp_contract(sandbox_client):
    r = sandbox_client.get("/precisefp/v1/clients/sample-1")
    assert r.get_json()["ssn_last4"] == "1234"
    assert sandbox_client.get("/precisefp/v1/clients/nope").status_code == 404


def test_dropbox_and_canva_contract(sandbox_client):
    import json
    up = sandbox_client.post("/dropbox/2/files/upload", data=b"PDFDATA",
                             headers={"Dropbox-API-Arg": json.dumps({"path": "/r.pdf"})})
    assert up.get_json()["path_display"] == "/r.pdf"
    a = sandbox_client.post("/canva/v1/asset-uploads", data=b"PDF")
    assert a.get_json()["asset"]["id"]
    d = sandbox_client.post("/canva/v1/designs", json={"title": "T", "asset_id": "x"})
    assert "edit_url" in d.get_json()["design"]["urls"]
