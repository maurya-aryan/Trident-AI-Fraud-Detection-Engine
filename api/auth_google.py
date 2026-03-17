import os
import json
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict

import core.token_store as token_store

# Conditional imports to avoid crash if dependencies not fully built yet in background
try:
    from google_auth_oauthlib.flow import Flow
except ImportError:
    Flow = None

router = APIRouter()

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ConnectBasic(BaseModel):
    owner_id: str
    email: str
    host: str
    password: str

class DisconnectRequest(BaseModel):
    owner_id: str

# ---------------------------------------------------------------------------
# OAuth Helpers
# ---------------------------------------------------------------------------

def _get_google_client_config():
    """Builds client config from env vars."""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    if not client_id or not client_secret:
        return None
    return {
        "web": {
            "client_id": client_id,
            "project_id": "trident-ai",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
        }
    }

# ---------------------------------------------------------------------------
# OAuth Endpoints
# ---------------------------------------------------------------------------

@router.get("/google/start", tags=["Auth"])
async def google_auth_start(
    owner_id: str = Query(..., description="Unique ID for this mailbox/user"),
    redirect_frontend: Optional[str] = Query(None, description="Frontend URL to return to")
):
    """
    Starts Google OAuth flow. Redirects user to Google Consent screen.
    """
    if not Flow:
        raise HTTPException(status_code=500, detail="google-auth-oauthlib and encryption aren't ready.")
        
    client_config = _get_google_client_config()
    if not client_config:
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth Credentials missing: set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars."
        )

    # Scopes needed for IMAP XOAUTH2 + email for userinfo
    scopes = ['https://mail.google.com/', 'openid', 'https://www.googleapis.com/auth/userinfo.email']
    
    # Callback URI
    # In production, this should be the public API URL.
    # We can read from environment or construct.
    redirect_uri = os.environ.get('TRIDENT_API_URL', 'http://localhost:8000') + '/auth/google/callback'

    flow = Flow.from_client_config(
        client_config,
        scopes=scopes,
        redirect_uri=redirect_uri
    )

    # Generate authorization URL with PKCE code_verifier
    auth_url, state_token = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent' # force refresh token
    )

    # We need to pass the code_verifier to the callback — store it in the state
    # The flow object generates code_verifier internally; extract it
    code_verifier = flow.code_verifier

    # Build state that carries owner_id, redirect, and code_verifier
    state_payload = {
        "owner_id": owner_id,
        "redirect_frontend": redirect_frontend,
        "code_verifier": code_verifier,
    }
    import urllib.parse
    # Re-build auth_url with our custom state
    parsed = urllib.parse.urlparse(auth_url)
    params = dict(urllib.parse.parse_qsl(parsed.query))
    params['state'] = json.dumps(state_payload)
    new_query = urllib.parse.urlencode(params)
    auth_url = urllib.parse.urlunparse(parsed._replace(query=new_query))

    return RedirectResponse(auth_url)


@router.get("/google/callback", tags=["Auth"])
async def google_auth_callback(request: Request):
    """
    Google OAuth callback endpoint.
    Recieves authorization code, exchanges for tokens, and stores them.
    """
    if not Flow:
        raise HTTPException(status_code=500, detail="google-auth-oauthlib isn't ready.")

    state_str = request.query_params.get('state')
    code = request.query_params.get('code')
    error = request.query_params.get('error')

    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")
    if not code or not state_str:
        raise HTTPException(status_code=400, detail="Missing code or state in callback.")

    try:
        state_payload = json.loads(state_str)
        owner_id = state_payload.get('owner_id')
        redirect_frontend = state_payload.get('redirect_frontend')
        code_verifier = state_payload.get('code_verifier')
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid state payload.")

    client_config = _get_google_client_config()
    redirect_uri = os.environ.get('TRIDENT_API_URL', 'http://localhost:8000') + '/auth/google/callback'

    flow = Flow.from_client_config(
        client_config,
        scopes=['https://mail.google.com/', 'openid', 'https://www.googleapis.com/auth/userinfo.email'],
        redirect_uri=redirect_uri
    )
    # Restore the code_verifier from state
    flow.code_verifier = code_verifier
    
    # Exchange code for tokens
    # Note: request.url is typically https if behind proxy, but here might be http local
    # If using HTTP locally, OAuth lib might complain unless OAUTHLIB_INSECURE_TRANSPORT is set.
    # We can force it in code or let operator set it.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # allow local http testing
    
    flow.fetch_token(code=code)
    credentials = flow.credentials

    if not credentials.refresh_token:
        raise HTTPException(status_code=400, detail="No refresh token returned from Google. Revoke access and try again.")

    # Fetch user's email from Google userinfo endpoint
    import requests as req
    try:
        userinfo_resp = req.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        user_email = userinfo_resp.json().get('email', owner_id)
    except Exception:
        user_email = owner_id  # fallback

    # Save to encrypted store
    token_store.save_credentials(
        owner_id=owner_id,
        provider='google',
        email=user_email,
        secret=credentials.refresh_token,
        meta={
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
        }
    )

    if redirect_frontend:
        # Redirect back with a success param
        separator = '&' if '?' in redirect_frontend else '?'
        return RedirectResponse(f"{redirect_frontend}{separator}connected=google")
    
    return {"status": "ok", "message": "Google Account connected successfully and token stored."}

