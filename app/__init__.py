"""Application factory for the AW Client Report Portal (spec 6)."""
from __future__ import annotations

import os

from flask import Flask, redirect, url_for, render_template

from .config import Config
from .extensions import db
from .security import current_user


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    from . import models  # noqa: F401  (register models)
    from .auth import bp as auth_bp
    from .clients import bp as clients_bp
    from .reports import bp as reports_bp
    from .settings import bp as settings_bp
    from .staff import bp as staff_bp
    from .portal_public import bp as public_bp
    from .signup import bp as signup_bp
    from .admin import bp as admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_user():
        from .models import Tenant
        u = current_user()
        brand = None
        if u:
            t = db.session.get(Tenant, u.tenant_id)
            brand = t.brand_color if t else None
        return {"current_user": u, "brand_color": brand or "#2E5E8C"}

    @app.before_request
    def enforce_tenant_status():
        from flask import request, render_template
        from .models import Tenant
        u = current_user()
        if u and u.role != "superadmin":
            t = db.session.get(Tenant, u.tenant_id)
            if t and t.status == "suspended" and request.endpoint not in ("auth.logout", "static"):
                return render_template("error.html", code=403,
                                       message="This workspace is suspended. Please contact support."), 403

    @app.route("/")
    def index():
        if current_user():
            return redirect(url_for("clients.list_clients"))
        return redirect(url_for("auth.login"))

    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403,
                               message="You do not have permission for that action."), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404,
                               message="Not found."), 404

    with app.app_context():
        db.create_all()

    return app
