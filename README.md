# SAGAN AW Client Portal

> Built by Sagan for the AW Client Report Portal engagement. See `analysis/` for the source
> discovery (call transcript, PRD analysis) and the approved Technical Specification.

A multi-tenant SaaS platform for financial-advisory firms: enter (or auto-fetch) client
data, generate polished quarterly **SACS** (cash-flow) and **TCC** (net-worth) PDF reports,
distribute them, and run the firm — with an AI agent layer, billing, and admin.

Built to the full Technical Specification — **all four phases, every element functional**,
**104 tests green**.

## Phases (all built)

- **Phase 1 — Portal core.** Client/account management, guided report workflow with a hard
  completeness gate, the deterministic calculation engine (spec §9, exhaustively tested),
  fixed-layout SACS & TCC PDF generation, auth + RBAC + TOTP MFA, audit log.
- **Phase 2 — Integrations.** Encrypted credential **vault** (Fernet) and read-only adapters
  for **Plaid, Schwab, RightCapital, Zillow, Pinnacle, PreciseFP** (+ **Dropbox/Canva** output).
  Reports auto-fill from connected providers and flag what is manual or stale. A bundled
  **provider sandbox** implements each real API contract so it runs end-to-end in dev.
- **Phase 3 — AI agents & client-facing.** Statement **extraction agent** (deterministic
  parsing; LLM optional via Anthropic), **anomaly flagging**, **onboarding agent**
  (invites, reminders, escalation), client-facing **onboarding form** and **expense
  worksheet**, and **distribution** (email with PDF attachments, Dropbox auto-save, Canva
  export). Real **Outbox** records every email.
- **Phase 4 — Multi-tenant SaaS.** Self-serve firm **signup**, per-tenant branding,
  **usage metering + billing** (cost + 20%, spec §16), **admin console** (superadmin),
  and tenant **suspension** enforcement.

## Taking it live (implementation team)

The app is complete and tested; going to production is **configuration + live credentials**,
not new architecture. Start with **[docs/IMPLEMENTATION_HANDOFF.md](docs/IMPLEMENTATION_HANDOFF.md)**:

- **[docs/PROVIDERS.md](docs/PROVIDERS.md)** — per-provider go-live (creds, endpoints, secret
  keys, account mapping, OAuth/refresh work to add).
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — Railway, Postgres, secrets, scheduled jobs.
- **[docs/OPERATIONS.md](docs/OPERATIONS.md)** — runbook (users/MFA, Outbox, reminders, billing, backups).
- **[.env.example](.env.example)** — every environment variable.
- **[livetests/](livetests/)** — `pytest livetests/` validates each adapter against its real API.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe seed.py            # 2 demo firms, providers connected, demo client
.\.venv\Scripts\python.exe run_sandbox.py     # (separate terminal) provider sandbox :5050
.\.venv\Scripts\python.exe run.py             # the portal :5000
```

Logins (password `changeme123`): `owner@firm.test` · `planner@firm.test` ·
`assistant@firm.test` · `superadmin@firm.test` (platform admin) · `northwind@firm.test`
(second firm). New firms can also self-register at **/signup**.

**Try it:** sign in as owner → a client → *Generate report*. The form auto-fills ~9 fields
from the connected providers (over real HTTP to the sandbox); fill the one manual field,
generate, then email / save-to-Dropbox / export-to-Canva. See usage on **Billing**; sign in
as `superadmin@firm.test` for the **Admin** console.

## CLI

```powershell
python manage.py create-user --email a@b.com --name "Jane" --role planner --password secret
python manage.py enroll-mfa  --email a@b.com     # prints an otpauth:// URI
python manage.py run-reminders                   # send due onboarding reminders / escalate
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest             # 104 tests
```

Coverage: calc engine + critical rules, data model, PDF content, reporting service, full
HTTP routes/RBAC/tenant-isolation (P1); vault, all provider adapters (driven through the real
sandbox), integration fetch (P2); anomaly, deterministic + LLM extraction, mailer, onboarding/
escalation, expense worksheet, distribution, and all their routes (P3); signup, billing maths,
metering, admin, suspension (P4).

## Configuration (environment; secrets never in code — spec §13)

| Variable | Purpose |
|---|---|
| `SECRET_KEY`, `VAULT_KEY` | Session signing; credential-vault key (derived from SECRET_KEY if unset) |
| `RAILWAY_DATABASE_PATH` / `DATABASE_URL` | DB location (SQLite default; Postgres-ready) |
| `SMTP_HOST/PORT/USER/PASSWORD/FROM` | Live email; without it, mail is recorded to the Outbox |
| `ANTHROPIC_API_KEY`, `LLM_MODEL` | Enables LLM extraction; deterministic parser runs without it |
| `PUBLIC_BASE_URL` | Base for client-facing onboarding / worksheet links |
| `CANVA_API_KEY` | Canva export (also configurable per-tenant under Settings → Providers) |

## Layout

```
app/
  calc/ pdf/ reporting.py     # deterministic engine + PDF renderers + glue (P1)
  vault.py providers/ integrations.py   # credential vault, adapters, fetch (P2)
  agents/                     # anomaly, extraction, llm, onboarding (P3)
  mailer.py distribution.py portal_public.py staff.py settings.py   # comms + UI (P3)
  billing.py signup.py admin.py   # SaaS layer (P4)
  models.py auth.py clients.py reports.py security.py audit.py
  templates/ static/
sandbox/                      # local provider sandbox (real API contracts)
tests/                        # 104 tests
seed.py manage.py run.py run_sandbox.py
```

## Notes

- **Sandbox vs live:** adapters call the provider `base_url`. In dev that is the bundled
  sandbox (`http://127.0.0.1:5050/<provider>`); in production, set it to the live API and
  store real credentials in the vault — no code change.
- **AI safety:** the LLM never touches the numeric path; agents propose, staff confirm; no
  client data is sent to a model unless `ANTHROPIC_API_KEY` is set (spec §12).
- PDF engine is ReportLab (spec §10). Exact visual parity with the firm's templates needs
  their sample PDFs (spec §17.2).
