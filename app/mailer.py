"""Email delivery (spec 8.10).

Every outbound message is recorded in the Outbox (viewable in-app), then sent via SMTP
when SMTP_HOST is configured. Without SMTP it is marked 'recorded' — functional and
auditable without a live mail server. Real SMTP send when configured.
"""
from __future__ import annotations

import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

from flask import current_app

from .extensions import db
from .models import Outbox


def send_email(tenant_id, to_email, subject, body, attachment=None, attachment_name=None):
    """Record + (when configured) send. Returns the Outbox row."""
    row = Outbox(tenant_id=tenant_id, to_email=to_email, subject=subject, body=body,
                 attachment_name=attachment_name, status="queued")
    db.session.add(row)
    db.session.commit()

    host = current_app.config.get("SMTP_HOST")
    try:
        if not host:
            row.status = "recorded"            # no SMTP: captured in Outbox
            row.sent_at = datetime.utcnow()
        else:
            em = EmailMessage()
            em["From"] = current_app.config.get("SMTP_FROM", "no-reply@awportal.local")
            em["To"] = to_email
            em["Subject"] = subject
            em.set_content(body)
            if attachment is not None:
                em.add_attachment(attachment, maintype="application", subtype="pdf",
                                  filename=attachment_name or "report.pdf")
            port = int(current_app.config.get("SMTP_PORT", 587))
            with smtplib.SMTP(host, port, timeout=20) as s:
                if current_app.config.get("SMTP_STARTTLS", True):
                    s.starttls(context=ssl.create_default_context())
                user = current_app.config.get("SMTP_USER")
                if user:
                    s.login(user, current_app.config.get("SMTP_PASSWORD"))
                s.send_message(em)
            row.status = "sent"
            row.sent_at = datetime.utcnow()
        db.session.commit()
    except Exception as e:  # noqa: BLE001  (any send failure is recorded, not raised)
        row.status = "failed"
        row.error = str(e)[:300]
        db.session.commit()
    from . import billing
    billing.record_usage(tenant_id, "email_send", detail=subject[:60] if subject else None)
    return row
