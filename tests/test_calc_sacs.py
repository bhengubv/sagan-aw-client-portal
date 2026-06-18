"""SACS calculation rules (spec 9.1)."""
from decimal import Decimal

import pytest

from app.calc import SacsInput, compute_sacs, FLOOR


def test_excess_is_inflow_minus_outflow():
    r = compute_sacs(SacsInput(inflow=15000, outflow=11000, monthly_expenses=10500))
    assert r.excess_to_reserve == Decimal("4000.00")


def test_excess_with_12000_outflow():
    r = compute_sacs(SacsInput(inflow=15000, outflow=12000, monthly_expenses=12000))
    assert r.excess_to_reserve == Decimal("3000.00")


def test_reserve_target_is_six_months_plus_deductibles():
    # 6 x 10,000 + (1,000 car + 2,000 home + 1,000 health) = 60,000 + 4,000
    r = compute_sacs(SacsInput(
        inflow=40000, outflow=18000, monthly_expenses=10000,
        insurance_deductibles=[1000, 2000, 1000],
    ))
    assert r.reserve_target == Decimal("64000.00")


def test_reserve_target_with_no_deductibles():
    r = compute_sacs(SacsInput(inflow=20000, outflow=15000, monthly_expenses=8000))
    assert r.reserve_target == Decimal("48000.00")


def test_floor_is_constant_thousand():
    r = compute_sacs(SacsInput(inflow=1, outflow=1, monthly_expenses=1))
    assert r.floor == FLOOR == Decimal("1000")


def test_negative_excess_when_overspending():
    r = compute_sacs(SacsInput(inflow=10000, outflow=12000, monthly_expenses=12000))
    assert r.excess_to_reserve == Decimal("-2000.00")


def test_balances_pass_through():
    r = compute_sacs(SacsInput(
        inflow=15000, outflow=12000, monthly_expenses=12000,
        private_reserve_balance=75000, investment_account_balance=15000,
    ))
    assert r.private_reserve_balance == Decimal("75000.00")
    assert r.investment_account_balance == Decimal("15000.00")


def test_money_parsing_accepts_strings_and_floats():
    r = compute_sacs(SacsInput(inflow="15000.50", outflow=11000.25, monthly_expenses=10000))
    assert r.inflow == Decimal("15000.50")
    assert r.outflow == Decimal("11000.25")
    assert r.excess_to_reserve == Decimal("4000.25")


def test_decimal_precision_no_float_drift():
    # 0.1 + 0.2 style drift must not appear
    r = compute_sacs(SacsInput(inflow="0.30", outflow="0.10", monthly_expenses="0.10"))
    assert r.excess_to_reserve == Decimal("0.20")
