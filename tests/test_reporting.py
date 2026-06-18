"""Reporting service: field discovery, completeness, build, serialize (spec 8.2-8.4)."""
from decimal import Decimal

from app.extensions import db
from app.models import Client
from app import reporting


def test_required_fields_cover_sacs_and_tcc(app, seeded):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        keys = [f["key"] for f in reporting.required_fields(c)]
        assert "private_reserve_balance" in keys
        assert "investment_account_balance" in keys
        assert "trust" in keys
        # one per account + cash for the investment account
        assert any(k.startswith("account:") for k in keys)
        assert any(k.startswith("account_cash:") for k in keys)
        assert any(k.startswith("liability:") for k in keys)


def test_missing_fields_flags_blanks(app, seeded):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        missing = reporting.missing_fields(c, {})  # nothing entered
        assert len(missing) == len(reporting.required_fields(c))
        # fill everything with 0 -> nothing missing
        entered = {f["key"]: "0" for f in reporting.required_fields(c)}
        assert reporting.missing_fields(c, entered) == []


def test_build_and_serialize_round_trip(app, seeded):
    with app.app_context():
        c = db.session.get(Client, seeded["client_id"])
        acc = seeded["accounts"]
        entered = {
            "private_reserve_balance": "75000",
            "investment_account_balance": "15000",
            f"account:{acc[0]}": "11000",    # IRA (C1)
            f"account:{acc[1]}": "15000",    # Roth IRA (C1)
            f"account_cash:{acc[1]}": "316",
            f"account:{acc[2]}": "50000",    # Brokerage (joint, non-retirement)
            "trust": "450000",
            f"liability:{seeded['liabilities'][0]}": "200000",
        }
        result, ctx = reporting.build(c, entered)
        # SACS: 15000 - 12000 = 3000 ; target 6*10000 + 4000 = 64000
        assert result.sacs.excess_to_reserve == Decimal("3000.00")
        assert result.sacs.reserve_target == Decimal("64000.00")
        # TCC: C1 retirement 26000 ; non-ret 50000 ; grand 526000 ; liabilities separate
        assert result.tcc.c1_retirement_total == Decimal("26000.00")
        assert result.tcc.non_retirement_total == Decimal("50000.00")
        assert result.tcc.grand_total_net_worth == Decimal("526000.00")
        assert result.tcc.liabilities_total == Decimal("200000.00")

        snap = reporting.serialize(result)
        assert snap["tcc"]["grand_total_net_worth"] == "526000.00"
        assert snap["sacs"]["excess_to_reserve"] == "3000.00"
        # ctx is render-ready
        assert len(ctx["c1_accounts"]) == 2
        assert len(ctx["non_ret_accounts"]) == 1
