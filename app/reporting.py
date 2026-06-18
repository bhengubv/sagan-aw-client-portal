"""Reporting service (spec 8.2-8.5): turn a client profile + entered balances into
computed results and PDFs. Pure-ish glue around the calc engine and PDF renderers;
no Flask request objects here so it stays unit-testable.
"""
from __future__ import annotations

from .calc import (
    Account as CalcAccount, Liability as CalcLiability,
    Owner, Category, SacsInput, TccInput, compute_report, money,
)
from .pdf import render_sacs, render_tcc


# ---- dynamic field discovery (drives the entry form + completeness check) ----
def required_fields(client):
    """Return ordered field specs the team must enter for a report.

    Each spec: {key, label, section, last_value}. last_value comes from the most
    recent ReportRun so the form can offer 'use last value' (spec 8.2).
    """
    last = client.last_report.entered_values if client.last_report else {}
    fields = []

    def add(key, label, section):
        fields.append({"key": key, "label": label, "section": section,
                       "last_value": last.get(key, "")})

    # SACS dynamic
    add("private_reserve_balance", "Private Reserve Balance", "SACS")
    add("investment_account_balance", "Investment Account (Schwab) Balance", "SACS")

    # TCC dynamic — one per account, plus cash for investment accounts
    for a in client.accounts:
        add(f"account:{a.id}", f"{a.type} ({a.owner}) Balance", "TCC")
        if a.has_cash_balance:
            add(f"account_cash:{a.id}", f"{a.type} ({a.owner}) Cash Balance", "TCC")
    if client.trust:
        add("trust", "Home / Trust Value (Zillow)", "TCC")
    for li in client.liabilities:
        add(f"liability:{li.id}", f"{li.type} Balance", "TCC")
    return fields


def missing_fields(client, entered):
    """Required keys with no value — a report cannot be generated while non-empty (spec 8.2)."""
    missing = []
    for f in required_fields(client):
        v = entered.get(f["key"])
        if v is None or str(v).strip() == "":
            missing.append(f)
    return missing


# ---- build calc inputs + render data ----
def _accounts_for(client, entered):
    calc_accounts, c1, c2, nonret = [], [], [], []
    for a in client.accounts:
        bal = entered.get(f"account:{a.id}", "0") or "0"
        cash = entered.get(f"account_cash:{a.id}", "0") or "0"
        calc_accounts.append(CalcAccount(
            owner=Owner(a.owner), category=Category(a.category), type=a.type,
            balance=bal, cash_balance=cash, acct_last4=a.acct_last4 or "",
        ))
        disp = {"type": a.type, "acct_last4": a.acct_last4 or "",
                "balance": money(bal), "cash_balance": money(cash)}
        if a.category == Category.RETIREMENT.value:
            (c1 if a.owner == Owner.C1.value else c2).append(disp)
        else:
            nonret.append(disp)
    return calc_accounts, c1, c2, nonret


def build(client, entered):
    """Return (report_result, render_ctx). Raises calc ValidationError on bad input."""
    s = client.static
    sacs_input = SacsInput(
        inflow=(s.monthly_salary_inflow if s else 0) or 0,
        outflow=(s.monthly_expense_budget_outflow if s else 0) or 0,
        monthly_expenses=(s.normal_monthly_expenses if s else 0) or 0,
        insurance_deductibles=(s.insurance_deductibles if s and s.insurance_deductibles else []),
        private_reserve_balance=entered.get("private_reserve_balance", "0") or "0",
        investment_account_balance=entered.get("investment_account_balance", "0") or "0",
    )
    calc_accounts, c1, c2, nonret = _accounts_for(client, entered)
    calc_liabs = [CalcLiability(type=li.type, interest_rate=li.interest_rate or "0",
                               balance=entered.get(f"liability:{li.id}", "0") or "0")
                  for li in client.liabilities]
    trust_val = entered.get("trust", "0") or "0" if client.trust else "0"
    tcc_input = TccInput(accounts=calc_accounts, trust_value=trust_val, liabilities=calc_liabs)

    result = compute_report(sacs_input, tcc_input)

    persons = [{"role": p.role, "name": p.name, "age": p.age,
                "dob": p.dob.isoformat() if p.dob else None, "ssn_last4": p.ssn_last4}
               for p in client.persons]
    liab_disp = [{"type": li.type, "interest_rate": li.interest_rate,
                  "balance": money(entered.get(f"liability:{li.id}", "0") or "0")}
                 for li in client.liabilities]
    ctx = {
        "persons": persons, "c1_accounts": c1, "c2_accounts": c2,
        "non_ret_accounts": nonret, "liabilities": liab_disp,
        "trust_address": client.trust.property_address if client.trust else None,
    }
    return result, ctx


def serialize(result):
    """JSON-safe snapshot of computed values for ReportRun.computed_values."""
    def d(x):
        return str(x)
    s, t = result.sacs, result.tcc
    return {
        "sacs": {"inflow": d(s.inflow), "outflow": d(s.outflow),
                 "excess_to_reserve": d(s.excess_to_reserve),
                 "reserve_target": d(s.reserve_target), "floor": d(s.floor),
                 "private_reserve_balance": d(s.private_reserve_balance),
                 "investment_account_balance": d(s.investment_account_balance)},
        "tcc": {"c1_retirement_total": d(t.c1_retirement_total),
                "c2_retirement_total": d(t.c2_retirement_total),
                "non_retirement_total": d(t.non_retirement_total),
                "trust_value": d(t.trust_value),
                "grand_total_net_worth": d(t.grand_total_net_worth),
                "liabilities_total": d(t.liabilities_total)},
    }


def render(client, result, ctx, date_str):
    sacs_pdf = render_sacs(client.display_name, date_str, result.sacs)
    tcc_pdf = render_tcc(client.display_name, date_str, result.tcc,
                         ctx["persons"], ctx["c1_accounts"], ctx["c2_accounts"],
                         ctx["non_ret_accounts"], ctx["liabilities"], ctx["trust_address"])
    return sacs_pdf, tcc_pdf
