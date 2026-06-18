"""Render the demo client's SACS & TCC PDFs (the real portal output) to Downloads."""
import os
from app import create_app
from app.models import Client
from app import reporting

ENTERED = {
    "private_reserve_balance": "75000", "investment_account_balance": "15000",
    "account:1": "11000", "account:2": "15000", "account_cash:2": "316",
    "account:3": "9000", "account:4": "50000", "account_cash:4": "1200",
    "trust": "450000", "liability:1": "200000",
}
OUT = r"C:\Users\tbeng\Downloads"

app = create_app()
with app.app_context():
    c = Client.query.filter_by(display_name="The Sample Household").first()
    result, ctx = reporting.build(c, ENTERED)
    sacs, tcc = reporting.render(c, result, ctx, "2026 Q2")
    with open(os.path.join(OUT, "AW_sample_SACS.pdf"), "wb") as f:
        f.write(sacs)
    with open(os.path.join(OUT, "AW_sample_TCC.pdf"), "wb") as f:
        f.write(tcc)
    print("Grand total:", result.tcc.grand_total_net_worth,
          "| Excess:", result.sacs.excess_to_reserve)
    print("wrote AW_sample_SACS.pdf and AW_sample_TCC.pdf to", OUT)
