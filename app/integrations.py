"""Integration service (spec 8.7, 11): run active input providers and merge field values.

This is what makes a report 'pull what it can': for a client, every active provider
fetches the fields it owns; results are merged by field key with their source + freshness.
Anything not returned stays blank for manual entry (spec 8.2). A failing provider degrades
gracefully (its error is reported; the field falls back to manual).
"""
from __future__ import annotations

from .models import ProviderCredential
from .vault import get_vault
from .providers.base import ClientData, LinkedAccount, ProviderError
from .providers.registry import build_provider, INPUT_PROVIDERS


def active_input_providers(tenant_id):
    creds = ProviderCredential.query.filter_by(tenant_id=tenant_id, status="active").all()
    vault = get_vault()
    providers = []
    for c in creds:
        if c.provider in INPUT_PROVIDERS:
            p = build_provider(c, vault)
            if p:
                providers.append(p)
    return providers


def _client_data_for(client, provider_name) -> ClientData:
    accounts = []
    for a in client.accounts:
        if a.provider == provider_name and a.external_ref:
            accounts.append(LinkedAccount(
                field_key=f"account:{a.id}", external_ref=a.external_ref,
                has_cash=a.has_cash_balance,
                cash_field_key=f"account_cash:{a.id}" if a.has_cash_balance else "",
            ))
    return ClientData(accounts=accounts,
                      trust_address=client.trust.property_address if client.trust else "")


def fetch_for_client(client):
    """Return (values, report).

    values: {field_key: FieldValue}
    report: {"sources": {field_key: provider}, "stale": [keys], "errors": [str], "fetched": n}
    """
    from . import billing
    values, report = {}, {"sources": {}, "stale": [], "errors": [], "fetched": 0}
    for p in active_input_providers(client.tenant_id):
        data = _client_data_for(client, p.name)
        billing.record_usage(client.tenant_id, "provider_call", detail=p.name)
        try:
            fetched = p.collect(data)
        except ProviderError as e:
            report["errors"].append(str(e))
            continue
        for key, fv in fetched.items():
            values[key] = fv
            report["sources"][key] = fv.source
            if not fv.is_fresh:
                report["stale"].append(key)
        report["fetched"] += len(fetched)
    return values, report
