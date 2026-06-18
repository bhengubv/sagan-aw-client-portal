"""Data model (spec Section 7).

Every business row carries a tenant_id so Phase 4 multi-tenancy is configuration,
not migration. Money is stored as strings and always passed through calc.money()
to keep exact Decimal arithmetic (SQLite has no native decimal type).
"""
from __future__ import annotations

from datetime import date, datetime

from .extensions import db


class Tenant(db.Model):
    __tablename__ = "tenant"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand_color = db.Column(db.String(7), default="#2E5E8C")
    region = db.Column(db.String(50), default="us")
    status = db.Column(db.String(20), default="active")  # active|suspended (Phase 4)
    plan = db.Column(db.String(40), default="standard")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship("User", backref="tenant", cascade="all, delete-orphan")
    clients = db.relationship("Client", backref="tenant", cascade="all, delete-orphan")


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default="assistant")  # owner|planner|assistant
    password_hash = db.Column(db.String(255), nullable=False)
    mfa_secret = db.Column(db.String(64))      # TOTP secret (set when MFA enrolled)
    mfa_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Client(db.Model):
    """A household (not an individual)."""
    __tablename__ = "client"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    display_name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(30), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    persons = db.relationship("Person", backref="client", cascade="all, delete-orphan")
    accounts = db.relationship("Account", backref="client", cascade="all, delete-orphan")
    liabilities = db.relationship("Liability", backref="client", cascade="all, delete-orphan")
    trust = db.relationship("Trust", backref="client", uselist=False, cascade="all, delete-orphan")
    static = db.relationship("StaticFinancials", backref="client", uselist=False, cascade="all, delete-orphan")
    reports = db.relationship("ReportRun", backref="client", cascade="all, delete-orphan",
                              order_by="ReportRun.created_at.desc()")

    @property
    def last_report(self):
        return self.reports[0] if self.reports else None


class Person(db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    role = db.Column(db.String(2), nullable=False, default="C1")  # C1|C2
    name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date)
    ssn_last4 = db.Column(db.String(4))

    @property
    def age(self):
        if not self.dob:
            return None
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))


class Account(db.Model):
    """Account STRUCTURE. The balance is dynamic and captured per ReportRun."""
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    owner = db.Column(db.String(6), nullable=False, default="JOINT")          # C1|C2|JOINT
    category = db.Column(db.String(20), nullable=False, default="non_retirement")  # retirement|non_retirement
    type = db.Column(db.String(80), nullable=False)                            # e.g. "Roth IRA"
    acct_last4 = db.Column(db.String(4))
    has_cash_balance = db.Column(db.Boolean, default=False)                     # investment accounts
    provider = db.Column(db.String(40))        # plaid|schwab|rightcapital... (Phase 2 link)
    external_ref = db.Column(db.String(120))   # provider's account id, for automated pulls


class Trust(db.Model):
    __tablename__ = "trust"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    property_address = db.Column(db.String(300))


class Liability(db.Model):
    """Liability STRUCTURE. The balance is dynamic and captured per ReportRun."""
    __tablename__ = "liability"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    type = db.Column(db.String(80), nullable=False)         # e.g. "Mortgage"
    interest_rate = db.Column(db.String(10), default="0")   # percent, as string


class StaticFinancials(db.Model):
    __tablename__ = "static_financials"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    monthly_salary_inflow = db.Column(db.String(20), default="0")
    monthly_expense_budget_outflow = db.Column(db.String(20), default="0")
    normal_monthly_expenses = db.Column(db.String(20), default="0")
    insurance_deductibles = db.Column(db.JSON, default=list)   # list of strings


class ReportRun(db.Model):
    __tablename__ = "report_run"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    period = db.Column(db.String(20))                  # e.g. "2026 Q3"
    entered_values = db.Column(db.JSON, default=dict)  # dynamic balances keyed by field
    computed_values = db.Column(db.JSON, default=dict) # snapshot of SACS+TCC results
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditEvent(db.Model):
    __tablename__ = "audit_event"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    action = db.Column(db.String(60), nullable=False)
    entity = db.Column(db.String(120))
    detail = db.Column(db.String(400))
    ip = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class ProviderCredential(db.Model):
    """Phase 2 seam (designed, unused in V1). Encrypted, read-only provider tokens.

    Present so the integration boundary exists from day one; no V1 code path writes
    to it. It is intentionally NOT a stub — it is a real, migration-ready table.
    """
    __tablename__ = "provider_credential"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    provider = db.Column(db.String(40), nullable=False)   # plaid|zillow|precisefp|schwab...
    base_url = db.Column(db.String(300))                  # provider API base (sandbox or live)
    encrypted_token = db.Column(db.Text)                  # vault-encrypted JSON of secrets
    scope = db.Column(db.String(40), default="read_only")
    status = db.Column(db.String(20), default="inactive") # inactive|active
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UsageRecord(db.Model):
    """Metered usage for billing (spec 16, Phase 4). Cost is charged at cost + markup."""
    __tablename__ = "usage_record"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    kind = db.Column(db.String(40), nullable=False)   # report_generate|provider_call|ai_call|email_send
    quantity = db.Column(db.Integer, default=1)
    unit_cost = db.Column(db.String(20), default="0")  # base cost (USD) as string
    detail = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Outbox(db.Model):
    """Every outbound email (spec 8.10). Real SMTP send when configured; always recorded."""
    __tablename__ = "outbox"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"))
    to_email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(300))
    body = db.Column(db.Text)
    attachment_name = db.Column(db.String(200))
    status = db.Column(db.String(20), default="queued")  # queued|sent|failed
    error = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)


class OnboardingInvite(db.Model):
    """Client-facing onboarding link (spec 8.8, Phase 3). Tokenised, no login."""
    __tablename__ = "onboarding_invite"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    email = db.Column(db.String(200))
    token = db.Column(db.String(64), unique=True, index=True, nullable=False)
    status = db.Column(db.String(20), default="sent")   # sent|completed|escalated
    reminders_sent = db.Column(db.Integer, default=0)
    data = db.Column(db.JSON, default=dict)             # submitted onboarding answers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reminder_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)


class ExpenseSubmission(db.Model):
    """Client-facing expense worksheet (spec 8.9, Phase 3). Tokenised, staff-approved."""
    __tablename__ = "expense_submission"
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    token = db.Column(db.String(64), unique=True, index=True, nullable=False)
    status = db.Column(db.String(20), default="sent")   # sent|submitted|approved
    data = db.Column(db.JSON, default=dict)             # {salary, expense_budget, expenses, deductibles}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
