# Setup — AW Client Report Portal

Get the portal running on your machine in about **5 minutes**, then click through the full
demo (auto-fill → generate → distribute). Everything runs locally — nothing is deployed and
no real accounts are touched.

---

## Prerequisites

- **Python 3.10+** — check with `python --version` (macOS/Linux: `python3 --version`)
- **Git** — to clone the repo
- ~200 MB of disk space

---

## 1 · Get the code

```bash
git clone https://github.com/bhengubv/sagan-aw-client-portal.git
cd sagan-aw-client-portal
```

## 2 · Create a virtual environment & install

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

> From here on, `PY` means your venv Python:
> Windows → `.\.venv\Scripts\python.exe` · macOS/Linux → `.venv/bin/python`

## 3 · Seed the demo data

```bash
PY seed.py
```
Creates two demo firms, seven connected providers, and a fully linked demo client.

## 4 · Start the two servers (two terminals)

**Terminal 1 — the provider sandbox** (powers the live auto-fill):
```bash
PY run_sandbox.py        # http://127.0.0.1:5050
```

**Terminal 2 — the portal**:
```bash
PY run.py                # http://127.0.0.1:5000
```

## 5 · Open it and sign in

Go to **http://127.0.0.1:5000** and sign in:

| Login | Password | Role |
|---|---|---|
| `owner@firm.test` | `changeme123` | Owner (full access) |
| `planner@firm.test` | `changeme123` | Planner |
| `assistant@firm.test` | `changeme123` | Assistant |
| `superadmin@firm.test` | `changeme123` | Platform admin (Admin console) |
| `northwind@firm.test` | `changeme123` | A second firm |

New firms can also self-register at **`/signup`**.

## 6 · Try the full flow

1. Open **The Sample Household** → click **Generate report**.
2. Watch the form **auto-fill ~9 balances** from the connected providers (each tagged with its source).
3. Fill the one remaining field (the mortgage balance) → **Generate report**.
4. **Download** the SACS & TCC PDFs, **email** them, or **save to Dropbox**.
5. Check **Billing** for metered usage, and sign in as `superadmin@firm.test` for the **Admin** console.

---

## Running the tests

The test suite is installed already — just run it:
```bash
PY -m pytest             # 104 tests, ~40s
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Auto-fill comes up empty | The **sandbox (:5050) isn't running** — start `PY run_sandbox.py` in its own terminal. |
| "Address already in use" / port busy | Something else is on `5000`/`5050`. Stop it, or change the port in `run.py` / `run_sandbox.py`. |
| Want a clean demo again | Delete `instance/aw_portal.db`, then re-run `PY seed.py`. |
| `pip install` SSL/permission errors | Make sure the venv is activated/used (`PY`), and you're on Python 3.10+. |

---

## Going live (production)

Local is a **demo** backed by a provider sandbox. To deploy it and connect **real** bank/custodian
accounts, follow the implementation docs:

- **[docs/IMPLEMENTATION_HANDOFF.md](docs/IMPLEMENTATION_HANDOFF.md)** — start here
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** — hosting, Postgres, secrets, scheduled jobs
- **[docs/PROVIDERS.md](docs/PROVIDERS.md)** — connect each real provider (credentials, OAuth)
- **[docs/OPERATIONS.md](docs/OPERATIONS.md)** — day-to-day runbook
