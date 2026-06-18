"""Deterministic calculation engine for SACS (cash-flow) and TCC (net-worth) reports.

This module is PURE: no I/O, no database, no framework. It takes plain values and
returns plain results, so it can be exhaustively unit-tested and reused by any caller
(the web UI today; an API or agent in a later phase).

All business rules trace to the Technical Specification, Section 9.
Money is handled with Decimal to avoid floating-point error.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Iterable

# The $1,000 minimum balance kept in each bank account (constant; never changes).
FLOOR = Decimal("1000")

# Number of months of expenses used in the private-reserve target.
RESERVE_MONTHS = Decimal("6")

TWO_DP = Decimal("0.01")


def money(value) -> Decimal:
    """Coerce int/float/str/Decimal to a 2-dp Decimal. Centralises money parsing."""
    if isinstance(value, Decimal):
        d = value
    else:
        d = Decimal(str(value))
    return d.quantize(TWO_DP, rounding=ROUND_HALF_UP)


def _sum(values: Iterable[Decimal]) -> Decimal:
    total = Decimal("0")
    for v in values:
        total += v
    return total.quantize(TWO_DP, rounding=ROUND_HALF_UP)


class Owner(str, Enum):
    C1 = "C1"        # Client 1 (e.g. high-earning spouse)
    C2 = "C2"        # Client 2 (spouse)
    JOINT = "JOINT"  # Jointly held


class Category(str, Enum):
    RETIREMENT = "retirement"          # 401k, IRA, Roth IRA, pension — cannot be joint
    NON_RETIREMENT = "non_retirement"  # brokerage, joint, options — may be joint


@dataclass
class Account:
    owner: Owner
    category: Category
    type: str                      # e.g. "Roth IRA", "Brokerage"
    balance: Decimal               # total balance (already includes any cash sub-balance)
    cash_balance: Decimal = Decimal("0")  # shown on the report, NOT added again
    acct_last4: str = ""

    def __post_init__(self):
        self.owner = Owner(self.owner)
        self.category = Category(self.category)
        self.balance = money(self.balance)
        self.cash_balance = money(self.cash_balance)


@dataclass
class Liability:
    type: str
    interest_rate: Decimal
    balance: Decimal

    def __post_init__(self):
        self.interest_rate = Decimal(str(self.interest_rate))
        self.balance = money(self.balance)


# --------------------------------------------------------------------------- SACS
@dataclass
class SacsInput:
    inflow: Decimal                       # client take-home pay / month
    outflow: Decimal                      # agreed monthly expense budget (rounded up)
    monthly_expenses: Decimal             # normal monthly expenses (for reserve target)
    insurance_deductibles: list = field(default_factory=list)
    private_reserve_balance: Decimal = Decimal("0")
    investment_account_balance: Decimal = Decimal("0")  # Schwab balance

    def __post_init__(self):
        self.inflow = money(self.inflow)
        self.outflow = money(self.outflow)
        self.monthly_expenses = money(self.monthly_expenses)
        self.insurance_deductibles = [money(d) for d in self.insurance_deductibles]
        self.private_reserve_balance = money(self.private_reserve_balance)
        self.investment_account_balance = money(self.investment_account_balance)


@dataclass
class SacsResult:
    inflow: Decimal
    outflow: Decimal
    excess_to_reserve: Decimal
    reserve_target: Decimal
    floor: Decimal
    private_reserve_balance: Decimal
    investment_account_balance: Decimal


def compute_sacs(data: SacsInput) -> SacsResult:
    """SACS rules (spec 9.1).

    Excess to Private Reserve = Inflow - Outflow
    Private Reserve Target    = (6 x monthly expenses) + sum(insurance deductibles)
    Floor                     = $1,000 (constant)
    """
    excess = money(data.inflow - data.outflow)
    target = money(RESERVE_MONTHS * data.monthly_expenses + _sum(data.insurance_deductibles))
    return SacsResult(
        inflow=data.inflow,
        outflow=data.outflow,
        excess_to_reserve=excess,
        reserve_target=target,
        floor=FLOOR,
        private_reserve_balance=data.private_reserve_balance,
        investment_account_balance=data.investment_account_balance,
    )


# ---------------------------------------------------------------------------- TCC
@dataclass
class TccInput:
    accounts: list = field(default_factory=list)
    trust_value: Decimal = Decimal("0")
    liabilities: list = field(default_factory=list)

    def __post_init__(self):
        self.trust_value = money(self.trust_value)


@dataclass
class TccResult:
    c1_retirement_total: Decimal
    c2_retirement_total: Decimal
    non_retirement_total: Decimal
    trust_value: Decimal
    grand_total_net_worth: Decimal
    liabilities_total: Decimal


class ValidationError(ValueError):
    """Raised when an input violates a hard business rule."""


def validate_accounts(accounts) -> None:
    """Retirement accounts cannot be joint (spec 8.1 / 9.2). Defence in depth."""
    for a in accounts:
        if a.category == Category.RETIREMENT and a.owner == Owner.JOINT:
            raise ValidationError(
                f"Retirement account '{a.type}' cannot be JOINT-owned."
            )


def compute_tcc(data: TccInput) -> TccResult:
    """TCC rules (spec 9.2).

    Client 1 Retirement Total = sum of C1 retirement balances
    Client 2 Retirement Total = sum of C2 retirement balances
    Non-Retirement Total      = sum of all non-retirement balances  (EXCLUDES the trust)
    Grand Total Net Worth     = C1 Retirement + C2 Retirement + Non-Retirement + Trust
    Liabilities Total         = sum of liabilities  (shown SEPARATELY, NOT subtracted)
    Investment balance already includes its cash sub-balance (cash shown, not re-added).
    """
    validate_accounts(data.accounts)

    c1 = _sum(
        a.balance for a in data.accounts
        if a.category == Category.RETIREMENT and a.owner == Owner.C1
    )
    c2 = _sum(
        a.balance for a in data.accounts
        if a.category == Category.RETIREMENT and a.owner == Owner.C2
    )
    non_ret = _sum(
        a.balance for a in data.accounts
        if a.category == Category.NON_RETIREMENT
    )
    grand = money(c1 + c2 + non_ret + data.trust_value)
    liabilities_total = _sum(l.balance for l in data.liabilities)

    return TccResult(
        c1_retirement_total=c1,
        c2_retirement_total=c2,
        non_retirement_total=non_ret,   # deliberately excludes trust
        trust_value=data.trust_value,
        grand_total_net_worth=grand,    # liabilities deliberately NOT subtracted
        liabilities_total=liabilities_total,
    )


# ------------------------------------------------------------------- full report
@dataclass
class ReportResult:
    sacs: SacsResult
    tcc: TccResult


def compute_report(sacs_input: SacsInput, tcc_input: TccInput) -> ReportResult:
    """Compute both reports for a client in one call."""
    return ReportResult(sacs=compute_sacs(sacs_input), tcc=compute_tcc(tcc_input))
