"""TCC calculation rules (spec 9.2), including the two emphasised CRITICAL rules."""
from decimal import Decimal

import pytest

from app.calc import (
    Account, Liability, Owner, Category,
    TccInput, compute_tcc, validate_accounts, ValidationError,
)


def _spec_example_accounts():
    # From spec 9.3: IRA $11k + Roth IRA $15k (Client 1) = $26k retirement;
    # brokerage $50k non-retirement; trust (house) $450k.
    return [
        Account(Owner.C1, Category.RETIREMENT, "IRA", 11000),
        Account(Owner.C1, Category.RETIREMENT, "Roth IRA", 15000),
        Account(Owner.JOINT, Category.NON_RETIREMENT, "Brokerage", 50000),
    ]


def test_spec_worked_example_grand_total():
    r = compute_tcc(TccInput(
        accounts=_spec_example_accounts(),
        trust_value=450000,
        liabilities=[Liability("Mortgage", Decimal("4.5"), 200000)],
    ))
    assert r.c1_retirement_total == Decimal("26000.00")
    assert r.non_retirement_total == Decimal("50000.00")
    assert r.trust_value == Decimal("450000.00")
    assert r.grand_total_net_worth == Decimal("526000.00")


def test_CRITICAL_trust_excluded_from_non_retirement_total():
    """Trust must NOT be inside the non-retirement total (only in grand total)."""
    r = compute_tcc(TccInput(accounts=_spec_example_accounts(), trust_value=450000))
    assert r.non_retirement_total == Decimal("50000.00")  # 50k only, not 500k
    assert r.grand_total_net_worth == Decimal("526000.00")


def test_CRITICAL_liabilities_not_subtracted_from_net_worth():
    """Liabilities are shown separately and NEVER subtracted from net worth."""
    without = compute_tcc(TccInput(accounts=_spec_example_accounts(), trust_value=450000))
    with_debt = compute_tcc(TccInput(
        accounts=_spec_example_accounts(), trust_value=450000,
        liabilities=[Liability("Mortgage", Decimal("4.5"), 200000),
                     Liability("Auto", Decimal("6.0"), 30000)],
    ))
    assert with_debt.grand_total_net_worth == without.grand_total_net_worth
    assert with_debt.liabilities_total == Decimal("230000.00")


def test_retirement_split_by_client():
    accounts = [
        Account(Owner.C1, Category.RETIREMENT, "401k", 100000),
        Account(Owner.C1, Category.RETIREMENT, "Roth IRA", 20000),
        Account(Owner.C2, Category.RETIREMENT, "IRA", 55000),
    ]
    r = compute_tcc(TccInput(accounts=accounts))
    assert r.c1_retirement_total == Decimal("120000.00")
    assert r.c2_retirement_total == Decimal("55000.00")


def test_retirement_account_cannot_be_joint():
    bad = [Account(Owner.JOINT, Category.RETIREMENT, "401k", 100000)]
    with pytest.raises(ValidationError):
        compute_tcc(TccInput(accounts=bad))
    with pytest.raises(ValidationError):
        validate_accounts(bad)


def test_non_retirement_can_be_joint_or_solo():
    accounts = [
        Account(Owner.JOINT, Category.NON_RETIREMENT, "Brokerage", 50000),
        Account(Owner.C2, Category.NON_RETIREMENT, "E-Trade options", 12000),
    ]
    r = compute_tcc(TccInput(accounts=accounts))
    assert r.non_retirement_total == Decimal("62000.00")


def test_cash_balance_is_not_added_again():
    # Roth IRA balance 11,162.47 already includes 316.00 cash; total must be 11,162.47.
    accounts = [Account(Owner.C1, Category.RETIREMENT, "Roth IRA",
                        Decimal("11162.47"), cash_balance=Decimal("316.00"))]
    r = compute_tcc(TccInput(accounts=accounts))
    assert r.c1_retirement_total == Decimal("11162.47")


def test_grand_total_with_two_clients_and_trust():
    accounts = [
        Account(Owner.C1, Category.RETIREMENT, "401k", 100000),
        Account(Owner.C2, Category.RETIREMENT, "IRA", 55000),
        Account(Owner.JOINT, Category.NON_RETIREMENT, "Brokerage", 50000),
    ]
    r = compute_tcc(TccInput(accounts=accounts, trust_value=450000))
    # 100k + 55k + 50k + 450k
    assert r.grand_total_net_worth == Decimal("655000.00")


def test_empty_client_is_all_zero():
    r = compute_tcc(TccInput(accounts=[]))
    assert r.c1_retirement_total == Decimal("0.00")
    assert r.grand_total_net_worth == Decimal("0.00")
    assert r.liabilities_total == Decimal("0.00")


def test_variable_bubble_count_six_accounts_per_spouse():
    accounts = [Account(Owner.C1, Category.RETIREMENT, f"Acct{i}", 1000) for i in range(6)]
    accounts += [Account(Owner.C2, Category.RETIREMENT, f"B{i}", 2000) for i in range(6)]
    r = compute_tcc(TccInput(accounts=accounts))
    assert r.c1_retirement_total == Decimal("6000.00")
    assert r.c2_retirement_total == Decimal("12000.00")
