"""Local provider sandbox (spec: 'sandbox in dev, live in prod').

A real, runnable WSGI app implementing each provider's API contract with deterministic
fixture data — the same pattern Plaid/Stripe ship. The portal's adapters make real HTTP
calls here in dev; in production their base_url points at the live provider. Run it with
`python sandbox.py` (port 5050), or drive it directly in tests via its test client.
"""
from __future__ import annotations

from flask import Flask, jsonify, request

# --- Fixtures (match the demo client's linked external_refs) ---
PLAID_ACCOUNTS = [
    {"account_id": "plaid-roth", "balances": {"current": 15000, "available": 316}},
    {"account_id": "plaid-brokerage", "balances": {"current": 50000, "available": 1200}},
]
SCHWAB_ACCOUNTS = [
    {"securitiesAccount": {"accountNumber": "schwab-401k",
                           "currentBalances": {"liquidationValue": 9000, "cashBalance": 0}}},
    {"securitiesAccount": {"accountNumber": "schwab-brokerage",
                           "currentBalances": {"liquidationValue": 15000, "cashBalance": 500}}},
]
RC_ACCOUNTS = [{"id": "rc-ira", "balance": 11000, "is_stale": False, "as_of": "2026-06-01"}]
PINNACLE_BALANCES = [{"account_ref": "pinnacle-reserve", "balance": 75000}]
ZESTIMATES = {"123 Sample St, Austin TX": 450000}
PRECISEFP = {
    "sample-1": {"first_name": "Jordan", "last_name": "Sample", "dob": "1975-04-01",
                 "ssn_last4": "1234",
                 "spouse": {"first_name": "Riley", "last_name": "Sample",
                            "dob": "1977-09-12", "ssn_last4": "5678"}},
}


def create_sandbox_app():
    app = Flask(__name__)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok", "service": "provider-sandbox"}

    # ---- Plaid ----
    @app.post("/plaid/accounts/balance/get")
    def plaid_balance():
        _ = request.get_json(silent=True) or {}
        return jsonify({"accounts": PLAID_ACCOUNTS})

    # ---- Schwab ----
    @app.get("/schwab/trader/v1/accounts")
    def schwab_accounts():
        return jsonify({"accounts": SCHWAB_ACCOUNTS})

    # ---- RightCapital ----
    @app.post("/rightcapital/v1/sync")
    def rc_sync():
        return jsonify({"status": "synced"})

    @app.get("/rightcapital/v1/accounts")
    def rc_accounts():
        return jsonify({"accounts": RC_ACCOUNTS})

    # ---- Zillow ----
    @app.get("/zillow/zestimate")
    def zillow():
        addr = request.args.get("address", "")
        return jsonify({"zestimate": ZESTIMATES.get(addr), "as_of": "2026-06-15"})

    # ---- Pinnacle ----
    @app.get("/pinnacle/v1/accounts/balances")
    def pinnacle():
        return jsonify({"balances": PINNACLE_BALANCES})

    # ---- PreciseFP ----
    @app.get("/precisefp/v1/clients/<cid>")
    def precisefp(cid):
        data = PRECISEFP.get(cid)
        if not data:
            return jsonify({"error": "not found"}), 404
        return jsonify(data)

    # ---- Dropbox ----
    @app.post("/dropbox/2/files/upload")
    def dropbox_upload():
        import json as _json
        arg = _json.loads(request.headers.get("Dropbox-API-Arg", "{}"))
        return jsonify({"id": "id:sandbox", "path_display": arg.get("path", "/"),
                        "size": request.content_length or 0})

    # ---- Canva ----
    @app.post("/canva/v1/asset-uploads")
    def canva_asset():
        return jsonify({"asset": {"id": "asset-sandbox-1"}})

    @app.post("/canva/v1/designs")
    def canva_design():
        body = request.get_json(silent=True) or {}
        return jsonify({"design": {"id": "design-sandbox-1", "title": body.get("title"),
                                   "urls": {"edit_url": "https://canva.example/design/design-sandbox-1/edit"}}})

    return app
