"""Platform admin console (spec 4 Phase 4): superadmin oversight of all tenants."""
from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, abort

from .extensions import db
from .models import Tenant, User, Client
from .security import role_required
from .audit import log_event
from . import billing

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@role_required("superadmin")
def dashboard():
    rows = []
    for t in Tenant.query.order_by(Tenant.created_at.desc()).all():
        rows.append({
            "t": t,
            "summary": billing.tenant_summary(t.id),
            "clients": Client.query.filter_by(tenant_id=t.id).count(),
            "users": User.query.filter_by(tenant_id=t.id).count(),
        })
    return render_template("admin/dashboard.html", rows=rows)


def _tenant(tid):
    t = db.session.get(Tenant, tid)
    if not t:
        abort(404)
    return t


@bp.route("/tenant/<int:tid>/suspend", methods=["POST"])
@role_required("superadmin")
def suspend(tid):
    t = _tenant(tid)
    t.status = "suspended"
    db.session.commit()
    log_event("tenant_suspend", "tenant", t.name)
    flash(f"Suspended {t.name}.", "ok")
    return redirect(url_for("admin.dashboard"))


@bp.route("/tenant/<int:tid>/activate", methods=["POST"])
@role_required("superadmin")
def activate(tid):
    t = _tenant(tid)
    t.status = "active"
    db.session.commit()
    log_event("tenant_activate", "tenant", t.name)
    flash(f"Reactivated {t.name}.", "ok")
    return redirect(url_for("admin.dashboard"))
