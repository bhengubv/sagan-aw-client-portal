# Implementation Handoff — AW Client Report Portal

This document is the entry point for the team taking the platform to production. The
software is complete and tested (104 green); what remains is **connecting live external
providers and deploying**. Everything you need is here and in the sibling docs.

- **[PROVIDERS.md](PROVIDERS.md)** — per-provider go-live: credentials, endpoints, secret
  keys, account mapping, and the OAuth/lifecycle work to add. **Start here for integrations.**
- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Railway, Postgres migration, secrets, scheduled jobs.
- **[OPERATIONS.md](OPERATIONS.md)** — runbook: backups, monitoring, reminders, MFA, Outbox.
- **[../.env.example](../.env.example)** — every environment variable.
- **[../livetests/](../livetests/)** — runnable smoke tests that validate each provider
  against its **real** API once you have credentials.

## 1. What is done vs. what you carry on

**Done (real, tested, runs today):**
- The entire application: client/account management, deterministic calc engine, SACS/TCC PDF
  generation, the report workflow, auth/RBAC/MFA, audit log.
- The integration framework: an encrypted **credential vault**, a uniform **provider
  interface**, and **adapters coded to each provider's real API contract** (request shapes,
  auth headers, response parsing).
- AI agents (extraction, anomaly, onboarding), client-facing forms, distribution
  (email/Dropbox/Canva), and the full multi-tenant SaaS layer (signup, billing, admin).
- A **provider sandbox** implementing each provider's contract so the whole system runs
  end-to-end in dev over real HTTP.

**You carry on (the live wiring):**
1. Obtain credentials/app registrations for each provider you will use.
2. For OAuth providers, implement the **auth handshake + token refresh** (the adapters
   consume a ready access token from the vault; see §3 and PROVIDERS.md).
3. Set each provider's `base_url` to the live API and store secrets in the vault
   (Settings → Data providers, or seeded/migrated).
4. Validate with `livetests/` against the real APIs.
5. Deploy (DEPLOYMENT.md) and wire the reminders cron (OPERATIONS.md).

Nothing in the app needs to be re-architected for any of this — these are the designed seams.

## 2. Architecture in one screen

```
Browser ── Flask app ──┬── calc/ (pure engine, spec §9)        deterministic, no I/O
                       ├── pdf/  (ReportLab SACS/TCC)
                       ├── reporting.py (profile+balances → calc → PDF)
                       ├── integrations.py ── providers/ ──HTTP──> live API  (prod)
                       │                          ▲                └─────────> sandbox (dev)
                       │                          └── vault.py (Fernet-encrypted secrets)
                       ├── agents/ (extraction, anomaly, onboarding; LLM optional)
                       ├── mailer.py / distribution.py (Outbox + SMTP; Dropbox/Canva)
                       └── billing.py / admin.py / signup.py (multi-tenant SaaS)
SQLite (dev) / Postgres (prod).  Every row carries tenant_id.
```

Key seams the live work plugs into:
- **`app/providers/`** — add nothing to call a provider; just configure its `base_url` + secrets.
  To support a new auth lifecycle, extend the adapter or add a token manager (see §3).
- **`app/vault.py`** — all provider secrets are encrypted here. `VAULT_KEY` is the root of trust.
- **`ProviderCredential`** rows (per tenant) — `provider`, `base_url`, `encrypted_token`, `status`.
- **`Account.provider` / `Account.external_ref`** — link a client account to a provider's account id.

## 3. The one cross-cutting addition: OAuth token lifecycle

The adapters read a ready `access_token` (and friends) from the vault and call the API. For
providers using OAuth2 (Plaid, Schwab, Dropbox, Canva, possibly RightCapital/PreciseFP),
production needs the **token acquisition + refresh** lifecycle, which is intentionally not
guessed here because it is provider- and account-specific:

- **Acquire:** run the provider's auth flow (e.g., Plaid Link, Schwab/Dropbox/Canva OAuth
  consent) to get the first access/refresh token; store via `vault.encrypt_dict({...})` into
  the tenant's `ProviderCredential`.
- **Refresh:** on a `401`, use the refresh token to mint a new access token and re-encrypt.
  Recommended seam: a small `TokenManager` that the adapter calls before requests, or a
  `before_request`/retry wrapper. Keep it behind the existing `Provider` interface so calc/
  render/UI are untouched.

Per PROVIDERS.md, each provider notes whether it needs this and which flow.

## 4. Run it locally (sanity check before you change anything)

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python seed.py
.venv\Scripts\python run_sandbox.py     # :5050, separate terminal
.venv\Scripts\python run.py             # :5000
.venv\Scripts\python -m pytest          # 104 green
```

## 5. Go-live checklist

- [ ] Set `SECRET_KEY` and a generated `VAULT_KEY` (back the vault key up securely).
- [ ] Provision Postgres; set `DATABASE_URL`; create schema (DEPLOYMENT.md §DB).
- [ ] Configure SMTP (or accept Outbox-only) and `PUBLIC_BASE_URL`.
- [ ] For each provider in scope: register the app, implement OAuth/refresh (§3), set
      `base_url` to live, store secrets in the vault, link `Account.external_ref`s.
- [ ] Run `livetests/` against each live provider until green.
- [ ] Set `ANTHROPIC_API_KEY` if enabling LLM extraction (optional).
- [ ] Deploy to Railway; pin region for data residency (spec §13.3).
- [ ] Schedule `python manage.py run-reminders` (e.g., daily) — OPERATIONS.md.
- [ ] Create the first superadmin; create/enroll staff users + MFA (OPERATIONS.md).
- [ ] Smoke-test a full quarterly report for one real client; confirm PDFs and distribution.
- [ ] Obtain the firm's sample SACS/TCC PDFs and tune the templates for exact parity (spec §17.2).

## 6. Test strategy you inherit

- `pytest` → 104 unit/integration tests, hermetic (no network), green in CI.
- `pytest livetests/` → opt-in, env-gated checks against the **real** provider APIs; skipped
  unless you set the relevant `AW_LIVE_*` env vars + credentials. Use these to certify each
  provider as you bring it online. CI stays green because they are not under `tests/`.
