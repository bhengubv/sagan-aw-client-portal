"""Phase 4: self-serve signup, billing/metering, admin console, suspension (spec 4, 16)."""
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User, Tenant, Client, UsageRecord
from app import billing, reporting
from tests.conftest import login


# ---- signup ----
def test_signup_creates_tenant_and_owner(client, app):
    r = client.post("/signup", data={"firm": "New Firm", "name": "Boss",
                                     "email": "boss@new.test", "password": "pw123456",
                                     "brand_color": "#123456"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Clients" in r.data                      # logged straight in
    with app.app_context():
        u = User.query.filter_by(email="boss@new.test").first()
        assert u and u.role == "owner"
        t = db.session.get(Tenant, u.tenant_id)
        assert t.name == "New Firm" and t.brand_color == "#123456"


def test_signup_rejects_duplicate_email(client, seeded):
    r = client.post("/signup", data={"firm": "X", "name": "Y", "email": "owner@t.test",
                                     "password": "pw"}, follow_redirects=True)
    assert b"already registered" in r.data


# ---- billing ----
def test_billing_math_cost_plus_markup(app, seeded):
    with app.app_context():
        billing.record_usage(seeded["tenant_id"], "report_generate")          # 0.50
        billing.record_usage(seeded["tenant_id"], "provider_call", quantity=5)  # 0.10
        billing.record_usage(seeded["tenant_id"], "ai_call")                   # 0.10
        s = billing.tenant_summary(seeded["tenant_id"])
    assert s["base_total"] == Decimal("0.70")
    assert s["billed_total"] == Decimal("0.84")       # 0.70 * 1.20
    assert s["by_kind"]["provider_call"]["qty"] == 5


def test_report_generation_is_metered(auth_client, app, seeded):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        form = {f["key"]: "0" for f in reporting.required_fields(c)}
    form["period"] = "2026 Q2"
    auth_client.post(f"/reports/{seeded['client_id']}/generate", data=form, follow_redirects=True)
    with app.app_context():
        assert UsageRecord.query.filter_by(tenant_id=seeded["tenant_id"],
                                           kind="report_generate").count() == 1


def test_billing_view_renders(auth_client, app, seeded):
    with app.app_context():
        billing.record_usage(seeded["tenant_id"], "report_generate")
    r = auth_client.get("/settings/billing")
    assert r.status_code == 200
    assert b"0.50" in r.data and b"0.60" in r.data     # base 0.50, billed 0.60


# ---- admin + suspension ----
def _make_superadmin(app, seeded):
    with app.app_context():
        sa = User(tenant_id=seeded["tenant_id"], name="SA", email="sa@t.test",
                  role="superadmin", password_hash=generate_password_hash("pw12345"))
        db.session.add(sa)
        db.session.commit()


def test_admin_requires_superadmin(auth_client):
    assert auth_client.get("/admin/").status_code == 403      # owner is not superadmin


def test_superadmin_dashboard_lists_tenants(client, app, seeded):
    _make_superadmin(app, seeded)
    login(client, email="sa@t.test")
    r = client.get("/admin/")
    assert r.status_code == 200
    assert b"Test Firm" in r.data


def test_suspension_blocks_tenant_but_not_superadmin(client, app, seeded):
    _make_superadmin(app, seeded)
    admin_c = app.test_client()
    login(admin_c, email="sa@t.test")
    login(client, email="owner@t.test")
    assert client.get("/clients/").status_code == 200

    admin_c.post(f"/admin/tenant/{seeded['tenant_id']}/suspend")
    assert client.get("/clients/").status_code == 403          # owner blocked
    assert admin_c.get("/admin/").status_code == 200           # superadmin unaffected

    admin_c.post(f"/admin/tenant/{seeded['tenant_id']}/activate")
    assert client.get("/clients/").status_code == 200          # reactivated
