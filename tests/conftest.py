import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import (Tenant, User, Client, Person, Account, Liability,
                        Trust, StaticFinancials)


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded(app):
    """A tenant, three users (one per role), and a fully-populated demo client."""
    with app.app_context():
        t = Tenant(name="Test Firm")
        db.session.add(t)
        db.session.flush()
        users = {
            "owner": User(tenant_id=t.id, name="Owner", email="owner@t.test", role="owner",
                          password_hash=generate_password_hash("pw12345")),
            "planner": User(tenant_id=t.id, name="Planner", email="planner@t.test", role="planner",
                            password_hash=generate_password_hash("pw12345")),
            "assistant": User(tenant_id=t.id, name="Asst", email="asst@t.test", role="assistant",
                              password_hash=generate_password_hash("pw12345")),
        }
        db.session.add_all(users.values())

        c = Client(tenant_id=t.id, display_name="Demo Household")
        db.session.add(c)
        db.session.flush()
        db.session.add(Person(client_id=c.id, role="C1", name="Pat Demo", ssn_last4="1234"))
        db.session.add_all([
            Account(client_id=c.id, owner="C1", category="retirement", type="IRA", acct_last4="1111"),
            Account(client_id=c.id, owner="C1", category="retirement", type="Roth IRA", acct_last4="2222"),
            Account(client_id=c.id, owner="JOINT", category="non_retirement", type="Brokerage",
                    acct_last4="4444", has_cash_balance=True),
        ])
        db.session.add(Trust(client_id=c.id, property_address="1 Demo Rd"))
        db.session.add(Liability(client_id=c.id, type="Mortgage", interest_rate="4.5"))
        db.session.add(StaticFinancials(client_id=c.id, monthly_salary_inflow="15000",
                       monthly_expense_budget_outflow="12000", normal_monthly_expenses="10000",
                       insurance_deductibles=["1000", "2000", "1000"]))
        db.session.commit()
        return {"tenant_id": t.id, "client_id": c.id,
                "accounts": [a.id for a in c.accounts],
                "liabilities": [li.id for li in c.liabilities]}


def login(client, email="owner@t.test", password="pw12345"):
    return client.post("/auth/login", data={"email": email, "password": password},
                       follow_redirects=True)


@pytest.fixture
def auth_client(client, seeded):
    login(client)
    return client


# --------------------------------------------------------------------------- #
# Provider sandbox plumbing: drive the real adapters through the real sandbox   #
# contract in-process (no sockets). This tests the FULL chain, not hand-written #
# JSON — the adapter parsing AND the sandbox's contract logic together.         #
# --------------------------------------------------------------------------- #
from sandbox import create_sandbox_app  # noqa: E402


class _SandboxResp:
    def __init__(self, werkzeug_resp):
        self._r = werkzeug_resp
        self.status_code = werkzeug_resp.status_code

    def json(self):
        return self._r.get_json()

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"sandbox HTTP {self.status_code}")


class SandboxSession:
    """Quacks like requests.Session but routes to the sandbox app's test client."""
    def __init__(self, client):
        self.client = client

    @staticmethod
    def _path(url):
        from urllib.parse import urlsplit
        return urlsplit(url).path

    def get(self, url, headers=None, params=None, timeout=None):
        return _SandboxResp(self.client.get(self._path(url), headers=headers or {},
                                            query_string=params))

    def post(self, url, headers=None, json=None, data=None, params=None, timeout=None):
        return _SandboxResp(self.client.post(self._path(url), headers=headers or {},
                                             json=json, data=data, query_string=params))


@pytest.fixture
def sandbox_client():
    return create_sandbox_app().test_client()


@pytest.fixture
def sandbox_session(sandbox_client):
    return SandboxSession(sandbox_client)


@pytest.fixture
def route_through_sandbox(sandbox_client, monkeypatch):
    """Make every Provider built anywhere use the sandbox transport."""
    monkeypatch.setattr("app.providers.base.requests.Session",
                        lambda: SandboxSession(sandbox_client))
    return sandbox_client
