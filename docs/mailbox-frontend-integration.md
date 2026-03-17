# Mailbox OAuth + Poller Integration

This project uses the frontend UI to connect a mailbox via Google OAuth, store refresh tokens in the backend, and run the IMAP poller to fetch mail. This guide explains the pieces, the recent XOAUTH2 fix, and how to run everything end-to-end.

## What changed
- File updated: `modules/gmail_xoauth2.py`
- Fix: The XOAUTH2 auth string now returns the raw value (not base64-encoded) so `imaplib.IMAP4.authenticate` can encode it correctly. This prevents Gmail errors like `Invalid SASL argument` during IMAP authentication.

## Prerequisites
- Python environment with project deps installed (`pip install -r requirements.txt`)
- Node/NPM for the frontend
- `.env` at the repo root containing at least:
  - `TOKEN_MASTER_KEY=...`
  - `GOOGLE_CLIENT_ID=...`
  - `GOOGLE_CLIENT_SECRET=...`
  - `GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback`

## Start backend (API)
```powershell
cd C:\Users\91801\Documents\GitHub\Trident-AI-Fraud-Detection-Engine
python main.py api
```
You should see: `INFO: Loaded environment from .env`.

## Start frontend (Vite UI)
```powershell
cd C:\Users\91801\Documents\GitHub\Trident-AI-Fraud-Detection-Engine\frontend
npm install   # first time only
npm run dev -- --host
```
Open the URL shown (typically http://localhost:5173).

## Connect mailbox via UI
1) In the UI, click **Connect Mailbox** → **Connect** to Google and complete OAuth.
2) After success, the backend stores the refresh token encrypted with `TOKEN_MASTER_KEY`.
3) Click **Test Connection** to verify IMAP (uses the XOAUTH2 fix in `modules/gmail_xoauth2.py`).

## Run the IMAP poller
- From the UI, start the poller (or run `python scripts/run_imap_poller.py`).
- Logs appear in the UI live log panel.
- Common issues:
  - `Invalid SASL argument`: restart the API/poller after the XOAUTH2 fix; ensure the account is connected again.
  - Token revoked: disconnect and reconnect the mailbox via the UI.

## Troubleshooting checklist
- Backend started from repo root so `.env` loads.
- `TOKEN_MASTER_KEY` set and unchanged since tokens were stored.
- `GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI` match your Google OAuth app and consent screen.
- After code changes, restart API and poller to pick up updates.

## File reference
- XOAUTH2 helper: `modules/gmail_xoauth2.py`
- Poller: `scripts/run_imap_poller.py`
- Backend routes: `api/routes.py` (connect/test/poller endpoints)
- Frontend: `frontend/` (Vite React UI)
