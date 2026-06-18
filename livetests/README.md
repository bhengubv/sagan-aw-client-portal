# Live provider validation

Opt-in smoke tests that hit the **real** provider APIs to certify each integration as you
bring it online. They are **not** run by the normal suite (`pytest` only collects `tests/`),
so CI stays green. Each test **skips** unless its `AW_LIVE_*` flag and credentials are set.

## Run

```
pytest livetests/                 # every configured provider (others skip)
pytest livetests/ -k plaid -v     # just one
```

## Environment variables per provider

Set the flag (`AW_LIVE_<PROVIDER>=1`) plus the values. Use a real linked account's id for the
`*_ACCOUNT_REF` (the provider's account identifier you store in `Account.external_ref`).

| Provider | Flag | Required vars |
|---|---|---|
| Plaid | `AW_LIVE_PLAID` | `PLAID_BASE_URL` `PLAID_CLIENT_ID` `PLAID_SECRET` `PLAID_ACCESS_TOKEN` `PLAID_ACCOUNT_REF` |
| Schwab | `AW_LIVE_SCHWAB` | `SCHWAB_BASE_URL` `SCHWAB_ACCESS_TOKEN` `SCHWAB_ACCOUNT_REF` |
| RightCapital | `AW_LIVE_RIGHTCAPITAL` | `RC_BASE_URL` `RC_ACCESS_TOKEN` `RC_ACCOUNT_REF` |
| Zillow | `AW_LIVE_ZILLOW` | `ZILLOW_BASE_URL` `ZILLOW_API_KEY` `ZILLOW_ADDRESS` |
| Pinnacle | `AW_LIVE_PINNACLE` | `PINNACLE_BASE_URL` `PINNACLE_ACCESS_TOKEN` `PINNACLE_ACCOUNT_REF` |
| PreciseFP | `AW_LIVE_PRECISEFP` | `PRECISEFP_BASE_URL` `PRECISEFP_ACCESS_TOKEN` `PRECISEFP_CLIENT_ID` |
| Dropbox | `AW_LIVE_DROPBOX` | `DROPBOX_BASE_URL` `DROPBOX_ACCESS_TOKEN` |
| Canva | `AW_LIVE_CANVA` | `CANVA_BASE_URL` `CANVA_ACCESS_TOKEN` |
| LLM (Anthropic) | `AW_LIVE_LLM` | `ANTHROPIC_API_KEY` (`ANTHROPIC_BASE_URL`, `LLM_MODEL` optional) |

Base URLs are in `docs/PROVIDERS.md`. Note Dropbox/Canva tests **write** a file/design.
A green run here means the live adapter reaches the API, authenticates, and parses a response.
