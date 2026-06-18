"""SACS (Simple Automated Cash Flow) PDF (spec 8.4, 10).

Page 1: Inflow -> Outflow -> Private Reserve bubble diagram.
Page 2: Private Reserve balance, investment (Schwab) balance, savings target.
Layout is fixed; numbers drop into set positions.
"""
from __future__ import annotations

import io

from reportlab.lib.colors import black, white
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from .common import (
    PAGE_W, PAGE_H, GREEN, RED, BLUE, GREY, fmt_money,
    header, footer, bubble, total_box, arrow,
)

TITLE = "Simple Automated CashFlow System (SACS)"


def render_sacs(client_name: str, date_str: str, sacs) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))

    # ---- Page 1: cash-flow diagram ----
    header(c, TITLE, client_name, date_str)
    cy = PAGE_H - 3.2 * inch
    left_x = 2.0 * inch
    right_x = PAGE_W - 2.0 * inch
    r = 0.95 * inch

    bubble(c, left_x, cy, r, GREEN, "INFLOW",
           [fmt_money(sacs.inflow), "per month"])
    bubble(c, right_x, cy, r, RED, "OUTFLOW",
           [fmt_money(sacs.outflow), "per month"])
    arrow(c, left_x + r, cy, right_x - r, cy, color=RED,
          label="Automated transfer  " + fmt_money(sacs.outflow))

    # Private reserve below, fed by the excess
    pr_y = cy - 2.4 * inch
    bubble(c, (left_x + right_x) / 2, pr_y, r, BLUE, "PRIVATE RESERVE",
           ["Excess", fmt_money(sacs.excess_to_reserve)])
    arrow(c, left_x, cy - r, (left_x + right_x) / 2 - r, pr_y + r * 0.6,
          color=BLUE, label="Excess = Inflow - Outflow", width=1.5)

    c.setFillColor(GREY)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(PAGE_W / 2, pr_y - 1.4 * inch, "MONTHLY CASHFLOW")
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, pr_y - 1.6 * inch,
                        f"Floor maintained per account: {fmt_money(sacs.floor)}")
    footer(c, "SACS — Page 1 of 2")
    c.showPage()

    # ---- Page 2: reserve detail ----
    header(c, TITLE + " — Reserve Detail", client_name, date_str)
    bw, bh = 2.6 * inch, 1.0 * inch
    gap = 0.5 * inch
    top = PAGE_H - 3.0 * inch
    x0 = (PAGE_W - (2 * bw + gap)) / 2
    total_box(c, x0, top, bw, bh, "Private Reserve Balance",
              fmt_money(sacs.private_reserve_balance))
    total_box(c, x0 + bw + gap, top, bw, bh, "Investment Account (Schwab)",
              fmt_money(sacs.investment_account_balance))
    total_box(c, (PAGE_W - bw) / 2, top - bh - gap, bw, bh,
              "Private Reserve Target", fmt_money(sacs.reserve_target))

    c.setFillColor(black)
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawCentredString(PAGE_W / 2, top - bh - gap - 0.4 * inch,
                        "Target = (6 x monthly expenses) + all insurance deductibles")
    footer(c, "SACS — Page 2 of 2")
    c.showPage()

    c.save()
    return buf.getvalue()
