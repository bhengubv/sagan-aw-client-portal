"""Self-serve firm signup (spec 4 Phase 4): create a new tenant + owner, no login required."""
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import Tenant, User
from .security import current_user

bp = Blueprint("signup", __name__)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user():
        return redirect(url_for("clients.list_clients"))
    if request.method == "POST":
        firm = (request.form.get("firm") or "").strip()
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        pw = request.form.get("password") or ""
        brand = (request.form.get("brand_color") or "#2E5E8C").strip()
        if not (firm and name and email and pw):
            flash("All fields are required.", "error")
            return render_template("signup.html")
        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "error")
            return render_template("signup.html")
        tenant = Tenant(name=firm, brand_color=brand)
        db.session.add(tenant)
        db.session.flush()
        user = User(tenant_id=tenant.id, name=name, email=email, role="owner",
                    password_hash=generate_password_hash(pw))
        db.session.add(user)
        db.session.commit()
        session.clear()
        session["user_id"] = user.id
        session.permanent = True
        flash("Welcome — your firm workspace is ready.", "ok")
        return redirect(url_for("clients.list_clients"))
    return render_template("signup.html")
