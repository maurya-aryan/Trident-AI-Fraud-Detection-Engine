# OAuth + IMAP (XOAUTH2) Implementation Instructions — Agent Checklist

Purpose: help an engineering agent implement a one-time user-friendly mailbox connect flow that keeps the existing IMAP poller but removes env-file / app-password friction. The agent should add server-side encrypted credential/token storage, an OAuth flow for Google/Microsoft producing refresh tokens, and an IMAP XOAUTH2 auth path so users authenticate once and never manually edit env vars.

Target: keep the current `scripts/run_imap_poller.py` behavior (message parsing, scoring, streaming logs) and only change how credentials are provided to it.

---

## Quick summary (what to deliver)
- A small, well-documented backend OAuth + token storage module.
- A Connect UI flow (frontend) which triggers OAuth or accepts app-password fallback once.
- Poller integration that uses stored credentials or refresh tokens to authenticate to IMAP using XOAUTH2 (for Google/Microsoft) or basic auth (fallback).
- End-to-end tests and a `docs/` verification checklist.

---

## Requirements (dependencies & accounts)
- Add to `requirements.txt` (or pip install):
  - google-auth
  - google-auth-oauthlib
  - google-auth-httplib2
  - google-api-python-client (optional if you later use Gmail API)
  - msal (for Microsoft OAuth) or `requests_oauthlib` (optional)
  - cryptography
  - requests

- Google Cloud Console access to create an OAuth client (if implementing Google OAuth). Save client_id & client_secret.
- (Optional) Microsoft Azure AD app registration for Outlook/Office365 support.

---

## Security notes (must follow)
- Never log plaintext credentials or full message content to public logs.
- Encrypt refresh tokens / credentials at rest using a server-side master key (environment variable or OS secret manager). Use `cryptography.Fernet`.
- Provide a `disconnect` API that deletes stored tokens.
- Show users a visible UI to revoke/disconnect and document how to remove access from provider console.

---

## File & module plan (suggested)
- `api/auth_google.py` — new FastAPI router for Google oauth endpoints.
- `core/token_store.py` — helper to encrypt/decrypt and read/write stored tokens (JSON or SQLite).
- `modules/gmail_xoauth2.py` — helper to build XOAUTH2 tokens and provide `get_access_token(email_id)`.
- `api/routes.py` — minor changes: add endpoints for `GET /auth/google/start`, `GET /auth/google/callback`, `POST /connect/basic` (app-password form), `POST /poller/connect-test`.
- `scripts/run_imap_poller.py` — minimal changes: replace fetching credentials from environment with reading from `core/token_store` (or injected via `env_overrides`) and do XOAUTH2 if token exists.
- `frontend` — add a `Connect mailbox` UI element that either opens OAuth or posts basic auth form.

---

## Step-by-step implementation (detailed)

### A. Token storage helper (`core/token_store.py`)
Goal: provide a small API to store and retrieve credentials encrypted.

Acceptance: store `owner_id` (or unique mailbox id) -> { provider, email, encrypted_secret, meta }

Suggested API (pseudocode):

- init(master_key: bytes | env var)
- save_credentials(owner_id: str, provider: str, email: str, secret: str, meta: dict)
- get_credentials(owner_id: str) -> dict | None
- delete_credentials(owner_id: str)

Implementation notes:
- Use `cryptography.Fernet(master_key)` to encrypt `secret` (app password or refresh token JSON).
- Persist single JSON file `data/tokens.json` or lightweight SQLite. Keep file permission-restricted.

Example (pseudocode):

```py
from cryptography.fernet import Fernet
import json, os

MASTER_KEY = os.environ.get('TOKEN_MASTER_KEY')  # must exist in env
f = Fernet(MASTER_KEY)

# store: encrypt secret, write file
# retrieve: decrypt
```

Security: Ensure `TOKEN_MASTER_KEY` is stored securely by the operator (e.g., environment or OS secret manager). Rotateable later.


### B. Backend OAuth endpoints (`api/auth_google.py`)
Goal: Implement OAuth endpoints that exchange codes for refresh tokens and store them with `token_store`.

