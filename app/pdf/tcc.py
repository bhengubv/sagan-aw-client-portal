"""TCC (Total Client Chart) net-worth PDF (spec 8.4, 9.2, 10).

Landscape to match the wide 'circle chart'. Client info bubbles on top; retirement
accounts per spouse with subtotals; trust in the centre; non-retirement row; grand
total; liabilities shown SEPARATELY (never subtracted). Variable bubble counts are
laid out on a fixed grid so nothing overflows.
"""
from __future__ import annotations

import io
from math import ceil

from reportlab.lib.colors import black, white, HexColor
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from .common import (
    GREEN, BLUE, GREY, BRAND, BOXGREY, RED,
    fmt_money, bubble, total_box,
)

# Landscape letter
W, H = 792.0, 612.0
NONRET = HexColor("#37618E")
RETIRE = HexColor("#2E7D32")


def _header(c, client_name, date_str):
    c.setFillColor(BRAND)
    c.rect(0, H - 0.8 * inch, W, 0.8 * inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(0.6 * inch, H - 0.52 * inch, "Total Client Chart (TCC)")
    c.setFont("Helvetica", 9)
    c.drawString(0.6 * inch, H - 0.7 * inch, client_name or "")
    c.drawRightString(W - 0.6 * inch, H - 0.7 * inch, date_str or "")


def _grid(c, cx, top_y, accounts, fill, cols=3, r=0.40 * inch, hgap=0.18 * inch, vgap=0.34 * inch):
    """Draw account bubbles in a grid centred horizontally on cx. Returns bottom y."""
    if not accounts:
        return top_y
    ncols = min(cols, len(accounts))
    grid_w = ncols * 2 * r + (ncols - 1) * hgap
    start_x = cx - grid_w / 2 + r
    rows = ceil(len(accounts) / cols)
    for i, a in enumerate(accounts):
        row, col = divmod(i, cols)
        bx = start_x + col * (2 * r + hgap)
        by = top_y - row * (2 * r + vgap) - r
        lines = []
        if a.get("acct_last4"):
            lines.append("x" + str(a["acct_last4"]))
        lines.append(fmt_money(a["balance"]))
        if a.get("cash_balance") and str(a["cash_balance"]) not in ("0", "0.00"):
            lines.append("cash " + fmt_money(a["cash_balance"]))
        bubble(c, bx, by, r, fill, str(a["type"])[:16], lines)
    # True bottom of the lowest row of bubbles.
    return top_y - (rows - 1) * (2 * r + vgap) - 2 * r


def render_tcc(client_name, date_str, tcc, persons, c1_accounts, c2_accounts,
               non_ret_accounts, liabilities, trust_address=None) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))
    _header(c, client_name, date_str)

    # Client info bubbles (green) top
    info_y = H - 1.7 * inch
    centers = {"C1": 2.6 * inch, "C2": 8.4 * inch}
    for p in persons:
        cx = centers.get(p.get("role"), W / 2)
        lines = []
        if p.get("age") is not None:
            lines.append(f"Age {p['age']}")
        if p.get("dob"):
            lines.append(str(p["dob"]))
        if p.get("ssn_last4"):
            lines.append("SSN x" + str(p["ssn_last4"]))
        bubble(c, cx, info_y, 0.7 * inch, GREEN, str(p.get("name", ""))[:16], lines)

    # Section label
    c.setFillColor(GREY)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W / 2, H - 2.5 * inch, "RETIREMENT ACCOUNTS")

    # Retirement grids per spouse
    ret_top = H - 2.8 * inch
    b1 = _grid(c, centers["C1"], ret_top, c1_accounts, RETIRE)
    b2 = _grid(c, centers["C2"], ret_top, c2_accounts, RETIRE)
    grid_bottom = min(b1, b2)

    # Retirement subtotals — placed BELOW the bubbles (box top = bubble bottom - gap)
    bw, bh = 2.2 * inch, 0.7 * inch
    box_y = grid_bottom - 0.20 * inch - bh
    total_box(c, centers["C1"] - bw / 2, box_y, bw, bh,
              "Client 1 Retirement Total", fmt_money(tcc.c1_retirement_total))
    total_box(c, centers["C2"] - bw / 2, box_y, bw, bh,
              "Client 2 Retirement Total", fmt_money(tcc.c2_retirement_total))

    # Trust (centre)
    total_box(c, W / 2 - bw / 2, info_y - 0.35 * inch, bw, bh,
              "Trust" + (f" — {trust_address[:22]}" if trust_address else ""),
              fmt_money(tcc.trust_value))

    # Non-retirement row
    c.setFillColor(GREY)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W / 2, box_y - 0.35 * inch, "NON-RETIREMENT ACCOUNTS")
    nonret_bottom = _grid(c, W / 2, box_y - 0.6 * inch, non_ret_accounts, NONRET, cols=5)
    total_box(c, W / 2 - bw / 2, nonret_bottom - 0.20 * inch - bh, bw, bh,
              "Non-Retirement Total", fmt_money(tcc.non_retirement_total))

    # Grand total (prominent, right)
    gw, gh = 2.6 * inch, 0.9 * inch
    total_box(c, W - gw - 0.6 * inch, 0.7 * inch, gw, gh,
              "GRAND TOTAL NET WORTH", fmt_money(tcc.grand_total_net_worth), fill=HexColor("#CFE3CF"))

    # Liabilities — SEPARATE, never subtracted
    lx, ly = 0.6 * inch, 1.7 * inch
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(lx, ly + 0.15 * inch, "LIABILITIES (shown separately — NOT subtracted)")
    c.setFillColor(black)
    c.setFont("Helvetica", 8)
    yy = ly - 0.05 * inch
    for li in liabilities:
        rate = li.get("interest_rate")
        rate_s = f"  @ {rate}%" if rate not in (None, "", "0") else ""
        c.drawString(lx, yy, f"{li['type']}{rate_s}: {fmt_money(li['balance'])}")
        yy -= 0.2 * inch
    total_box(c, lx, 0.55 * inch, 2.2 * inch, 0.65 * inch,
              "Liabilities Total", fmt_money(tcc.liabilities_total), fill=HexColor("#F3D6D6"))

    from .common import footer as _f
    # footer (landscape coords)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 7.5)
    c.drawString(0.6 * inch, 0.3 * inch, "CONFIDENTIAL — AW Client Report Portal")
    c.drawRightString(W - 0.6 * inch, 0.3 * inch, "TCC")

    c.showPage()
    c.save()
    return buf.getvalue()
