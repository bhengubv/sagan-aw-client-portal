"""Client & account management (spec 8.1 / US1)."""
from __future__ import annotations

from datetime import date

from flask import (Blueprint, render_template, request, redirect, url_for, flash, abort)

from .extensions import db
from .models import Client, Person, Account, Liability, Trust, StaticFinancials
from .security import login_required, role_required, current_user
from .audit import log_event
from .agents import onboarding

bp = Blueprint("clients", __name__, url_prefix="/clients")


def _get_client(cid):
    u = current_user()
    c = Client.query.filter_by(id=cid, tenant_id=u.tenant_id).first()
    if not c:
        abort(404)
    return c


def _parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


@bp.route("/")
@login_required
def list_clients():
    u = current_user()
    clients = Client.query.filter_by(tenant_id=u.tenant_id).order_by(Client.display_name).all()
    return render_template("clients/list.html", clients=clients)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_client():
    if request.method == "POST":
        name = (request.form.get("display_name") or "").strip()
        if not name:
            flash("Household name is required.", "error")
            return render_template("clients/new.html")
        c = Client(tenant_id=current_user().tenant_id, display_name=name)
        db.session.add(c)
        db.session.flush()
        # Optional first person
        p1 = (request.form.get("c1_name") or "").strip()
        if p1:
            db.session.add(Person(client_id=c.id, role="C1", name=p1,
                                  dob=_parse_date(request.form.get("c1_dob")),
                                  ssn_last4=(request.form.get("c1_ssn4") or "").strip() or None))
        db.session.add(StaticFinancials(client_id=c.id, insurance_deductibles=[]))
        db.session.commit()
        log_event("client_create", "client", c.display_name)
        flash("Client created.", "ok")
        return redirect(url_for("clients.detail", cid=c.id))
    return render_template("clients/new.html")


@bp.route("/<int:cid>")
@login_required
def detail(cid):
    c = _get_client(cid)
    log_event("client_view", "client", c.display_name)  # PII view (spec 13.2)
    return render_template("clients/detail.html", c=c)


@bp.route("/<int:cid>/persons", methods=["POST"])
@login_required
def add_person(cid):
    c = _get_client(cid)
    name = (request.form.get("name") or "").strip()
    if name:
        db.session.add(Person(client_id=c.id, role=request.form.get("role", "C2"),
                              name=name, dob=_parse_date(request.form.get("dob")),
                              ssn_last4=(request.form.get("ssn4") or "").strip() or None))
        db.session.commit()
        log_event("person_add", "client", c.display_name)
    return redirect(url_for("clients.detail", cid=cid))


@bp.route("/<int:cid>/accounts", methods=["POST"])
@login_required
def add_account(cid):
    c = _get_client(cid)
    atype = (request.form.get("type") or "").strip()
    owner = request.form.get("owner", "JOINT")
    category = request.form.get("category", "non_retirement")
    if category == "retirement" and owner == "JOINT":
        flash("Retirement accounts cannot be joint.", "error")
        return redirect(url_for("clients.detail", cid=cid))
    if atype:
        db.session.add(Account(client_id=c.id, type=atype, owner=owner, category=category,
                               acct_last4=(request.form.get("acct_last4") or "").strip() or None,
                               has_cash_balance=bool(request.form.get("has_cash"))))
        db.session.commit()
        log_event("account_add", "client", f"{c.display_name}:{atype}")
    return redirect(url_for("clients.detail", cid=cid))


@bp.route("/<int:cid>/liabilities", methods=["POST"])
@login_required
def add_liability(cid):
    c = _get_client(cid)
    ltype = (request.form.get("type") or "").strip()
    if ltype:
        db.session.add(Liability(client_id=c.id, type=ltype,
                                 interest_rate=(request.form.get("interest_rate") or "0").strip()))
        db.session.commit()
        log_event("liability_add", "client", c.display_name)
    return redirect(url_for("clients.detail", cid=cid))


@bp.route("/<int:cid>/trust", methods=["POST"])
@login_required
def set_trust(cid):
    c = _get_client(cid)
    addr = (request.form.get("property_address") or "").strip()
    if c.trust:
        c.trust.property_address = addr
    else:
        db.session.add(Trust(client_id=c.id, property_address=addr))
    db.session.commit()
    log_event("trust_set", "client", c.display_name)
    return redirect(url_for("clients.detail", cid=cid))


@bp.route("/<int:cid>/static", methods=["POST"])
@login_required
def set_static(cid):
    c = _get_client(cid)
    s = c.static or StaticFinancials(client_id=c.id)
    s.monthly_salary_inflow = (request.form.get("inflow") or "0").strip()
    s.monthly_expense_budget_outflow = (request.form.get("outflow") or "0").strip()
    s.normal_monthly_expenses = (request.form.get("expenses") or "0").strip()
    deds = [d.strip() for d in (request.form.get("deductibles") or "").split(",") if d.strip()]
    s.insurance_deductibles = deds
    if not c.static:
        db.session.add(s)
    db.session.commit()
    log_event("static_set", "client", c.display_name)
    flash("Financials saved.", "ok")
    return redirect(url_for("clients.detail", cid=cid))


@bp.route("/<int:cid>/accounts/<int:aid>/delete", methods=["POST"])
@login_required
def delete_account(cid, aid):
    c = _get_client(cid)
    a = Account.query.filter_by(id=aid, client_id=c.id).first_or_404()
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for("clients.detail", cid=cid))


@bp.route("/<int:cid>/liabilities/<int:lid>/delete", methods=["POST"])
@login_required
def delete_liability(cid, lid):
    c = _get_client(cid)
    li = Liability.query.filter_by(id=lid, client_id=c.id).first_or_404()
    db.session.delete(li)
    db.session.commit()
    return redirect(url_for("clients.detail", cid=cid))


@bp.route("/<int:cid>/onboard", methods=["POST"])
@login_required
def onboard(cid):
    c = _get_client(cid)
    email = (request.form.get("email") or "").strip()
    if email:
        onboarding.create_invite(c.tenant_id, email, client_id=c.id)
        log_event("onboard_invite", "client", c.display_name)
        flash("Onboarding invite sent.", "ok")
    return redirect(url_for("clients.detail", cid=cid))


@bp.route("/<int:cid>/worksheet", methods=["POST"])
@login_required
def worksheet_invite(cid):
    c = _get_client(cid)
    email = (request.form.get("email") or "").strip()
    if email:
        onboarding.create_expense_invite(c.tenant_id, c.id, email)
        log_event("worksheet_invite", "client", c.display_name)
        flash("Expense worksheet sent to the client.", "ok")
    return redirect(url_for("clients.detail", cid=cid))


@bp.route("/<int:cid>/delete", methods=["POST"])
@role_required("owner", "planner")
def delete_client(cid):
    c = _get_client(cid)
    name = c.display_name
    db.session.delete(c)
    db.session.commit()
    log_event("client_delete", "client", name)
    flash(f"Deleted {name}.", "ok")
    return redirect(url_for("clients.list_clients"))