# ---------------------------------------------------------------------------
# Basic Auth & Disconnect
# ---------------------------------------------------------------------------

@router.post("/connect/basic", tags=["Auth"])
async def connect_basic(payload: ConnectBasic):
    """Stores an app-password or standard credentials encrypted."""
    try:
        token_store.save_credentials(
            owner_id=payload.owner_id,
            provider='basic',
            email=payload.email,
            secret=payload.password,
            meta={"host": payload.host}
        )
        return {"status": "ok", "message": f"Basic credentials stored for {payload.email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect", tags=["Auth"])
async def disconnect(payload: DisconnectRequest):
    """Deletes stored credentials for an owner."""
    try:
        token_store.delete_credentials(payload.owner_id)
        return {"status": "ok", "message": "Credentials disconnected."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# Test Connection Endpoint
# ---------------------------------------------------------------------------

@router.post("/poller/connect-test", tags=["Auth"])
async def test_connection(owner_id: str):
    """Attempts to connect to IMAP with stored credentials to verify them."""
    import imaplib
    import base64
    import requests

    creds = token_store.get_credentials(owner_id)
    if not creds:
        raise HTTPException(status_code=404, detail="No credentials found for this owner.")

    try:
        if creds['provider'] == 'google':
            # Refresh token to get access token
            refresh_token = creds['secret']
            client_id = creds['meta'].get('client_id')
            client_secret = creds['meta'].get('client_secret')
            token_uri = creds['meta'].get('token_uri')

            # Build refresh request
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
            }
            r = requests.post(token_uri, data=data)
            if r.status_code != 200:
                raise Exception(f"Failed to refresh Google token: {r.text}")
            
            access_token = r.json().get('access_token')

            # XOAUTH2 — imaplib does the base64 encoding
            auth_str = f"user={creds['email']}\x01auth=Bearer {access_token}\x01\x01"

            M = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            M.authenticate('XOAUTH2', lambda x: auth_str.encode())
            M.select('INBOX')
            M.logout()
            return {"status": "success", "message": "Connected successfully to IMAP via XOAUTH2"}

        elif creds['provider'] == 'basic':
            host = creds['meta'].get('host', 'imap.gmail.com')
            M = imaplib.IMAP4_SSL(host, 993)
            M.login(creds['email'], creds['secret'])
            M.select('INBOX')
            M.logout()
            return {"status": "success", "message": "Connected successfully to IMAP via Basic Auth"}

        else:
            raise Exception("Unknown provider")

    except Exception as e:
        return {"status": "failure", "message": f"Connection failed: {e}"}

@router.get("/status", tags=["Auth"])
async def auth_status(owner_id: str):
    """Checks if credentials exist for the owner."""
    try:
        creds = token_store.get_credentials(owner_id)
        if creds:
            return {"connected": True, "provider": creds['provider'], "email": creds['email']}
        return {"connected": False}
    except Exception as e:
        return {"connected": False, "error": str(e)}
