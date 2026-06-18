"""Quarterly report workflow (spec 8.2-8.5 / US2-US4)."""
from __future__ import annotations

from datetime import datetime

from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, abort, Response)

from .extensions import db
from .models import Client, ReportRun
from .security import login_required, current_user
from .audit import log_event
from . import reporting
from . import integrations
from . import distribution
from . import billing
from .agents import anomaly, extraction
from .calc import ValidationError

bp = Blueprint("reports", __name__, url_prefix="/reports")


def _get_client(cid):
    u = current_user()
    c = Client.query.filter_by(id=cid, tenant_id=u.tenant_id).first()
    if not c:
        abort(404)
    return c


def _current_quarter():
    now = datetime.utcnow()
    return f"{now.year} Q{(now.month - 1) // 3 + 1}"


@bp.route("/<int:cid>/new")
@login_required
def new_report(cid):
    c = _get_client(cid)
    fields = reporting.required_fields(c)
    # Pull whatever the configured providers can supply (spec 8.2, 11); rest stays manual.
    fetched, fetch_report = integrations.fetch_for_client(c)
    prefill = {k: fv.value for k, fv in fetched.items()}
    if fetch_report["fetched"]:
        log_event("report_autofetch", "client", f"{c.display_name}:{fetch_report['fetched']} fields")
    return render_template("reports/new.html", c=c, fields=fields, entered=prefill,
                           missing_keys=[], period=_current_quarter(),
                           sources=fetch_report["sources"], stale=fetch_report["stale"],
                           fetch_report=fetch_report)


@bp.route("/<int:cid>/generate", methods=["POST"])
@login_required
def generate(cid):
    c = _get_client(cid)
    fields = reporting.required_fields(c)
    entered = {f["key"]: (request.form.get(f["key"]) or "").strip() for f in fields}
    period = (request.form.get("period") or _current_quarter()).strip()

    missing = reporting.missing_fields(c, entered)
    if missing:
        flash(f"{len(missing)} field(s) still need a value — a report cannot be "
              f"generated until all required fields are filled.", "error")
        return render_template("reports/new.html", c=c, fields=fields, entered=entered,
                               missing_keys=[m["key"] for m in missing], period=period)

    try:
        result, ctx = reporting.build(c, entered)
    except ValidationError as e:
        flash(str(e), "error")
        return render_template("reports/new.html", c=c, fields=fields, entered=entered,
                               missing_keys=[], period=period)

    run = ReportRun(client_id=c.id, period=period, entered_values=entered,
                    computed_values=reporting.serialize(result),
                    created_by=current_user().id)
    db.session.add(run)
    db.session.commit()
    log_event("report_generate", "client", f"{c.display_name}:{period}")
    billing.record_usage(c.tenant_id, "report_generate", detail=f"{c.display_name}:{period}")
    return redirect(url_for("reports.review", rid=run.id))


@bp.route("/run/<int:rid>")
@login_required
def review(rid):
    run = _get_run(rid)
    prior = (ReportRun.query
             .filter(ReportRun.client_id == run.client_id, ReportRun.id < run.id)
             .order_by(ReportRun.id.desc()).first())
    flags = []
    if prior:
        labels = {f["key"]: f["label"] for f in reporting.required_fields(run.client)}
        flags = anomaly.detect(prior.entered_values or {}, run.entered_values or {}, labels=labels)
    return render_template("reports/review.html", run=run, c=run.client,
                           cv=run.computed_values, flags=flags)


