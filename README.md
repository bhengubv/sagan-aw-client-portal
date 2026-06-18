# AW Client Report Portal
#### built by **Sagan**

# A full day of client-report prep — done in minutes. In your exact format.

Pull every balance from your banks and custodians **automatically**, let the system do **all the math**, and hand your client a polished **cash-flow** and **net-worth** report — with no Canva, no spreadsheets, no calculator, and no errors.

### ⏱️ A day → minutes  ·  ✅ Zero manual math  ·  🎯 Your templates, untouched  ·  🔒 Your data stays yours

---

## 1 · Open a client, hit *Generate* — the numbers fill themselves

The portal reaches into **Plaid, Schwab, RightCapital, Zillow and Pinnacle**, pulls the balances, and shows you **exactly where each number came from**. Anything it can't reach, it flags — so you never hunt for a figure again.

![Balances auto-filled from your connected providers, each tagged with its source](docs/img/autofill.png)

## 2 · One click, and the math is done

Inflows, outflows, retirement, the trust, liabilities, net worth — **every total calculated and re-checked for you**, every time. No more double-checking numbers at 9pm.

![Report ready — every total computed, ready to download or send](docs/img/review.png)

## 3 · Your reports, your format

Pixel-perfect **SACS** (cash-flow) and **TCC** (net-worth) PDFs — exactly the way Andrew built them. Download, email to the client, or drop straight into Dropbox.

| Cash-flow (SACS) | Net-worth (TCC) |
|:--:|:--:|
| ![SACS cash-flow report](docs/img/report-sacs.png) | ![TCC net-worth report](docs/img/report-tcc.png) |

---

## Why your team will love it

- **⏱️ A day becomes minutes.** Spend that time with clients, not in Canva.
- **✅ No more math errors.** Every figure is computed and cross-checked automatically.
- **🎯 Nothing changes for your clients.** Same reports, same format — just faster and flawless.
- **🔒 Secure by design.** Read-only access, your data stays yours, and **nothing is ever used to train an AI**.
- **📈 Grow without hiring.** Take on more clients without adding headcount.

> It's already built, fully tested, and ready to connect to your accounts.

## See it in action

▶️ **[Watch the 2-minute walkthrough](#)**  *(drop your Loom link here)*

Want to click around yourself? **[Get it running in 5 minutes → SETUP.md](SETUP.md)**

---

<details>
<summary><strong>🔧 For developers &amp; the implementation team</strong> — setup, architecture, tests, go-live</summary>

<br>

A multi-tenant SaaS platform for financial-advisory firms: enter (or auto-fetch) client data,
generate quarterly **SACS** and **TCC** PDFs, distribute them, and run the firm — with an AI
agent layer, billing, and admin. Built to the full Technical Specification — **all four phases,
every element functional, 104 tests green**.

### Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe seed.py            # 2 demo firms, providers connected, demo client
.\.venv\Scripts\python.exe run_sandbox.py     # (separate terminal) provider sandbox :5050
.\.venv\Scripts\python.exe run.py             # the portal :5000
```

Sign in as `owner@firm.test` / `changeme123` → a client → **Generate report**. The form
auto-fills ~9 fields from the connected providers (real HTTP to the bundled sandbox); fill the
one manual field, generate, then email / save-to-Dropbox / export-to-Canva. `superadmin@firm.test`
opens the Admin console; new firms self-register at `/signup`.

### What's built (all four phases)

- **Phase 1 — Portal core.** Client/account management, guided report workflow with a hard
  completeness gate, the deterministic calculation engine (spec §9, exhaustively tested),
  fixed-layout SACS &amp; TCC PDF generation, auth + RBAC + TOTP MFA, audit log.
- **Phase 2 — Integrations.** Encrypted credential **vault** (Fernet) and read-only adapters for
  **Plaid, Schwab, RightCapital, Zillow, Pinnacle, PreciseFP** (+ **Dropbox/Canva** output),
  with a bundled **provider sandbox** that implements each real API contract so it runs end-to-end in dev.
- **Phase 3 — AI agents &amp; client-facing.** Statement **extraction** (deterministic; LLM optional
  via Anthropic), **anomaly flagging**, an **onboarding agent** (invites/reminders/escalation),
  client-facing **onboarding form** and **expense worksheet**, and **distribution** (email, Dropbox, Canva).
- **Phase 4 — Multi-tenant SaaS.** Self-serve **signup**, per-tenant branding, **usage metering +
  billing** (cost + 20%), **admin console**, and tenant **suspension**.

### Tests

```powershell
.\.venv\Scripts\python.exe -m pytest             # 104 tests
```
Covers the calc engine + critical rules, PDF content, all routes/RBAC/tenant-isolation, the
vault, every provider adapter (driven through the real sandbox), the AI agents, distribution,
billing, and admin.

### Taking it live

Going to production is **configuration + live credentials, not new architecture.** Start here:

- **[docs/IMPLEMENTATION_HANDOFF.md](docs/IMPLEMENTATION_HANDOFF.md)** — the entry point
- **[docs/PROVIDERS.md](docs/PROVIDERS.md)** — per-provider go-live (creds, endpoints, OAuth/refresh)
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — Railway, Postgres, secrets, scheduled jobs
- **[docs/OPERATIONS.md](docs/OPERATIONS.md)** — runbook (users/MFA, Outbox, reminders, billing, backups)
- **[.env.example](.env.example)** — every environment variable
- **[livetests/](livetests/)** — `pytest livetests/` validates each adapter against its real API

### Layout

```
app/
  calc/ pdf/ reporting.py     # deterministic engine + PDF renderers + glue
  vault.py providers/ integrations.py   # credential vault, adapters, fetch
  agents/                     # anomaly, extraction, llm, onboarding
  mailer.py distribution.py portal_public.py staff.py settings.py
  billing.py signup.py admin.py
  models.py auth.py clients.py reports.py security.py audit.py
sandbox/   # local provider sandbox (real API contracts)
tests/     # 104 tests
seed.py manage.py run.py run_sandbox.py
```

**Notes** — Adapters call a provider `base_url`: the bundled sandbox in dev, the live API in
prod (no code change). The LLM never touches the numeric path. PDFs use ReportLab; exact visual
parity with the firm's templates needs their sample PDFs.

</details>