Endpoints:
- `GET /auth/google/start?owner_id=<id>&redirect_frontend=<url>` — build Google OAuth URL and redirect the user.
- `GET /auth/google/callback?owner_id=<id>&state=...` — receive code, exchange for tokens, store refresh token via `token_store.save_credentials(owner_id, provider='google', email=...)`, then redirect back to frontend with success.

Implementation details:
- Use `google_auth_oauthlib.flow.Flow` or `requests_oauthlib` to perform the OAuth exchange.
- When creating the OAuth flow, request `access_type='offline'` and `include_granted_scopes='true'` to obtain a refresh token.
- Scope for IMAP XOAUTH2 (Gmail): `https://mail.google.com/` (or `https://www.googleapis.com/auth/gmail.readonly`—if you plan to use Gmail API instead, but for IMAP XOAUTH2 `https://mail.google.com/` is common).

Callback logic:
- Exchange authorization code for tokens.
- Save `refresh_token` (and optionally `access_token` + expiry) in encrypted store bound to `owner_id`.
- Also save `email` / `profile` information if available from token introspection or Gmail profile API.

Security & UX:
- Use `state` and `owner_id` to prevent CSRF and tie the token to a local user/account.
- After success, redirect back to the frontend URL provided in `state` or query param and show a success banner.


### C. Poller integration with XOAUTH2 (minimal code changes in `scripts/run_imap_poller.py`)
Goal: Before establishing IMAP connection, check token store for stored credentials for the mailbox. If a `refresh_token` exists, fetch a fresh `access_token` and authenticate IMAP with XOAUTH2. Otherwise, fall back to basic auth using stored app-password.

High-level flow (poller boot/connect):
1. Determine mailbox `owner_id` or `imap_user` to look up in token_store.
2. creds = token_store.get_credentials(owner_id)
3. if creds.provider == 'google' and creds.secret is refresh_token:
     - call token refresh endpoint (e.g., using `google.oauth2.credentials.Credentials` or `requests` to token URI) to get `access_token`.
     - create XOAUTH2 string: `user={email}\x01auth=Bearer {access_token}\x01\x01`, base64 encode and use imaplib `authenticate('XOAUTH2', lambda x: xoauth2_b64)`.
4. else if creds.provider == 'basic' (app-password): use basic login as before.

Python example for XOAUTH2 with `imaplib`:

```py
import base64, imaplib

def build_xoauth2(email, access_token):
    auth_str = f"user={email}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_str.encode()).decode()

M = imaplib.IMAP4_SSL(host, 993)
xoauth = build_xoauth2(email, access_token)
M.authenticate('XOAUTH2', lambda x: xoauth)
```

Edge cases:
- If token refresh fails (revoked), the poller should broadcast the error and fall back to an interactive reconnect flow (UI) or fail gracefully.
- Some Google accounts may not allow IMAP (disabled at account level)—detect and present actionable message to the user.


### D. Frontend: "Connect mailbox" flow (minimal UX)
Goal: Provide a single place for the user to authenticate once. This can be placed in the existing Terminal section or a settings page.

UI options:
- Provider buttons: `Connect with Google`, `Connect with Outlook`.
- A fallback form: `Email`, `IMAP Host`, `App Password` (for providers without OAuth).

Flow:
- For OAuth: front-end opens `/auth/google/start?owner_id=<uuid>&return_to=/app/path` in a popup/new tab.
- After callback, backend redirects back to `return_to` with `?connected=1` — UI reads this and shows success.
- For app-password fallback, POST to `/connect/basic` with form JSON: `{ owner_id, provider: 'basic', email, host, password }` — backend stores encrypted.

Security UX:
- Make clear the credential is stored encrypted and show a `Disconnect` button.
- Provide a `Test connection` button which calls `POST /poller/connect-test` to attempt a connection and return success + sample headers.


### E. Backend auxiliary endpoints
Create these endpoints in `api/routes.py` or `api/auth_google.py`:

