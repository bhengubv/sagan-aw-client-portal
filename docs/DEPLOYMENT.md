# Deployment

Target is **Railway** (spec §6.3), but the app is a standard WSGI Flask app and runs on any
host. Below is what to set up.

## 1. App server

The app factory is `app:create_app`. Serve with a production WSGI server:
```
pip install gunicorn          # Linux
gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 3
```
`run.py` is for local dev only (Flask dev server). On Railway, set the start command to the
gunicorn line above and `PORT` is injected by the platform.

## 2. Database (Postgres)

Dev uses SQLite via `db.create_all()`. For production:
1. Provision Postgres; set `DATABASE_URL=postgresql+psycopg://user:pass@host:5432/aw_portal`
   (add the `psycopg` driver to requirements for Postgres).
2. **Schema:** the app calls `db.create_all()` on startup, which creates missing tables. For
   controlled migrations over time, adopt **Alembic**:
   ```
   pip install alembic
   alembic init migrations          # configure target_metadata = app.extensions.db.metadata
   alembic revision --autogenerate -m "init"
   alembic upgrade head
   ```
   Until then, `create_all()` is sufficient for first deploy.
3. The data model is already multi-tenant (every row has `tenant_id`); no data migration is
   needed to onboard more firms.

## 3. Secrets & config

Set via the platform's env (never commit). See `.env.example` for the full list. Critical:
- `SECRET_KEY` — long random string.
- `VAULT_KEY` — generated Fernet key; **back it up**. Losing/rotating it makes stored provider
  credentials undecryptable (re-enter them if rotated).
- `DATABASE_URL`, `PUBLIC_BASE_URL`, SMTP_*, and `ANTHROPIC_API_KEY` if using the LLM.

## 4. Provider sandbox in production

Do **not** deploy `sandbox/` to production — it is a dev test double. In prod, each provider's
`base_url` points at the live API (see PROVIDERS.md). The sandbox stays a local/CI convenience.

## 5. Scheduled jobs

The onboarding agent's reminders/escalation run on demand:
```
python manage.py run-reminders
```
Schedule it (e.g., daily) with Railway Cron or any scheduler. It is idempotent and respects
the reminder interval and escalation threshold.

## 6. Region & compliance

Pin the app + database region to satisfy data-residency expectations (spec §13.3). Keep
TLS/HSTS at the edge. The platform must not route the firm's data through services the firm's
compliance policy forbids (spec §13.3) — verify your host and any CDN.

## 7. First-run after deploy

```
python manage.py create-user --email owner@firm.com --name "Owner" --role owner --password '...'
python manage.py enroll-mfa  --email owner@firm.com     # share the otpauth URI securely
```
Or let firms self-register at `/signup`. Create a `superadmin` for platform oversight by
inserting a user with `role="superadmin"` (or promote one in the DB).
