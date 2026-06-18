"""Audit logging (spec 13.2): immutable record of logins, PII views, generations."""
from __future__ import annotations

from flask import request

from .extensions import db
from .models import AuditEvent
from .security import current_user


def log_event(action, entity=None, detail=None):
    u = current_user()
    ev = AuditEvent(
        tenant_id=u.tenant_id if u else None,
        user_id=u.id if u else None,
        action=action, entity=entity, detail=detail,
        ip=request.remote_addr if request else None,
    )
    db.session.add(ev)
    db.session.commit()
