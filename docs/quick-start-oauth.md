# Quick-Start: OAuth + IMAP (XOAUTH2) for TRIDENT

This guide explains how to set up OAuth-based mailbox authentication so users connect once via a browser and never manually edit env vars.

---

## 1. Generate a Master Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Store the output in your environment:

```bash
# .env or system env
TOKEN_MASTER_KEY=<generated-key>
```

> **Important**: Keep this key safe. It encrypts all stored credentials. If lost, stored tokens become unreadable and users must reconnect.

---

## 2. Set Up Google Cloud OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new **OAuth 2.0 Client ID** (type: Web application)
3. Set **Authorized redirect URI** to: `http://localhost:8000/auth/google/callback`
4. Note the **Client ID** and **Client Secret**
5. Add them to your environment:

```bash
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

6. Under **OAuth consent screen**, add test users (unless your app is verified by Google)

---

## 3. Run the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py api

# In a separate terminal, start the frontend
cd frontend && npm run dev
```

---

## 4. Connect a Mailbox

### Option A: Google OAuth (recommended)
1. Open the frontend (`http://localhost:5173`)
2. Scroll to **Live Detection** section
3. Click **Connect with Google**
4. Complete the Google consent flow
5. You'll be redirected back with a success message

### Option B: App Password (fallback)
1. Switch to the **APP PASSWORD** tab
2. Enter your email, IMAP host, and app password
3. Click **SAVE & CONNECT**

### Test the Connection
- Click **TEST CONNECTION** — this performs a real IMAP connect and shows INBOX message count

### Disconnect
- Click **DISCONNECT** to delete stored credentials

---

## 5. Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `TOKEN_MASTER_KEY` | **Yes** | Fernet encryption key for credential storage |
| `GOOGLE_CLIENT_ID` | For OAuth | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | For OAuth | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | No | Defaults to `http://localhost:8000/auth/google/callback` |
| `IMAP_HOST` | Fallback | IMAP server (default: `imap.gmail.com`) |
| `IMAP_USER` | Fallback | Email address (env-var fallback only) |
| `IMAP_PASSWORD` | Fallback | App password (env-var fallback only) |

---

## 6. Security Notes

- Refresh tokens and app passwords are encrypted at rest using Fernet (AES-128-CBC)
- The master key (`TOKEN_MASTER_KEY`) should be stored in a secret manager or `.env` file excluded from git
- `data/tokens.json` is gitignored by default
- Users can revoke access from [Google Account Permissions](https://myaccount.google.com/permissions) at any time
- The **DISCONNECT** button deletes stored tokens server-side

---

## 7. API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/auth/google/start` | Returns Google OAuth consent URL |
| GET | `/auth/google/callback` | Handles OAuth code exchange |
| POST | `/connect/basic` | Stores app-password credentials |
| POST | `/poller/connect-test` | Tests IMAP connection with stored creds |
| POST | `/auth/disconnect` | Deletes stored credentials |
