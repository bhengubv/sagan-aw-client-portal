"""Report distribution (spec 8.5, 8.10): email reports, auto-save to Dropbox, export to Canva."""
from __future__ import annotations

from .models import ProviderCredential
from .vault import get_vault
from . import reporting
from .providers.registry import build_provider
from .mailer import send_email


class DistributionError(Exception):
    pass


def _render(run):
    result, ctx = reporting.build(run.client, run.entered_values)
    date_str = run.period or run.created_at.date().isoformat()
    return reporting.render(run.client, result, ctx, date_str)


def _slug(s):
    return "".join(ch if ch.isalnum() else "_" for ch in (s or "client")).strip("_")


def email_report(run, to_email):
    sacs, tcc = _render(run)
    p = run.period or "report"
    return [
        send_email(run.client.tenant_id, to_email, f"Your {p} cash-flow (SACS) report",
                   "Please find your quarterly cash-flow report attached.",
                   attachment=sacs, attachment_name=f"SACS_{_slug(run.client.display_name)}_{p}.pdf"),
        send_email(run.client.tenant_id, to_email, f"Your {p} net-worth (TCC) report",
                   "Please find your quarterly net-worth report attached.",
                   attachment=tcc, attachment_name=f"TCC_{_slug(run.client.display_name)}_{p}.pdf"),
    ]


def _output_provider(tenant_id, name):
    cred = ProviderCredential.query.filter_by(tenant_id=tenant_id, provider=name,
                                              status="active").first()
    if not cred:
        raise DistributionError(f"{name} is not connected for this firm")
    return build_provider(cred, get_vault())


def save_to_dropbox(run):
    dbx = _output_provider(run.client.tenant_id, "dropbox")
    sacs, tcc = _render(run)
    base = f"/{_slug(run.client.display_name)}/{run.period}"
    return [dbx.upload(f"{base}/SACS.pdf", sacs), dbx.upload(f"{base}/TCC.pdf", tcc)]


def export_to_canva(run, title=None):
    canva = _output_provider(run.client.tenant_id, "canva")
    _, tcc = _render(run)
    title = title or f"{run.client.display_name} — {run.period}"
    return canva.create_design(title, tcc)
