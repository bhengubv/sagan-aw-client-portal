"""Provider connection management (spec 11): connect/activate data providers per tenant.

Secrets are encrypted in the vault. base_url points at the live provider in production
or the local sandbox in dev.
"""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, flash

from .extensions import db
from .models import ProviderCredential
from .security import login_required, role_required, current_user
from .audit import log_event
from .vault import get_vault
from .providers.registry import ALL_PROVIDERS
from . import billing

bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/billing")
@login_required
def billing_view():
    summary = billing.tenant_summary(current_user().tenant_id)
    return render_template("settings/billing.html", summary=summary)


@bp.route("/providers")
@login_required
def providers():
    creds = ProviderCredential.query.filter_by(tenant_id=current_user().tenant_id).all()
    return render_template("settings/providers.html", creds=creds,
                           names=sorted(ALL_PROVIDERS.keys()))


@bp.route("/providers/connect", methods=["POST"])
@role_required("owner", "planner")
def connect():
    provider = request.form.get("provider", "")
    if provider not in ALL_PROVIDERS:
        flash("Unknown provider.", "error")
        return redirect(url_for("settings.providers"))
    secrets = {}
    for line in request.form.get("secrets", "").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            secrets[k.strip()] = v.strip()
    cred = ProviderCredential(
        tenant_id=current_user().tenant_id, provider=provider,
        base_url=request.form.get("base_url", "").strip(),
        encrypted_token=get_vault().encrypt_dict(secrets), status="active")
    db.session.add(cred)
    db.session.commit()
    log_event("provider_connect", "provider", provider)
    flash(f"Connected {provider} (read-only).", "ok")
    return redirect(url_for("settings.providers"))


def _own(pid):
    return ProviderCredential.query.filter_by(
        id=pid, tenant_id=current_user().tenant_id).first_or_404()


@bp.route("/providers/<int:pid>/toggle", methods=["POST"])
@role_required("owner", "planner")
def toggle(pid):
    cred = _own(pid)
    cred.status = "inactive" if cred.status == "active" else "active"
    db.session.commit()
    log_event("provider_toggle", "provider", f"{cred.provider}:{cred.status}")
    return redirect(url_for("settings.providers"))


@bp.route("/providers/<int:pid>/delete", methods=["POST"])
@role_required("owner", "planner")
def delete(pid):
    cred = _own(pid)
    db.session.delete(cred)
    db.session.commit()
    return redirect(url_for("settings.providers"))
