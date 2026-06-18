# Operations Runbook

## Users & access
- **Create staff:** `python manage.py create-user --email .. --name ".." --role owner|planner|assistant --password ..`
- **Enrol MFA:** `python manage.py enroll-mfa --email ..` → share the printed `otpauth://` URI
  (QR it into an authenticator app). MFA then required at login for that user.
- **Roles:** `owner` (full incl. delete), `planner` (full client+report), `assistant` (entry +
  generate), `superadmin` (platform admin, cross-tenant).
- **Suspend a firm:** Admin console → Suspend. Suspended tenants' users get a 403 until
  reactivated; superadmin is unaffected.

## Email / Outbox
- Every outbound email is recorded in **Staff → Inbox → Outbox** with status
  `sent` (SMTP delivered), `recorded` (no SMTP configured), or `failed` (+ error).
- If email isn't delivering: confirm `SMTP_HOST/PORT/USER/PASSWORD/STARTTLS`; check Outbox
  rows for `failed` + error text. Without SMTP, mail is still captured (status `recorded`).

## Onboarding reminders
- `python manage.py run-reminders` sends due reminders and escalates after 4 (every 2 days,
  configurable in `app/agents/onboarding.py`). Schedule daily (DEPLOYMENT.md §5).
- Escalations appear in Staff → Inbox and email the firm owner.

## Providers
- Manage under **Settings → Data providers**: connect (base_url + secrets), activate/deactivate,
  remove. Secrets are vault-encrypted; the plaintext is never stored or shown.
- A provider that errors at fetch time **degrades gracefully** — its fields fall back to manual
  and the error is shown on the report form. Check the provider's `base_url`, token validity,
  and (for OAuth) token refresh.
- Validate live providers any time with `pytest livetests/` (see livetests/README.md).

## Billing
- Usage is metered per tenant (`report_generate`, `provider_call`, `ai_call`, `email_send`)
  and shown at **Settings → Billing** (cost + 20%) and in the Admin console per firm.
- Adjust unit prices/markup in `app/billing.py` (`UNIT_COSTS`, `MARKUP`).

## Data & backups
- Back up the database regularly (encrypted, region-pinned) and **test restores**.
- Back up `VAULT_KEY` separately and securely — it decrypts provider credentials.
- PII stored is minimised: only SSN **last-4**, DOB, balances. Honour the firm's retention
  policy for `ReportRun` history.

## Monitoring
- Health endpoint: `GET /healthz` → `{"status":"ok"}`. Point uptime monitoring at it.
- Application errors are logged by the WSGI server; ship logs to your platform's log drain.

## Audit
- Logins, PII views, report generation/downloads, provider changes, and admin actions are
  written to `audit_event`. Query it for compliance/investigations.
