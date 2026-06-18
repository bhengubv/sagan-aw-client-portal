"""End-to-end route + workflow tests (spec US1-US4, 8.6)."""
from app.extensions import db
from app.models import Client, ReportRun, Tenant
from app import reporting
from tests.conftest import login


def _full_form(app, seeded):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        data = {f["key"]: "0" for f in reporting.required_fields(c)}
    acc = seeded["accounts"]
    data.update({
        "period": "2026 Q3",
        "private_reserve_balance": "75000",
        "investment_account_balance": "15000",
        f"account:{acc[0]}": "11000",
        f"account:{acc[1]}": "15000",
        f"account_cash:{acc[1]}": "316",
        f"account:{acc[2]}": "50000",
        "trust": "450000",
        f"liability:{seeded['liabilities'][0]}": "200000",
    })
    return data


# ---- auth ----
def test_clients_requires_login(client):
    r = client.get("/clients/", follow_redirects=False)
    assert r.status_code == 302
    assert "/auth/login" in r.headers["Location"]


def test_login_then_list(client, seeded):
    r = login(client)
    assert r.status_code == 200
    assert b"Clients" in r.data


def test_bad_password_rejected(client, seeded):
    r = login(client, password="wrong")
    assert b"Invalid email or password" in r.data


def test_healthz(client):
    assert client.get("/healthz").get_json() == {"status": "ok"}


# ---- client management ----
def test_create_client(auth_client, app):
    r = auth_client.post("/clients/new", data={"display_name": "New Family", "c1_name": "Sam"},
                         follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert Client.query.filter_by(display_name="New Family").count() == 1


def test_retirement_account_cannot_be_joint_via_route(auth_client, seeded, app):
    cid = seeded["client_id"]
    r = auth_client.post(f"/clients/{cid}/accounts",
                         data={"type": "401k", "owner": "JOINT", "category": "retirement"},
                         follow_redirects=True)
    assert b"cannot be joint" in r.data


# ---- report workflow ----
def test_new_report_form_loads(auth_client, seeded):
    r = auth_client.get(f"/reports/{seeded['client_id']}/new")
    assert r.status_code == 200
    assert b"Generate report" in r.data


def test_generate_blocked_when_fields_missing(auth_client, seeded, app):
    cid = seeded["client_id"]
    r = auth_client.post(f"/reports/{cid}/generate", data={"period": "2026 Q3"})
    assert r.status_code == 200
    assert b"cannot be generated" in r.data
    with app.app_context():
        assert ReportRun.query.count() == 0  # nothing saved


def test_generate_success_and_download(auth_client, seeded, app):
    cid = seeded["client_id"]
    data = _full_form(app, seeded)
    r = auth_client.post(f"/reports/{cid}/generate", data=data, follow_redirects=True)
    assert r.status_code == 200
    assert b"Report ready" in r.data
    assert b"526,000" in r.data or b"526000" in r.data  # grand total shown
    with app.app_context():
        run = ReportRun.query.first()
        assert run is not None
        assert run.computed_values["tcc"]["grand_total_net_worth"] == "526000.00"
        rid = run.id
    sacs = auth_client.get(f"/reports/run/{rid}/sacs.pdf")
    assert sacs.status_code == 200
    assert sacs.mimetype == "application/pdf"
    assert sacs.data[:4] == b"%PDF"
    tcc = auth_client.get(f"/reports/run/{rid}/tcc.pdf")
    assert tcc.status_code == 200
    assert tcc.data[:4] == b"%PDF"


def test_history_lists_run(auth_client, seeded, app):
    cid = seeded["client_id"]
    auth_client.post(f"/reports/{cid}/generate", data=_full_form(app, seeded), follow_redirects=True)
    r = auth_client.get(f"/reports/{cid}/history")
    assert r.status_code == 200
    assert b"2026 Q3" in r.data


# ---- RBAC + tenant isolation ----
def test_assistant_cannot_delete_client(client, seeded):
    login(client, email="asst@t.test")
    r = client.post(f"/clients/{seeded['client_id']}/delete")
    assert r.status_code == 403


def test_owner_can_delete_client(client, seeded, app):
    login(client, email="owner@t.test")
    r = client.post(f"/clients/{seeded['client_id']}/delete", follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert db.session.get(Client, seeded["client_id"]) is None


def test_tenant_isolation(auth_client, seeded, app):
    with app.app_context():
        other = Tenant(name="Other Firm")
        db.session.add(other); db.session.flush()
        oc = Client(tenant_id=other.id, display_name="Not Yours")
        db.session.add(oc); db.session.commit()
        other_cid = oc.id
    r = auth_client.get(f"/clients/{other_cid}")
    assert r.status_code == 404
