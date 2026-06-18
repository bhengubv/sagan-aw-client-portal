"""Anomaly flagging (spec 8.8, 12).

Pure logic: compare this quarter's entered balances to the previous quarter's and flag
implausible moves for human review. Never blocks or alters the numbers.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from ..calc import money

DEFAULT_THRESHOLD = Decimal("0.5")  # 50% move


def detect(prev_entered: dict, curr_entered: dict, threshold=DEFAULT_THRESHOLD, labels=None):
    """Return a list of flags: {key, label, prev, curr, pct, reason}."""
    threshold = Decimal(str(threshold))
    labels = labels or {}
    flags = []
    for key, raw_cur in (curr_entered or {}).items():
        if key not in (prev_entered or {}):
            continue
        try:
            p = money(prev_entered[key])
            c = money(raw_cur)
        except (InvalidOperation, ValueError, TypeError):
            continue
        label = labels.get(key, key)
        if p == 0:
            if c != 0:
                flags.append({"key": key, "label": label, "prev": str(p), "curr": str(c),
                              "pct": None, "reason": "was zero, now non-zero"})
            continue
        change = abs((c - p) / p)
        if change >= threshold:
            pct = float(change * 100)
            direction = "up" if c > p else "down"
            flags.append({"key": key, "label": label, "prev": str(p), "curr": str(c),
                          "pct": pct, "reason": f"moved {direction} {pct:.0f}% vs last quarter"})
    return flags
