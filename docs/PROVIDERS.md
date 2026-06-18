# Provider Go-Live Guide

How to take each adapter from the dev sandbox to the live API. The adapters
(`app/providers/inputs.py`, `outputs.py`, `app/agents/llm.py`) are coded to the contracts
below. To go live: register the app, obtain credentials, set the `base_url` to the live API,
store the listed secrets in the vault, link accounts, then run `livetests/`.

## How configuration works

A provider is a `ProviderCredential` row per tenant:
- `provider` — one of `plaid, schwab, rightcapital, zillow, pinnacle, precisefp, dropbox, canva`
- `base_url` — dev: `http://127.0.0.1:5050/<provider>`; prod: the live API base (below)
- `encrypted_token` — `vault.encrypt_dict({...secrets...})`
- `status` — `active` to use it

Configure via **Settings → Data providers** in the app, or programmatically:
```python
from app.vault import get_vault
from app.models import ProviderCredential
from app.extensions import db
db.session.add(ProviderCredential(
    tenant_id=TID, provider="plaid", status="active",
    base_url="https://production.plaid.com",
    encrypted_token=get_vault().encrypt_dict({"client_id": "...", "secret": "...", "access_token": "..."})))
db.session.commit()
```

**Account linking** (for per-account balances): set `Account.provider` and
`Account.external_ref` (the provider's account id) on each account. The integration service
maps the fetched balance to `account:<id>` (and `account_cash:<id>` when `has_cash_balance`).

---

## Input providers

### Plaid  — bank/investment balances
- **Adapter call:** `POST {base_url}/accounts/balance/get` with JSON `{client_id, secret, access_token}`.
- **Parses:** `accounts[].account_id`, `accounts[].balances.current` (→ balance),
  `accounts[].balances.available` (→ cash).
- **Vault secrets:** `client_id`, `secret`, `access_token`.
- **Account link:** `external_ref = <plaid account_id>`.
- **Live base_url:** `https://production.plaid.com` (or `https://sandbox.plaid.com`).
- **To go live:** create a Plaid app (client_id/secret). Implement **Plaid Link** + token
  exchange (`/link/token/create` → public_token → `/item/public_token/exchange`) to obtain the
  per-item `access_token`; store it in the vault. The balance call itself is production-correct.

### Schwab — investment accounts (authorised-user, compliance-gated)
- **Adapter call:** `GET {base_url}/trader/v1/accounts`, header `Authorization: Bearer <access_token>`.
- **Parses:** `accounts[].securitiesAccount.accountNumber`,
  `.currentBalances.liquidationValue` (→ balance), `.cashBalance` (→ cash).
- **Vault secrets:** `access_token`; optional `investment_account_ref` (its accountNumber →
  fills the SACS `investment_account_balance`).
- **Account link:** `external_ref = <accountNumber>`.
- **Live base_url:** `https://api.schwabapi.com`.
- **To go live:** Schwab Trader API requires app approval + **OAuth2 3-legged** auth and
  **token refresh**. Honour the firm's rule that access is per authorised user, never a shared
  agent login (spec §11). Add token refresh (Handoff §3).

### RightCapital — aggregator (treated as low-trust; refresh then read)
- **Adapter call:** `POST {base_url}/v1/sync` then `GET {base_url}/v1/accounts`, bearer auth.
- **Parses:** `accounts[].id`, `.balance`, `.is_stale` (→ freshness flag), `.as_of`.
- **Vault secrets:** `access_token`.
- **Account link:** `external_ref = <rightcapital account id>`.
- **To go live:** confirm RightCapital's auth scheme + exact endpoint paths against their API
  docs and adjust if needed. Keep the sync-then-read pattern (their data is often stale —
  the adapter already flags it). Prefer Plaid where possible (spec §11).

### Zillow — trust property value (Zestimate)
- **Adapter call:** `GET {base_url}/zestimate?address=<addr>&apikey=<key>`.
- **Parses:** `zestimate` (→ `trust`), `as_of`. Uses `client.trust.property_address`.
- **Vault secrets:** `api_key`.
- **⚠ Important:** Zillow's classic Zestimate API is retired. Use **Zillow Bridge API** or an
  alternative (ATTOM, HouseCanary). Point `base_url` at the chosen service and, if its response
  field isn't `zestimate`, adjust the one line in `ZillowProvider.collect` (or add a sibling
  adapter). Everything downstream is unaffected.

### Pinnacle Bank — bank balances (secure channel)
- **Adapter call:** `GET {base_url}/v1/accounts/balances`, bearer auth.
- **Parses:** `balances[].account_ref`, `.balance`.
- **Vault secrets:** `access_token`; optional `private_reserve_ref` (→ `private_reserve_balance`).
- **Account link:** `external_ref = <bank account ref>`.
- **To go live:** confirm the bank's real channel. If they expose a treasury/portal **HTTP
  API**, set `base_url` + token. If balances arrive only by **secure email/file** (per the
  discovery call), implement an ingestion adapter (IMAP/SFTP parse) behind the same `Provider`
  interface — `collect()` returns the same `{field_key: FieldValue}`. Do not automate insecurely.

### PreciseFP — onboarding profile import (not a balance source)
- **Adapter call:** `GET {base_url}/v1/clients/<external_id>`, bearer auth. Method `fetch_profile`.
- **Returns:** profile dict (`first_name, last_name, dob, ssn_last4, spouse{...}`).
- **Vault secrets:** `access_token`.
- **To go live:** obtain PreciseFP API access; map your client to its external id; wire
  `fetch_profile` into the client-import action (a thin call site — the adapter is ready).

---

## Output providers

### Dropbox — auto-save generated reports
- **Adapter call:** `POST {base_url}/2/files/upload`, header `Authorization: Bearer <token>`,
  `Dropbox-API-Arg: {path, mode, autorename}`, body = PDF bytes.
- **Vault secrets:** `access_token`.
- **Live base_url:** `https://content.dropboxapi.com`.
- **To go live:** Dropbox OAuth with **refresh tokens**, scope `files.content.write`.

### Canva — export the report as an editable design
- **Adapter calls:** `POST {base_url}/v1/asset-uploads` (bearer, body=PDF) → `asset.id`;
  then `POST {base_url}/v1/designs` (bearer, JSON `{title, asset_id}`) → `design.urls.edit_url`.
- **Vault secrets:** `access_token`.
- **Live base_url:** `https://api.canva.com/rest`.
- **To go live:** Canva **Connect** OAuth. Note the live asset upload may be an **async job**
  (create upload job → poll status → then create design). If so, add the poll between the two
  calls in `CanvaProvider.create_design`; the call sites are unaffected.

---

## LLM (Anthropic) — optional statement extraction
- **Call:** `POST {ANTHROPIC_BASE_URL}/v1/messages`, headers `x-api-key`,
  `anthropic-version: 2023-06-01`; body `{model, max_tokens, system, messages}`; parses the
  text content as JSON.
- **Config (env, not vault):** `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`, `LLM_MODEL`.
- **To go live:** set `ANTHROPIC_API_KEY`. Without it, the deterministic extractor runs — the
  feature is never disabled. The LLM never touches the numeric path (spec §12).

---

## Verifying a provider is live
Set the matching `AW_LIVE_*` env vars (see `livetests/README.md`) with real credentials and run:
```
pytest livetests/ -k plaid    # or schwab, zillow, dropbox, canva, llm, ...
```
Each test builds the real adapter against the live `base_url` and asserts it returns data.
