"""
TRIDENT Gmail XOAUTH2 Helper
Builds XOAUTH2 authentication strings for IMAP and refreshes Google
OAuth2 access tokens from stored refresh tokens.
"""
import logging
import os
import time
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)

# Google OAuth endpoints
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"

# In-memory cache: owner_id -> {access_token, expires_at}
_token_cache: Dict[str, Dict[str, Any]] = {}


def build_xoauth2_string(email: str, access_token: str) -> str:
    """
    Build the raw XOAUTH2 authentication string (not base64-encoded) suitable for
    ``imaplib.IMAP4_SSL.authenticate('XOAUTH2', ...)``.
    """
    # ``imaplib.IMAP4.authenticate`` will base64-encode the value returned by
    # the callback. We therefore return the RAW auth string here (NOT
    # base64-encoded) to avoid double-encoding which causes
    # ``Invalid SASL argument`` errors from Gmail.
    return f"user={email}\x01auth=Bearer {access_token}\x01\x01"


def refresh_google_token(
    client_id: str,
    client_secret: str,
    refresh_token: str,
) -> Dict[str, Any]:
    """
    Exchange a Google refresh token for a fresh access token.

    Returns the parsed JSON response containing ``access_token``,
    ``expires_in``, ``token_type``, etc.  Raises on HTTP error.
    """
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    resp = requests.post(GOOGLE_TOKEN_URI, data=data, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_access_token(
    owner_id: str,
    token_store,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> Optional[str]:
    """
    High-level helper: look up stored Google refresh token for *owner_id*,
    refresh it if needed, cache the result, and return an access token.

    Returns ``None`` if no credentials are stored or refresh fails.
    """
    # Check cache first
    cached = _token_cache.get(owner_id)
    if cached and cached["expires_at"] > time.time():
        return cached["access_token"]

    creds = token_store.get_credentials(owner_id)
    if creds is None or creds["provider"] != "google":
        return None

    cid = client_id or os.environ.get("GOOGLE_CLIENT_ID", "")
    csecret = client_secret or os.environ.get("GOOGLE_CLIENT_SECRET", "")
    if not cid or not csecret:
        logger.error("GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set")
        return None

    try:
        token_resp = refresh_google_token(cid, csecret, creds["secret"])
    except Exception as exc:
        logger.error("failed to refresh Google token for %s: %s", owner_id, exc)
        return None

    access_token = token_resp["access_token"]
    expires_in = token_resp.get("expires_in", 3600)
    _token_cache[owner_id] = {
        "access_token": access_token,
        "expires_at": time.time() + expires_in - 60,  # 60s safety margin
    }
    logger.info("refreshed Google access token for owner_id=%s", owner_id)
    return access_token