@bp.route("/<int:cid>/extract", methods=["POST"])
@login_required
def extract(cid):
    """Upload a statement; the extraction agent proposes balances into the form (spec 8.8)."""
    c = _get_client(cid)
    fields = reporting.required_fields(c)
    entered = {fl["key"]: (request.form.get(fl["key"]) or "").strip() for fl in fields}
    f = request.files.get("statement")
    if not f or not f.filename:
        flash("Choose a statement file to extract from.", "warn")
    else:
        text = extraction.extract_text(f.read(), f.filename)
        accounts = [{"field_key": f"account:{a.id}", "label": a.type,
                     "last4": a.acct_last4, "type": a.type} for a in c.accounts]
        proposals, method = extraction.propose(text, accounts)
        applied = 0
        for p in proposals:
            if not entered.get(p["field_key"]):
                entered[p["field_key"]] = p["value"]
                applied += 1
        if method == "llm":
            billing.record_usage(c.tenant_id, "ai_call", detail="statement extraction")
        log_event("statement_extract", "client", f"{c.display_name}:{applied} via {method}")
        flash(f"Extracted {applied} balance(s) from the statement ({method}). "
              f"Review and override as needed before generating.", "ok")
    return render_template("reports/new.html", c=c, fields=fields, entered=entered,
                           missing_keys=[], period=_current_quarter(),
                           sources={}, stale=[], fetch_report=None)


@bp.route("/run/<int:rid>/email", methods=["POST"])
@login_required
def email_report(rid):
    run = _get_run(rid)
    to = (request.form.get("to_email") or "").strip()
    if not to:
        flash("Enter a recipient email.", "error")
    else:
        distribution.email_report(run, to)
        log_event("report_email", "client", f"{run.client.display_name}->{to}")
        flash(f"Report emailed to {to} (view it in Staff → Inbox / Outbox).", "ok")
    return redirect(url_for("reports.review", rid=rid))


@bp.route("/run/<int:rid>/dropbox", methods=["POST"])
@login_required
def dropbox_save(rid):
    run = _get_run(rid)
    try:
        res = distribution.save_to_dropbox(run)
        log_event("report_dropbox", "client", run.client.display_name)
        flash(f"Saved {len(res)} file(s) to Dropbox.", "ok")
    except distribution.DistributionError as e:
        flash(f"{e} — connect it under Settings → Data providers.", "error")
    return redirect(url_for("reports.review", rid=rid))


@bp.route("/run/<int:rid>/canva", methods=["POST"])
@login_required
def canva_export(rid):
    run = _get_run(rid)
    try:
        res = distribution.export_to_canva(run)
        edit = (res.get("design") or {}).get("urls", {}).get("edit_url", "")
        log_event("report_canva", "client", run.client.display_name)
        flash(f"Exported to Canva. Edit: {edit}", "ok")
    except distribution.DistributionError as e:
        flash(f"{e} — connect it under Settings → Data providers.", "error")
    return redirect(url_for("reports.review", rid=rid))


def _get_run(rid):
    run = db.session.get(ReportRun, rid)
    if not run or run.client.tenant_id != current_user().tenant_id:
        abort(404)
    return run


def _pdf_response(data, filename):
    return Response(data, mimetype="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@bp.route("/run/<int:rid>/sacs.pdf")
@login_required
def sacs_pdf(rid):
    run = _get_run(rid)
    result, ctx = reporting.build(run.client, run.entered_values)
    date_str = run.period or run.created_at.date().isoformat()
    sacs, _ = reporting.render(run.client, result, ctx, date_str)
    log_event("report_download", "client", f"{run.client.display_name}:SACS")
    return _pdf_response(sacs, f"SACS_{_slug(run.client.display_name)}_{run.period}.pdf")


@bp.route("/run/<int:rid>/tcc.pdf")
@login_required
def tcc_pdf(rid):
    run = _get_run(rid)
    result, ctx = reporting.build(run.client, run.entered_values)
    date_str = run.period or run.created_at.date().isoformat()
    _, tcc = reporting.render(run.client, result, ctx, date_str)
    log_event("report_download", "client", f"{run.client.display_name}:TCC")
    return _pdf_response(tcc, f"TCC_{_slug(run.client.display_name)}_{run.period}.pdf")


@bp.route("/<int:cid>/history")
@login_required
def history(cid):
    c = _get_client(cid)
    return render_template("reports/history.html", c=c, runs=c.reports)


def _slug(s):
    return "".join(ch if ch.isalnum() else "_" for ch in (s or "client")).strip("_")
