"""Input provider adapters (spec 11). Real API contracts; live in prod, sandbox in dev."""
from __future__ import annotations

from .base import Provider, FieldValue, ClientData


def _emit(data: ClientData, info: dict, source: str) -> dict:
    """Map {external_ref: {balance, cash, fresh, as_of}} to {field_key: FieldValue}."""
    out = {}
    for la in data.accounts:
        rec = info.get(la.external_ref)
        if not rec or rec.get("balance") is None:
            continue
        fresh = rec.get("fresh", True)
        as_of = rec.get("as_of", "")
        out[la.field_key] = FieldValue(la.field_key, str(rec["balance"]), source, fresh, as_of)
        if la.has_cash and la.cash_field_key and rec.get("cash") is not None:
            out[la.cash_field_key] = FieldValue(la.cash_field_key, str(rec["cash"]), source, fresh, as_of)
    return out


class PlaidProvider(Provider):
    """Plaid /accounts/balance/get (consented, read-only aggregation)."""
    name = "plaid"

    def collect(self, data: ClientData) -> dict:
        body = {"client_id": self.secrets.get("client_id"),
                "secret": self.secrets.get("secret"),
                "access_token": self.secrets.get("access_token")}
        resp = self._post("/accounts/balance/get", json=body)
        info = {}
        for a in resp.get("accounts", []):
            bal = a.get("balances", {}) or {}
            info[str(a.get("account_id"))] = {"balance": bal.get("current"),
                                              "cash": bal.get("available")}
        return _emit(data, info, self.name)


class SchwabProvider(Provider):
    """Schwab Trader API /accounts (authorised-user, OAuth bearer, read-only)."""
    name = "schwab"

    def collect(self, data: ClientData) -> dict:
        headers = {"Authorization": f"Bearer {self.secrets.get('access_token', '')}"}
        resp = self._get("/trader/v1/accounts", headers=headers)
        items = resp.get("accounts", []) if isinstance(resp, dict) else resp
        info = {}
        for item in items:
            sa = item.get("securitiesAccount", item)
            ref = str(sa.get("accountNumber"))
            cb = sa.get("currentBalances", {}) or {}
            info[ref] = {"balance": cb.get("liquidationValue"), "cash": cb.get("cashBalance")}
        out = _emit(data, info, self.name)
        inv_ref = self.secrets.get("investment_account_ref")
        if inv_ref and inv_ref in info and info[inv_ref]["balance"] is not None:
            out["investment_account_balance"] = FieldValue(
                "investment_account_balance", str(info[inv_ref]["balance"]), self.name)
        return out


class RightCapitalProvider(Provider):
    """RightCapital: force a re-sync, then read (data is often stale → flagged, spec 11)."""
    name = "rightcapital"

    def collect(self, data: ClientData) -> dict:
        headers = {"Authorization": f"Bearer {self.secrets.get('access_token', '')}"}
        self._post("/v1/sync", headers=headers, json={})        # push it to refresh
        resp = self._get("/v1/accounts", headers=headers)
        info = {}
        for a in resp.get("accounts", []):
            info[str(a.get("id"))] = {"balance": a.get("balance"),
                                      "fresh": not a.get("is_stale", False),
                                      "as_of": a.get("as_of", "")}
        return _emit(data, info, self.name)


class ZillowProvider(Provider):
    """Zillow Zestimate for the trust property value (clearly an estimate)."""
    name = "zillow"

    def collect(self, data: ClientData) -> dict:
        if not data.trust_address:
            return {}
        resp = self._get("/zestimate", params={"address": data.trust_address,
                                               "apikey": self.secrets.get("api_key", "")})
        z = resp.get("zestimate")
        if z is None:
            return {}
        return {"trust": FieldValue("trust", str(z), self.name, as_of=resp.get("as_of", ""))}


class PinnacleProvider(Provider):
    """Pinnacle Bank secure balance API (treasury/portal API; read-only)."""
    name = "pinnacle"

    def collect(self, data: ClientData) -> dict:
        headers = {"Authorization": f"Bearer {self.secrets.get('access_token', '')}"}
        resp = self._get("/v1/accounts/balances", headers=headers)
        info = {str(b.get("account_ref")): {"balance": b.get("balance")}
                for b in resp.get("balances", [])}
        out = _emit(data, info, self.name)
        pr_ref = self.secrets.get("private_reserve_ref")
        if pr_ref and pr_ref in info and info[pr_ref]["balance"] is not None:
            out["private_reserve_balance"] = FieldValue(
                "private_reserve_balance", str(info[pr_ref]["balance"]), self.name)
        return out


class PreciseFPProvider(Provider):
    """PreciseFP onboarding/profile import (not a balance source)."""
    name = "precisefp"

    def collect(self, data: ClientData) -> dict:
        return {}

    def fetch_profile(self, external_id: str) -> dict:
        headers = {"Authorization": f"Bearer {self.secrets.get('access_token', '')}"}
        return self._get(f"/v1/clients/{external_id}", headers=headers)
