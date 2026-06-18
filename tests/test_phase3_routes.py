"""Phase 3 HTTP wiring: public pages, staff, settings, extraction, distribution, anomaly."""
import io

from app.extensions import db
from app.models import (Client, ReportRun, OnboardingInvite, ExpenseSubmission,
                        Outbox, ProviderCredential, StaticFinancials)
from app.vault import get_vault
from app import reporting
from app.agents import onboarding
from tests.conftest import login


def _run(app, seeded, trust="450000"):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        entered = {"private_reserve_balance": "75000", "investment_account_balance": "15000",
                   "trust": trust, f"liability:{c.liabilities[0].id}": "200000"}
        for i, a in enumerate(c.accounts):
            entered[f"account:{a.id}"] = ["11000", "15000", "50000"][i]
            if a.has_cash_balance:
                entered[f"account_cash:{a.id}"] = "0"
        result, _ = reporting.build(c, entered)
        run = ReportRun(client_id=c.id, period="2026 Q2", entered_values=entered,
                        computed_values=reporting.serialize(result))
        db.session.add(run)
        db.session.commit()
        return run.id


# ---- public (no login) ----
def test_public_onboarding_roundtrip(client, app, seeded):
    with app.app_context():
        inv = onboarding.create_invite(seeded["tenant_id"], "c@x.com")
        token = inv.token
    assert client.get(f"/welcome/{token}").status_code == 200
    r = client.post(f"/welcome/{token}", data={"c1_name": "Jordan", "c1_ssn4": "1234"},
                    follow_redirects=True)
    assert b"Received" in r.data
    with app.app_context():
        inv = OnboardingInvite.query.filter_by(token=token).first()
        assert inv.status == "completed" and inv.data["c1_name"] == "Jordan"


def test_public_worksheet_roundtrip(client, app, seeded):
    with app.app_context():
        sub = onboarding.create_expense_invite(seeded["tenant_id"], seeded["client_id"], "c@x.com")
        token = sub.token
    assert client.get(f"/worksheet/{token}").status_code == 200
    r = client.post(f"/worksheet/{token}", data={"salary": "16000", "expense_budget": "12000",
                                                 "expenses": "10000", "deductibles": "1000,2000"},
                    follow_redirects=True)
    assert b"Received" in r.data
    with app.app_context():
        sub = ExpenseSubmission.query.filter_by(token=token).first()
        assert sub.status == "submitted" and sub.data["salary"] == "16000"


def test_public_bad_token_404(client):
    assert client.get("/welcome/nope").status_code == 404


# ---- settings / providers ----
def test_connect_and_toggle_provider(auth_client, app, seeded):
    r = auth_client.post("/settings/providers/connect",
                         data={"provider": "plaid", "base_url": "http://127.0.0.1:5050/plaid",
                               "secrets": "access_token=t\nclient_id=c"}, follow_redirects=True)
    assert b"Connected plaid" in r.data
    with app.app_context():
        cred = ProviderCredential.query.filter_by(tenant_id=seeded["tenant_id"], provider="plaid").first()
        assert cred.status == "active"
        # secrets are encrypted at rest, not stored in clear
        assert "access_token" not in (cred.encrypted_token or "")
        assert get_vault().decrypt_dict(cred.encrypted_token)["access_token"] == "t"
        pid = cred.id
    auth_client.post(f"/settings/providers/{pid}/toggle")
    with app.app_context():
        assert db.session.get(ProviderCredential, pid).status == "inactive"


# ---- client engagement invites ----
def test_client_onboard_invite_creates_outbox(auth_client, app, seeded):
    auth_client.post(f"/clients/{seeded['client_id']}/onboard",
                     data={"email": "client@x.com"}, follow_redirects=True)
    with app.app_context():
        assert Outbox.query.filter(Outbox.subject.like("Welcome%")).count() == 1


# ---- staff inbox + approval ----
def test_staff_inbox_and_approve(auth_client, app, seeded):
    with app.app_context():
        sub = onboarding.create_expense_invite(seeded["tenant_id"], seeded["client_id"], "c@x.com")
        onboarding.submit_expense(sub.token, {"salary": "17000", "expense_budget": "12000",
                                              "expenses": "10000", "deductibles": []})
        sid = sub.id
    assert auth_client.get("/staff/inbox").status_code == 200
    auth_client.post(f"/staff/expense/{sid}/approve", follow_redirects=True)
    with app.app_context():
        s = StaticFinancials.query.filter_by(client_id=seeded["client_id"]).first()
        assert s.monthly_salary_inflow == "17000"


# ---- extraction upload ----
def test_extract_prefills_form(auth_client, app, seeded):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        # statement references the seeded account last-4s (1111, 2222, 4444)
    statement = ("IRA ****1111   Balance: $11,000.00\n"
                 "Roth IRA ****2222   Balance: $15,000.00\n"
                 "Brokerage ****4444   Balance: $50,000.00\n").encode()
    r = auth_client.post(f"/reports/{seeded['client_id']}/extract",
                         data={"statement": (io.BytesIO(statement), "stmt.txt")},
                         content_type="multipart/form-data")
    assert r.status_code == 200
    assert b"Extracted" in r.data
    assert b"11000.00" in r.data and b"50000.00" in r.data


# ---- distribution ----
def test_email_report_route(auth_client, app, seeded):
    rid = _run(app, seeded)
    r = auth_client.post(f"/reports/run/{rid}/email", data={"to_email": "client@x.com"},
                         follow_redirects=True)
    assert b"emailed to client@x.com" in r.data
    with app.app_context():
        assert Outbox.query.filter_by(to_email="client@x.com").count() == 2


def test_dropbox_route_requires_connection(auth_client, app, seeded):
    rid = _run(app, seeded)
    r = auth_client.post(f"/reports/run/{rid}/dropbox", follow_redirects=True)
    assert b"not connected" in r.data


def test_dropbox_route_saves_when_connected(auth_client, app, seeded, route_through_sandbox):
    rid = _run(app, seeded)
    with app.app_context():
        db.session.add(ProviderCredential(tenant_id=seeded["tenant_id"], provider="dropbox",
                       status="active", base_url="http://sandbox/dropbox",
                       encrypted_token=get_vault().encrypt_dict({"access_token": "t"})))
        db.session.commit()
    r = auth_client.post(f"/reports/run/{rid}/dropbox", follow_redirects=True)
    assert b"Saved 2 file" in r.data


# ---- anomaly on review ----
def test_review_shows_anomaly_flags(auth_client, app, seeded):
    _run(app, seeded, trust="450000")            # prior quarter
    rid2 = _run(app, seeded, trust="900000")     # +100% trust move
    r = auth_client.get(f"/reports/run/{rid2}")
    assert b"anomaly flag" in r.data
    assert b"Home / Trust Value" in r.data or b"Trust" in r.data
