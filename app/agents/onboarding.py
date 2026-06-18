"""Onboarding & client-intake agent (spec 8.8, 8.9).

Sends a client a tokenised onboarding link, chases reminders, and escalates to staff
after a threshold. Also issues the client-facing expense worksheet and lands submissions
for staff approval. Human-in-the-loop: nothing reaches a profile without approval.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from flask import current_app

from ..extensions import db
from ..models import OnboardingInvite, ExpenseSubmission, StaticFinancials, User
from ..mailer import send_email

MAX_REMINDERS = 4
REMINDER_INTERVAL = timedelta(days=2)


def _token():
    return secrets.token_urlsafe(24)


def _link(kind, token):
    base = current_app.config.get("PUBLIC_BASE_URL", "").rstrip("/")
    return f"{base}/{kind}/{token}"


# ----------------------------------------------------------------- onboarding
def create_invite(tenant_id, email, client_id=None, now=None):
    now = now or datetime.utcnow()
    inv = OnboardingInvite(tenant_id=tenant_id, client_id=client_id, email=email,
                           token=_token(), status="sent", created_at=now)
    db.session.add(inv)
    db.session.commit()
    link = _link("welcome", inv.token)
    send_email(tenant_id, email, "Welcome — please complete your onboarding",
               f"Welcome! Please complete your secure onboarding form:\n{link}")
    return inv


def due_reminders(now=None):
    now = now or datetime.utcnow()
    due = []
    for inv in OnboardingInvite.query.filter_by(status="sent").all():
        last = inv.last_reminder_at or inv.created_at
        if now - last >= REMINDER_INTERVAL and inv.reminders_sent < MAX_REMINDERS:
            due.append(inv)
    return due


def run_reminders(now=None):
    """Send due reminders; escalate to staff after MAX_REMINDERS. Returns a summary."""
    now = now or datetime.utcnow()
    sent = escalated = 0
    for inv in due_reminders(now):
        link = _link("welcome", inv.token)
        send_email(inv.tenant_id, inv.email, "Reminder: please complete your onboarding",
                   f"A reminder to complete your onboarding form:\n{link}")
        inv.reminders_sent += 1
        inv.last_reminder_at = now
        sent += 1
        if inv.reminders_sent >= MAX_REMINDERS:
            inv.status = "escalated"
            escalated += 1
            owner = User.query.filter_by(tenant_id=inv.tenant_id, role="owner").first()
            if owner:
                send_email(inv.tenant_id, owner.email,
                           "Onboarding needs a personal nudge",
                           f"{inv.email} has not completed onboarding after {MAX_REMINDERS} "
                           f"reminders. Consider a personal call.")
    db.session.commit()
    return {"reminders": sent, "escalated": escalated}


def complete_invite(token, data, now=None):
    now = now or datetime.utcnow()
    inv = OnboardingInvite.query.filter_by(token=token).first()
    if not inv or inv.status == "completed":
        return None
    inv.data = data
    inv.status = "completed"
    inv.completed_at = now
    db.session.commit()
    return inv


# ------------------------------------------------------------ expense worksheet
def create_expense_invite(tenant_id, client_id, email, now=None):
    now = now or datetime.utcnow()
    sub = ExpenseSubmission(tenant_id=tenant_id, client_id=client_id, token=_token(),
                            status="sent", created_at=now)
    db.session.add(sub)
    db.session.commit()
    link = _link("worksheet", sub.token)
    send_email(tenant_id, email, "Your monthly expense worksheet",
               f"Please complete your expense worksheet here:\n{link}")
    return sub


def submit_expense(token, data, now=None):
    now = now or datetime.utcnow()
    sub = ExpenseSubmission.query.filter_by(token=token).first()
    if not sub or sub.status == "approved":
        return None
    sub.data = data
    sub.status = "submitted"
    sub.submitted_at = now
    db.session.commit()
    return sub


def approve_expense(submission, now=None):
    """Staff approval lands the worksheet into the client's static financials (spec 8.9)."""
    now = now or datetime.utcnow()
    s = StaticFinancials.query.filter_by(client_id=submission.client_id).first()
    if not s:
        s = StaticFinancials(client_id=submission.client_id)
        db.session.add(s)
    d = submission.data or {}
    if d.get("salary") is not None:
        s.monthly_salary_inflow = str(d["salary"])
    if d.get("expense_budget") is not None:
        s.monthly_expense_budget_outflow = str(d["expense_budget"])
    if d.get("expenses") is not None:
        s.normal_monthly_expenses = str(d["expenses"])
    if d.get("deductibles") is not None:
        s.insurance_deductibles = [str(x) for x in d["deductibles"]]
    submission.status = "approved"
    submission.approved_at = now
    db.session.commit()
    return s
