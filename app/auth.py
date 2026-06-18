"""Authentication: password login + optional TOTP MFA (spec 8.6)."""
from __future__ import annotations

import pyotp
from flask import (Blueprint, render_template, request, redirect, url_for,
                   session, flash)
from werkzeug.security import check_password_hash

from .models import User
from .audit import log_event
from .security import current_user, login_required

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("clients.list_clients"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            log_event("login_failed", "user", email)
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")
        if user.mfa_enabled and user.mfa_secret:
            session["pending_user"] = user.id
            return redirect(url_for("auth.mfa"))
        _complete_login(user)
        return redirect(url_for("clients.list_clients"))
    return render_template("auth/login.html")


@bp.route("/mfa", methods=["GET", "POST"])
def mfa():
    uid = session.get("pending_user")
    if not uid:
        return redirect(url_for("auth.login"))
    user = User.query.get(uid)
    if request.method == "POST":
        code = (request.form.get("code") or "").strip()
        if user and pyotp.TOTP(user.mfa_secret).verify(code, valid_window=1):
            session.pop("pending_user", None)
            _complete_login(user)
            return redirect(url_for("clients.list_clients"))
        flash("Invalid authentication code.", "error")
    return render_template("auth/mfa.html")


def _complete_login(user):
    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    log_event("login", "user", user.email)


@bp.route("/logout")
@login_required
def logout():
    log_event("logout", "user", current_user().email)
    session.clear()
    flash("Signed out.", "ok")
    return redirect(url_for("auth.login"))
