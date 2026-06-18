"""Client-facing public pages (spec 8.8, 8.9): tokenised, no login.

Onboarding form and expense worksheet. Submissions land for staff approval — nothing
reaches a client profile automatically.
"""
from __future__ import annotations

from flask import Blueprint, render_template, request, abort

from .models import OnboardingInvite, ExpenseSubmission
from .agents import onboarding

bp = Blueprint("public", __name__)


@bp.route("/welcome/<token>", methods=["GET", "POST"])
def welcome(token):
    inv = OnboardingInvite.query.filter_by(token=token).first()
    if not inv:
        abort(404)
    if inv.status == "completed":
        return render_template("public/thanks.html",
                               msg="This onboarding form has already been completed. Thank you.")
    if request.method == "POST":
        data = {k: request.form.get(k, "") for k in
                ("c1_name", "c1_dob", "c1_ssn4", "c2_name", "c2_dob", "c2_ssn4", "notes")}
        onboarding.complete_invite(token, data)
        return render_template("public/thanks.html",
                               msg="Thank you — your onboarding details were received securely.")
    return render_template("public/welcome.html", inv=inv)


@bp.route("/worksheet/<token>", methods=["GET", "POST"])
def worksheet(token):
    sub = ExpenseSubmission.query.filter_by(token=token).first()
    if not sub:
        abort(404)
    if sub.status == "approved":
        return render_template("public/thanks.html",
                               msg="This worksheet has already been processed. Thank you.")
    if request.method == "POST":
        deds = [d.strip() for d in request.form.get("deductibles", "").split(",") if d.strip()]
        onboarding.submit_expense(token, {
            "salary": request.form.get("salary", "0"),
            "expense_budget": request.form.get("expense_budget", "0"),
            "expenses": request.form.get("expenses", "0"),
            "deductibles": deds,
        })
        return render_template("public/thanks.html",
                               msg="Thank you — your expense worksheet was submitted.")
    return render_template("public/worksheet.html", sub=sub)
