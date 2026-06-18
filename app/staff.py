"""Staff inbox (spec 8.8-8.10): outbox, onboarding escalations, expense approvals."""
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash

from .models import Outbox, OnboardingInvite, ExpenseSubmission, Client
from .security import login_required, role_required, current_user
from .audit import log_event
from .agents import onboarding

bp = Blueprint("staff", __name__, url_prefix="/staff")


@bp.route("/inbox")
@login_required
def inbox():
    tid = current_user().tenant_id
    outbox = (Outbox.query.filter_by(tenant_id=tid)
              .order_by(Outbox.created_at.desc()).limit(50).all())
    escalations = OnboardingInvite.query.filter_by(tenant_id=tid, status="escalated").all()
    pending = ExpenseSubmission.query.filter_by(tenant_id=tid, status="submitted").all()
    clients = {c.id: c.display_name for c in Client.query.filter_by(tenant_id=tid).all()}
    return render_template("staff/inbox.html", outbox=outbox, escalations=escalations,
                           pending=pending, clients=clients)


@bp.route("/expense/<int:sid>/approve", methods=["POST"])
@login_required
def approve_expense(sid):
    sub = ExpenseSubmission.query.filter_by(
        id=sid, tenant_id=current_user().tenant_id).first_or_404()
    onboarding.approve_expense(sub)
    log_event("expense_approve", "client", str(sub.client_id))
    flash("Worksheet approved and applied to the client's financials.", "ok")
    return redirect(url_for("staff.inbox"))


@bp.route("/run-reminders", methods=["POST"])
@role_required("owner", "planner")
def run_reminders():
    res = onboarding.run_reminders()
    flash(f"Sent {res['reminders']} reminder(s); escalated {res['escalated']}.", "ok")
    return redirect(url_for("staff.inbox"))
