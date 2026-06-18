"""Auth helpers: current user, login/role decorators (spec 8.6)."""
from __future__ import annotations

from functools import wraps

from flask import g, session, redirect, url_for, flash, abort

from .extensions import db
from .models import User

ROLES = ("owner", "planner", "assistant")


def current_user():
    if "user" not in g:
        uid = session.get("user_id")
        g.user = db.session.get(User, uid) if uid else None
    return g.user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            flash("Please sign in.", "warn")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def deco(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            u = current_user()
            if u is None:
                return redirect(url_for("auth.login"))
            if u.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return deco
