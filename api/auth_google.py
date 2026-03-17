import config  # Triggers manual .env loading
import json
import logging
import os
import urllib.parse
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/google", tags=["OAuth"])

# Will read from os.environ dynamically per request

# Scope required for IMAP XOAUTH2 access to Gmail
SCOPES = [
    "https://mail.google.com/",
    "openid",
    "email",
]

GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"


def _get_token_store():
    """Lazy import and dynamic key retrieval to handle runtime env changes."""
    from core.token_store import TokenStore
    key = os.environ.get("TOKEN_MASTER_KEY", "").strip()
    return TokenStore(master_key=key if key else None)


@router.get("/start")
async def google_oauth_start(
    owner_id: str = "default",
    redirect_frontend: str = "http://localhost:5173",
):
    """
    Build a Google OAuth consent URL and return it.
    The frontend should open this URL in a new tab / popup.
    """
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    
    if not client_id:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLIENT_ID not configured on server",
        )

    # Encode owner_id and return URL in state param
    state = json.dumps({"owner_id": owner_id, "return_to": redirect_frontend})

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    }
    auth_url = f"{GOOGLE_AUTH_URI}?{urllib.parse.urlencode(params)}"
    return {"auth_url": auth_url}


@router.get("/callback")
async def google_oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
):
    """
    Handle the OAuth callback from Google.
    Exchange the authorisation code for tokens, store the refresh token
    encrypted, and redirect the user back to the frontend.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")

    # Parse state
    try:
        state_data = json.loads(state)
        owner_id = state_data.get("owner_id", "default")
        return_to = state_data.get("return_to", "http://localhost:5173")
    except (json.JSONDecodeError, TypeError):
        owner_id = "default"
        return_to = "http://localhost:5173"

    # Exchange code for tokens
    import requests as req

    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

    token_data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    try:
        resp = req.post(GOOGLE_TOKEN_URI, data=token_data, timeout=15)
        resp.raise_for_status()
        tokens = resp.json()
    except Exception as exc:
        logger.exception("Token exchange failed")
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {exc}")

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="No refresh_token returned. Re-consent may be needed.",
        )

    # Try to get user email from id_token or userinfo
    email = ""
    id_token_payload = tokens.get("id_token")
    if id_token_payload:
        try:
            # Decode JWT payload (no verification – just to read email claim)
            import base64
            payload_b64 = id_token_payload.split(".")[1]
            # Fix padding
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            claims = json.loads(base64.urlsafe_b64decode(payload_b64))
            email = claims.get("email", "")
        except Exception:
            pass

    # Fallback: fetch from userinfo endpoint
    if not email:
        try:
            access_token = tokens.get("access_token", "")
            userinfo = req.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            ).json()
            email = userinfo.get("email", "")
        except Exception:
            pass

    # Store refresh token encrypted
    try:
        store = _get_token_store()
        store.save_credentials(
            owner_id=owner_id,
            provider="google",
            email=email,
            secret=refresh_token,
            meta={"host": "imap.gmail.com", "port": 993},
        )
    except Exception as exc:
        logger.exception("Failed to store credentials")
        raise HTTPException(status_code=500, detail=f"Failed to store credentials: {exc}")

    # Redirect back to frontend with success flag
    separator = "&" if "?" in return_to else "?"
    redirect_url = f"{return_to}{separator}connected=1&email={urllib.parse.quote(email)}"
    return RedirectResponse(url=redirect_url, status_code=302)
