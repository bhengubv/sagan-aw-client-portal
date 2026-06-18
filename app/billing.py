"""Usage metering & billing (spec 16, Phase 4).

Records metered events and totals them at cost + 20% markup. Real records, real maths.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from .extensions import db
from .models import UsageRecord

# Base (cost) prices in USD per unit. Charged to the tenant at cost + markup.
UNIT_COSTS = {
    "report_generate": Decimal("0.50"),
    "provider_call": Decimal("0.02"),
    "ai_call": Decimal("0.10"),
    "email_send": Decimal("0.01"),
}
MARKUP = Decimal("1.20")  # cost + 20% (spec 16)
CENTS = Decimal("0.01")


def record_usage(tenant_id, kind, quantity=1, detail=None):
    """Record a metered event. Safe no-op if tenant_id is missing."""
    if not tenant_id:
        return None
    unit = UNIT_COSTS.get(kind, Decimal("0"))
    rec = UsageRecord(tenant_id=tenant_id, kind=kind, quantity=quantity,
                      unit_cost=str(unit), detail=detail)
    db.session.add(rec)
    db.session.commit()
    return rec


def tenant_summary(tenant_id):
    """Aggregate a tenant's usage into a billable summary."""
    recs = UsageRecord.query.filter_by(tenant_id=tenant_id).all()
    by_kind, base_total = {}, Decimal("0")
    for r in recs:
        cost = Decimal(r.quantity) * Decimal(r.unit_cost or "0")
        base_total += cost
        b = by_kind.setdefault(r.kind, {"qty": 0, "base": Decimal("0")})
        b["qty"] += r.quantity
        b["base"] += cost
    for b in by_kind.values():
        b["base"] = b["base"].quantize(CENTS, ROUND_HALF_UP)
        b["billed"] = (b["base"] * MARKUP).quantize(CENTS, ROUND_HALF_UP)
    return {
        "by_kind": by_kind,
        "base_total": base_total.quantize(CENTS, ROUND_HALF_UP),
        "billed_total": (base_total * MARKUP).quantize(CENTS, ROUND_HALF_UP),
        "markup_pct": 20,
    }