- `POST /connect/basic` — store an encryption of `{email, host, password}` for owner_id and return success.
- `GET /auth/google/start` — start oauth redirect.
- `GET /auth/google/callback` — accept code and store tokens.
- `POST /poller/connect-test` — attempt to obtain token (refresh if needed) and open IMAP with supplied creds to list `INBOX` or fetch first header; return success/failure and human message.
- `POST /auth/disconnect` — delete stored tokens for owner.


### F. Tests & verification steps (handable by agent)
1. Local dev setup:
   - Set `TOKEN_MASTER_KEY` env var. Use `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` to generate one.
   - Add OAuth client credentials (client_id/client_secret) to env or a local config file not in git.

2. End-to-end test flow:
   - Start backend and frontend.
   - Open frontend and click `Connect with Google`.
   - Complete Google consent for test user.
   - Backend should save encrypted refresh token; poller/test endpoint should be able to use it to get access_token and perform IMAP XOAUTH2 connect.
   - Trigger poller start; verify logs show successful XOAUTH2 authentication.

3. Failure scenarios to test:
   - Revoked refresh token: backend should return graceful error and UI should prompt reconnect.
   - Provider denies IMAP access: UI shows action (enable IMAP in account settings) and link to help.

Acceptance criteria:
- Single sign-on flow completes and tokens are stored encrypted.
- Poller connects to IMAP using XOAUTH2 with access_token and proceeds to select INBOX.
- Fallback: app-password flow works and poller behaves as before.
- Users can disconnect/revoke from UI and stored tokens are deleted.

---

## Helpful snippets & examples

1) Build XOAUTH2 string (python):

```py
import base64

def xoauth2_b64(email, access_token):
    auth_str = f"user={email}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_str.encode()).decode()
```

2) Refresh token -> access token (Google) using `requests` (simple):

```py
import requests

def refresh_google_token(client_id, client_secret, refresh_token):
    token_uri = 'https://oauth2.googleapis.com/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }
    r = requests.post(token_uri, data=data)
    r.raise_for_status()
    return r.json()  # contains access_token, expires_in
```

3) IMAP connect example using imaplib + XOAUTH2:

```py
import imaplib

M = imaplib.IMAP4_SSL('imap.gmail.com', 993)
xoauth = xoauth2_b64('user@example.com', access_token)
M.authenticate('XOAUTH2', lambda x: xoauth)
# Now: M.select('INBOX') etc.
```


---

## Operational notes for Google verification
If you plan to make this public, request the following early from the product owner:
- Privacy policy URL
- Application name, logo
- Support contact email
- Justification for the `https://mail.google.com/` scope in consent screen

For testing/in-house use: add test users to the OAuth consent screen and avoid full verification until product is stable.

---

## Rollout plan & timeline (suggested incremental)
- Day 0.5: Add `core/token_store.py`, simple `POST /connect/basic`, basic frontend form, and test connection endpoint. (Fast path — removes env editing.)
- Day 1: Add Google OAuth endpoints and frontend button; store refresh tokens encrypted.
- Day 1.5: Integrate token retrieval into poller (XOAUTH2 path) and add disconnect + tests.
- Day 2: Add Microsoft OAuth (optional) and test; write docs for app verification.


---

## Handoff checklist for the agent (deliverables)
- New files: `api/auth_google.py`, `core/token_store.py`, `modules/gmail_xoauth2.py` (or similar) plus minimal frontend changes documented in PR.
- Tests: a local test script demonstrating XOAUTH2 login to IMAP using stored refresh token.
- README entry: `docs/OAuth_IMAP_Instructions_for_Agent.md` plus a `docs/quick-start-oauth.md` for operators.
- Security: `TOKEN_MASTER_KEY` usage documented; instructions to store it in env or secret manager.
- Acceptance tests: step-by-step E2E test described in section F passed.

---

If you want, I can also generate the initial skeleton files and a small PoC `scripts/xoauth2_poc.py` that demonstrates refresh-token -> access-token -> IMAP XOAUTH2 connect. Tell me if you want that next, and whether to target Google only (preferred) or both Google + Microsoft.

