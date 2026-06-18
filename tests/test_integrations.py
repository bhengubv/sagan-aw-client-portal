"""fetch_for_client end-to-end: many providers -> merged field values (spec 8.7, 11)."""
from app.extensions import db
from app.models import Client, ProviderCredential
from app.vault import get_vault
from app import integrations


def _configure(app, seeded):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        ira, roth, brok = c.accounts[0], c.accounts[1], c.accounts[2]
        ira.provider, ira.external_ref = "rightcapital", "rc-ira"
        roth.provider, roth.external_ref, roth.has_cash_balance = "plaid", "plaid-roth", True
        brok.provider, brok.external_ref, brok.has_cash_balance = "plaid", "plaid-brokerage", True
        c.trust.property_address = "123 Sample St, Austin TX"
        v = get_vault()

        def cred(provider, secrets):
            return ProviderCredential(tenant_id=seeded["tenant_id"], provider=provider,
                                      status="active", base_url=f"http://sandbox/{provider}",
                                      encrypted_token=v.encrypt_dict(secrets))
        db.session.add_all([
            cred("plaid", {"client_id": "c", "secret": "s", "access_token": "t"}),
            cred("rightcapital", {"access_token": "t"}),
            cred("zillow", {"api_key": "k"}),
            cred("pinnacle", {"access_token": "t", "private_reserve_ref": "pinnacle-reserve"}),
            cred("schwab", {"access_token": "t", "investment_account_ref": "schwab-brokerage"}),
        ])
        db.session.commit()
        return {"ira": ira.id, "roth": roth.id, "brok": brok.id}


def test_fetch_for_client_pulls_from_all_providers(app, seeded, route_through_sandbox):
    ids = _configure(app, seeded)
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        values, report = integrations.fetch_for_client(c)

    assert values[f"account:{ids['roth']}"].value == "15000"
    assert values[f"account_cash:{ids['roth']}"].value == "316"
    assert values[f"account:{ids['brok']}"].value == "50000"
    assert values[f"account_cash:{ids['brok']}"].value == "1200"
    assert values[f"account:{ids['ira']}"].value == "11000"
    assert values["trust"].value == "450000"
    assert values["private_reserve_balance"].value == "75000"
    assert values["investment_account_balance"].value == "15000"
    assert report["errors"] == []
    assert report["fetched"] >= 8
    # sources are recorded for provenance
    assert report["sources"][f"account:{ids['ira']}"] == "rightcapital"


def test_inactive_providers_are_ignored(app, seeded, route_through_sandbox):
    with app.app_context():
        v = get_vault()
        db.session.add(ProviderCredential(tenant_id=seeded["tenant_id"], provider="plaid",
                       status="inactive", base_url="http://sandbox/plaid",
                       encrypted_token=v.encrypt_dict({"access_token": "t"})))
        db.session.commit()
        c = db.session.get(Client, seeded["client_id"])
        values, report = integrations.fetch_for_client(c)
    assert report["fetched"] == 0  # nothing active


def test_unreachable_provider_is_reported_not_raised(app, seeded):
    with app.app_context():
        v = get_vault()
        db.session.add(ProviderCredential(tenant_id=seeded["tenant_id"], provider="zillow",
                       status="active", base_url="http://127.0.0.1:9/zillow",
                       encrypted_token=v.encrypt_dict({"api_key": "k"})))
        db.session.commit()
        c = db.session.get(Client, seeded["client_id"])
        c.trust.property_address = "123 Sample St, Austin TX"
        values, report = integrations.fetch_for_client(c)
    assert values == {}
    assert len(report["errors"]) == 1
