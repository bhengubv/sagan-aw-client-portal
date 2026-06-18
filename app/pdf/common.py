"""Shared PDF drawing helpers (spec 10).

Fixed-coordinate drawing so layouts never reflow with value length or account count.
Brand colour is configurable; defaults to the firm's blue.
"""
from __future__ import annotations

from decimal import Decimal

from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

PAGE_W, PAGE_H = letter

BRAND = HexColor("#2E5E8C")
GREEN = HexColor("#2E7D32")
RED = HexColor("#C62828")
BLUE = HexColor("#1565C0")
GREY = HexColor("#6B7280")
LIGHTGREY = HexColor("#E5E7EB")
BOXGREY = HexColor("#D7DEE6")


def fmt_money(value) -> str:
    """Format a Decimal/number as $ with thousands separators; drop .00 when whole."""
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    neg = d < 0
    d = abs(d)
    whole = d == d.to_integral_value()
    s = f"{d:,.0f}" if whole else f"{d:,.2f}"
    return ("-$" if neg else "$") + s


def header(c, title, client_name, date_str):
    """Common report header: title bar + client name (left) and date (right)."""
    c.setFillColor(BRAND)
    c.rect(0, PAGE_H - 0.9 * inch, PAGE_W, 0.9 * inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.6 * inch, PAGE_H - 0.58 * inch, title)
    c.setFont("Helvetica", 10)
    c.drawString(0.6 * inch, PAGE_H - 0.78 * inch, client_name or "")
    c.drawRightString(PAGE_W - 0.6 * inch, PAGE_H - 0.78 * inch, date_str or "")


def footer(c, page_label=""):
    c.setFillColor(GREY)
    c.setFont("Helvetica", 7.5)
    c.drawString(0.6 * inch, 0.4 * inch, "CONFIDENTIAL — AW Client Report Portal")
    if page_label:
        c.drawRightString(PAGE_W - 0.6 * inch, 0.4 * inch, page_label)


def bubble(c, cx, cy, r, fill, title, lines, title_color=white, text_color=white):
    """A filled circle with a bold title and small detail lines, centred."""
    c.setFillColor(fill)
    c.circle(cx, cy, r, fill=1, stroke=0)
    c.setFillColor(title_color)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(cx, cy + r * 0.45, title)
    c.setFillColor(text_color)
    c.setFont("Helvetica", 7.5)
    y = cy + r * 0.18
    for ln in lines:
        c.drawCentredString(cx, y, ln)
        y -= 10


def total_box(c, x, y, w, h, label, value, fill=BOXGREY):
    """A grey summary box: small label on top, bold value below."""
    c.setFillColor(fill)
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.setStrokeColor(GREY)
    c.setLineWidth(0.5)
    c.rect(x, y, w, h, fill=0, stroke=1)
    c.setFillColor(black)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(x + w / 2, y + h - 13, label)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x + w / 2, y + 7, value)


def arrow(c, x1, y1, x2, y2, color=GREY, label=None, width=1.5):
    """A simple line with an arrowhead from (x1,y1) to (x2,y2)."""
    import math
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 7
    c.line(x2, y2, x2 - size * math.cos(ang - 0.4), y2 - size * math.sin(ang - 0.4))
    c.line(x2, y2, x2 - size * math.cos(ang + 0.4), y2 - size * math.sin(ang + 0.4))
    if label:
        c.setFont("Helvetica", 7.5)
        c.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 4, label)
