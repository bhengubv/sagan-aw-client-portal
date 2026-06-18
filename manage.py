"""Admin CLI: create users and enrol TOTP MFA (spec 8.6).

  python manage.py create-user --email a@b.com --name "Jane" --role planner --password secret
  python manage.py enroll-mfa --email a@b.com      # prints an otpauth:// URI for the authenticator
"""
import argparse

import pyotp
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Tenant, User


def create_user(args):
    app = create_app()
    with app.app_context():
        tenant = Tenant.query.first()
        if not tenant:
            tenant = Tenant(name="Default Firm")
            db.session.add(tenant)
            db.session.flush()
        if User.query.filter_by(email=args.email.lower()).first():
            print("user already exists")
            return
        db.session.add(User(tenant_id=tenant.id, name=args.name, email=args.email.lower(),
                            role=args.role, password_hash=generate_password_hash(args.password)))
        db.session.commit()
        print(f"created {args.email} ({args.role})")


def enroll_mfa(args):
    app = create_app()
    with app.app_context():
        u = User.query.filter_by(email=args.email.lower()).first()
        if not u:
            print("no such user")
            return
        secret = pyotp.random_base32()
        u.mfa_secret = secret
        u.mfa_enabled = True
        db.session.commit()
        uri = pyotp.TOTP(secret).provisioning_uri(name=u.email, issuer_name="AW Client Report Portal")
        print("MFA enabled. Add this to your authenticator app:")
        print(uri)


def run_reminders(args):
    app = create_app()
    with app.app_context():
        from app.agents import onboarding
        res = onboarding.run_reminders()
        print(f"reminders sent: {res['reminders']}, escalated: {res['escalated']}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(required=True)
    rr = sub.add_parser("run-reminders")
    rr.set_defaults(func=run_reminders)
    cu = sub.add_parser("create-user")
    cu.add_argument("--email", required=True)
    cu.add_argument("--name", required=True)
    cu.add_argument("--role", default="assistant", choices=["owner", "planner", "assistant"])
    cu.add_argument("--password", required=True)
    cu.set_defaults(func=create_user)
    em = sub.add_parser("enroll-mfa")
    em.add_argument("--email", required=True)
    em.set_defaults(func=enroll_mfa)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
