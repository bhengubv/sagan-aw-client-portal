"""Seed demo data so every feature is usable immediately.

Run:  python seed.py
Then (for live provider fetch):  python run_sandbox.py   (separate terminal)

Logins (all password 'changeme123'):
  owner@firm.test (owner) · planner@firm.test · assistant@firm.test
  superadmin@firm.test (platform admin)
  northwind@firm.test (a second firm, for the admin view)
"""
from datetime import date

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import (Tenant, User, Client, Person, Account, Liability,
                        Trust, StaticFinancials, ProviderCredential)
from app.vault import get_vault

import os

# Where the provider sandbox lives. Locally it's a separate server on :5050.
# On a DEMO_MODE deploy the sandbox is mounted into the app itself, so we call it
# on the app's own port at /provider-sandbox.
if os.environ.get("DEMO_MODE") == "1" and os.environ.get("PORT"):
    SANDBOX = f"http://127.0.0.1:{os.environ['PORT']}/provider-sandbox"
else:
    SANDBOX = os.environ.get("SANDBOX_BASE_URL", "http://127.0.0.1:5050")

PW = generate_password_hash("changeme123")


def _provider(tenant_id, name, secrets):
    return ProviderCredential(tenant_id=tenant_id, provider=name, status="active",
                              base_url=f"{SANDBOX}/{name}",
                              encrypted_token=get_vault().encrypt_dict(secrets))


def run():
    app = create_app()
    with app.app_context():
        if User.query.filter_by(email="owner@firm.test").first():
            print("seed: already present")
            return

        # ---- Firm 1: the demo firm, fully wired ----
        t = Tenant(name="Demo Advisory Firm", brand_color="#2E5E8C")
        db.session.add(t)
        db.session.flush()
        db.session.add_all([
            User(tenant_id=t.id, name="Andrew (Owner)", email="owner@firm.test", role="owner", password_hash=PW),
            User(tenant_id=t.id, name="Rebecca (Planner)", email="planner@firm.test", role="planner", password_hash=PW),
            User(tenant_id=t.id, name="Maryann (Assistant)", email="assistant@firm.test", role="assistant", password_hash=PW),
            User(tenant_id=t.id, name="Platform Admin", email="superadmin@firm.test", role="superadmin", password_hash=PW),
        ])

        c = Client(tenant_id=t.id, display_name="The Sample Household")
        db.session.add(c)
        db.session.flush()
        db.session.add_all([
            Person(client_id=c.id, role="C1", name="Jordan Sample", dob=date(1975, 4, 1), ssn_last4="1234"),
            Person(client_id=c.id, role="C2", name="Riley Sample", dob=date(1977, 9, 12), ssn_last4="5678"),
        ])
        # Accounts linked to providers (external_ref matches the sandbox fixtures).
        db.session.add_all([
            Account(client_id=c.id, owner="C1", category="retirement", type="IRA",
                    acct_last4="1111", provider="rightcapital", external_ref="rc-ira"),
            Account(client_id=c.id, owner="C1", category="retirement", type="Roth IRA",
                    acct_last4="2222", has_cash_balance=True, provider="plaid", external_ref="plaid-roth"),
            Account(client_id=c.id, owner="C2", category="retirement", type="401k",
                    acct_last4="3333", provider="schwab", external_ref="schwab-401k"),
            Account(client_id=c.id, owner="JOINT", category="non_retirement", type="Brokerage",
                    acct_last4="4444", has_cash_balance=True, provider="plaid", external_ref="plaid-brokerage"),
        ])
        db.session.add(Trust(client_id=c.id, property_address="123 Sample St, Austin TX"))
        db.session.add(Liability(client_id=c.id, type="Mortgage", interest_rate="4.5"))
        db.session.add(StaticFinancials(client_id=c.id, monthly_salary_inflow="15000",
                       monthly_expense_budget_outflow="12000", normal_monthly_expenses="10000",
                       insurance_deductibles=["1000", "2000", "1000"]))

        # Connected providers (point at the local sandbox; swap base_url for live in prod).
        db.session.add_all([
            _provider(t.id, "plaid", {"client_id": "demo", "secret": "demo", "access_token": "demo-token"}),
            _provider(t.id, "schwab", {"access_token": "demo-token", "investment_account_ref": "schwab-brokerage"}),
            _provider(t.id, "rightcapital", {"access_token": "demo-token"}),
            _provider(t.id, "zillow", {"api_key": "demo-key"}),
            _provider(t.id, "pinnacle", {"access_token": "demo-token", "private_reserve_ref": "pinnacle-reserve"}),
            _provider(t.id, "dropbox", {"access_token": "demo-token"}),
            _provider(t.id, "canva", {"access_token": "demo-token"}),
        ])

        # ---- Firm 2: a second tenant, so the admin console has more than one ----
        t2 = Tenant(name="Northwind Wealth Advisors", brand_color="#2c3e50")
        db.session.add(t2)
        db.session.flush()
        db.session.add(User(tenant_id=t2.id, name="Nadia (Owner)", email="northwind@firm.test",
                            role="owner", password_hash=PW))
        c2 = Client(tenant_id=t2.id, display_name="The Northwind Client")
        db.session.add(c2)
        db.session.flush()
        db.session.add(Person(client_id=c2.id, role="C1", name="Alex North", dob=date(1980, 2, 2), ssn_last4="9999"))
        db.session.add(StaticFinancials(client_id=c2.id, monthly_salary_inflow="20000",
                       monthly_expense_budget_outflow="14000", normal_monthly_expenses="12000",
                       insurance_deductibles=["1500"]))

        db.session.commit()
        print("seed: created 2 firms, 4 logins on Demo Advisory Firm, 7 connected providers, "
              "and a fully-linked demo client. Run 'python run_sandbox.py' for live fetch.")


if __name__ == "__main__":
    run()
