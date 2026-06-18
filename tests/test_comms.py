"""Mailer, onboarding agent, expense worksheet, and distribution (spec 8.8-8.10)."""
from datetime import datetime, timedelta

import pytest

from app.extensions import db
from app.mailer import send_email
from app.agents import onboarding
from app.models import (Outbox, OnboardingInvite, ExpenseSubmission, StaticFinancials,
                        Client, ReportRun, ProviderCredential)
from app.vault import get_vault
from app import reporting, distribution


# ---- mailer ----
def test_send_email_recorded_without_smtp(app, seeded):
    with app.app_context():
        row = send_email(seeded["tenant_id"], "x@y.com", "Hi", "Body")
        assert row.status == "recorded"
        assert Outbox.query.count() == 1


def test_send_email_uses_smtp_when_configured(app, seeded, monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=None):
            sent["host"] = host

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def starttls(self, context=None):
            sent["tls"] = True

        def login(self, u, p):
            sent["login"] = u

        def send_message(self, em):
            sent["to"] = em["To"]

    monkeypatch.setattr("app.mailer.smtplib.SMTP", FakeSMTP)
    with app.app_context():
        app.config.update(SMTP_HOST="smtp.test", SMTP_USER="u", SMTP_PASSWORD="p")
        row = send_email(seeded["tenant_id"], "to@x.com", "S", "B")
        status = row.status
    assert status == "sent"
    assert sent["to"] == "to@x.com" and sent["host"] == "smtp.test" and sent["tls"]


# ---- onboarding agent ----
def test_invite_reminders_and_escalation(app, seeded):
    with app.app_context():
        t0 = datetime(2026, 6, 1, 12, 0, 0)
        inv = onboarding.create_invite(seeded["tenant_id"], "client@x.com", now=t0)
        assert Outbox.query.count() == 1                       # the invite
        assert onboarding.due_reminders(now=t0) == []          # not yet due
        now = t0
        for _ in range(4):
            now = now + timedelta(days=2, seconds=1)
            onboarding.run_reminders(now=now)
        inv = db.session.get(OnboardingInvite, inv.id)
        assert inv.reminders_sent == 4
        assert inv.status == "escalated"
        assert Outbox.query.filter_by(subject="Onboarding needs a personal nudge").count() == 1


def test_complete_invite_stops_reminders(app, seeded):
    with app.app_context():
        t0 = datetime(2026, 6, 1)
        inv = onboarding.create_invite(seeded["tenant_id"], "c@x.com", now=t0)
        onboarding.complete_invite(inv.token, {"answer": "ok"}, now=t0)
        assert onboarding.due_reminders(now=t0 + timedelta(days=30)) == []
        inv = db.session.get(OnboardingInvite, inv.id)
        assert inv.status == "completed" and inv.data == {"answer": "ok"}


def test_expense_worksheet_lands_on_approval(app, seeded):
    with app.app_context():
        cid = seeded["client_id"]
        sub = onboarding.create_expense_invite(seeded["tenant_id"], cid, "c@x.com")
        onboarding.submit_expense(sub.token, {"salary": "16000", "expense_budget": "12500",
                                              "expenses": "11000", "deductibles": ["1000", "2000"]})
        sub = db.session.get(ExpenseSubmission, sub.id)
        assert sub.status == "submitted"
        onboarding.approve_expense(sub)
        s = StaticFinancials.query.filter_by(client_id=cid).first()
        assert s.monthly_salary_inflow == "16000"
        assert s.normal_monthly_expenses == "11000"
        assert s.insurance_deductibles == ["1000", "2000"]


# ---- distribution ----
def _make_run(app, seeded):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        entered = {"private_reserve_balance": "75000", "investment_account_balance": "15000",
                   "trust": "450000", f"liability:{c.liabilities[0].id}": "200000"}
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


def test_email_report_attaches_two_pdfs(app, seeded):
    rid = _make_run(app, seeded)
    with app.app_context():
        run = db.session.get(ReportRun, rid)
        rows = distribution.email_report(run, "client@x.com")
        assert len(rows) == 2
        assert all(r.status == "recorded" for r in rows)
        assert rows[0].attachment_name.startswith("SACS_")
        assert rows[1].attachment_name.startswith("TCC_")


def test_save_to_dropbox(app, seeded, route_through_sandbox):
    rid = _make_run(app, seeded)
    with app.app_context():
        v = get_vault()
        db.session.add(ProviderCredential(tenant_id=seeded["tenant_id"], provider="dropbox",
                       status="active", base_url="http://sandbox/dropbox",
                       encrypted_token=v.encrypt_dict({"access_token": "t"})))
        db.session.commit()
        run = db.session.get(ReportRun, rid)
        res = distribution.save_to_dropbox(run)
    assert len(res) == 2
    assert res[0]["path_display"].endswith("SACS.pdf")


def test_export_to_canva(app, seeded, route_through_sandbox):
    rid = _make_run(app, seeded)
    with app.app_context():
        v = get_vault()
        db.session.add(ProviderCredential(tenant_id=seeded["tenant_id"], provider="canva",
                       status="active", base_url="http://sandbox/canva",
                       encrypted_token=v.encrypt_dict({"access_token": "t"})))
        db.session.commit()
        run = db.session.get(ReportRun, rid)
        res = distribution.export_to_canva(run)
    assert "edit_url" in res["design"]["urls"]


def test_dropbox_not_connected_raises(app, seeded):
    rid = _make_run(app, seeded)
    with app.app_context():
        run = db.session.get(ReportRun, rid)
        with pytest.raises(distribution.DistributionError):
            distribution.save_to_dropbox(run)
