"""PDF generation: valid PDFs whose text contains the right labels and numbers (spec 8.4, 10)."""
import fitz  # PyMuPDF

from app.calc import (Account, Owner, Category, SacsInput, TccInput,
                      compute_sacs, compute_tcc)
from app.pdf import render_sacs, render_tcc


def _text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(p.get_text() for p in doc), doc.page_count


def test_sacs_pdf_is_valid_and_has_values():
    sacs = compute_sacs(SacsInput(inflow=15000, outflow=12000, monthly_expenses=10000,
                                  insurance_deductibles=[1000, 2000, 1000],
                                  private_reserve_balance=75000, investment_account_balance=15000))
    pdf = render_sacs("The Sample Household", "2026 Q3", sacs)
    assert pdf[:4] == b"%PDF"
    text, pages = _text(pdf)
    assert pages == 2
    assert "INFLOW" in text and "OUTFLOW" in text and "PRIVATE RESERVE" in text
    assert "The Sample Household" in text
    assert "$15,000" in text
    assert "$64,000" in text  # reserve target 6*10000 + 4000


def test_tcc_pdf_is_valid_and_has_totals():
    accounts = [
        Account(Owner.C1, Category.RETIREMENT, "IRA", 11000, acct_last4="1111"),
        Account(Owner.C1, Category.RETIREMENT, "Roth IRA", 15000, acct_last4="2222"),
        Account(Owner.JOINT, Category.NON_RETIREMENT, "Brokerage", 50000, acct_last4="4444"),
    ]
    tcc = compute_tcc(TccInput(accounts=accounts, trust_value=450000))
    persons = [{"role": "C1", "name": "Jordan", "age": 50, "dob": "1975-04-01", "ssn_last4": "1234"}]
    c1 = [{"type": "IRA", "acct_last4": "1111", "balance": 11000},
          {"type": "Roth IRA", "acct_last4": "2222", "balance": 15000}]
    nonret = [{"type": "Brokerage", "acct_last4": "4444", "balance": 50000}]
    pdf = render_tcc("The Sample Household", "2026 Q3", tcc, persons, c1, [], nonret,
                     [{"type": "Mortgage", "interest_rate": "4.5", "balance": 200000}],
                     "123 Sample St")
    assert pdf[:4] == b"%PDF"
    text, pages = _text(pdf)
    assert pages == 1
    assert "GRAND TOTAL NET WORTH" in text
    assert "$526,000" in text
    assert "LIABILITIES" in text
    assert "Jordan" in text


def test_tcc_handles_six_bubbles_per_spouse_without_error():
    accounts = [Account(Owner.C1, Category.RETIREMENT, f"Acct{i}", 1000, acct_last4=f"{i}{i}{i}{i}")
                for i in range(6)]
    accounts += [Account(Owner.C2, Category.RETIREMENT, f"B{i}", 2000) for i in range(6)]
    tcc = compute_tcc(TccInput(accounts=accounts))
    c1 = [{"type": f"Acct{i}", "acct_last4": f"{i}{i}{i}{i}", "balance": 1000} for i in range(6)]
    c2 = [{"type": f"B{i}", "acct_last4": "", "balance": 2000} for i in range(6)]
    pdf = render_tcc("Big Family", "2026 Q3", tcc,
                     [{"role": "C1", "name": "A", "age": 40, "dob": None, "ssn_last4": None},
                      {"role": "C2", "name": "B", "age": 38, "dob": None, "ssn_last4": None}],
                     c1, c2, [], [], None)
    assert pdf[:4] == b"%PDF"
    text, _ = _text(pdf)
    assert "$6,000" in text   # C1 total
    assert "$12,000" in text  # C2 total
