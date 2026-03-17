"""
TRIDENT FastAPI Routes
"""
import asyncio
import base64
import imaplib
import json
import logging
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Dict, Optional, Set

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from core.data_models import FraudSignal, TridentResult
from core.trident import TRIDENT
from datetime import datetime
import threading

# ---------------------------------------------------------------------------
# Poller process management
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
POLLER_SCRIPT = ROOT_DIR / "scripts" / "run_imap_poller.py"
_poller_proc: Optional[subprocess.Popen] = None
_poller_thread: Optional[threading.Thread] = None
_stream_subscribers: Set[asyncio.Queue] = set()
_stream_lock = threading.Lock()

ENV_ALLOWLIST = {
    "IMAP_HOST",
    "IMAP_USER",
    "IMAP_PASSWORD",
    "IMAP_POLL_INTERVAL",
    "IMAP_MARK_SEEN",
    "TRIDENT_URL",
    "ALERTS_URL",
    "PYTHONUNBUFFERED",
    "TOKEN_MASTER_KEY",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REDIRECT_URI",
}


class PollerStart(BaseModel):
    env_overrides: Optional[Dict[str, str]] = None


class BasicConnect(BaseModel):
    owner_id: str = "default"
    provider: str = "basic"
    email: str
    host: str = "imap.gmail.com"
    password: str


def _broadcast(payload: Dict):
    """Send a message to all SSE subscribers."""
    try:
        message = json.dumps(payload)
    except Exception:
        return
    with _stream_lock:
        subs = list(_stream_subscribers)
    for q in subs:
        try:
            q.put_nowait(message)
        except Exception:
            continue


def _reader_loop(proc: subprocess.Popen):
    """Read stdout/stderr lines from the poller process and broadcast."""
    try:
        for raw in iter(proc.stdout.readline, ""):
            if raw is None:
                break
            line = raw.rstrip("\n")
            if not line:
                continue
            _broadcast({"type": "line", "data": line})
    finally:
        code = proc.poll()
        _broadcast({"type": "status", "data": "stopped", "exit_code": code})
        proc.stdout and proc.stdout.close()


def _start_poller(env_overrides: Optional[Dict[str, str]] = None):
    global _poller_proc, _poller_thread
    if _poller_proc and _poller_proc.poll() is None:
        raise RuntimeError("poller already running")

    if not POLLER_SCRIPT.exists():
        raise RuntimeError(f"poller script missing: {POLLER_SCRIPT}")

    env = os.environ.copy()
    for k, v in (env_overrides or {}).items():
        if k in ENV_ALLOWLIST:
            env[k] = v

    cmd = [sys.executable, str(POLLER_SCRIPT)]
    _poller_proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        text=True,
    )

    _broadcast({"type": "status", "data": "started", "pid": _poller_proc.pid})
    _poller_thread = threading.Thread(target=_reader_loop, args=(_poller_proc,), daemon=True)
    _poller_thread.start()


def _stop_poller():
    global _poller_proc
    proc = _poller_proc
    if not proc or proc.poll() is not None:
        raise RuntimeError("poller not running")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    _broadcast({"type": "status", "data": "stopped", "exit_code": proc.poll()})

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="TRIDENT AI-Fraud Detection API",
    description="Multi-modal fraud detection engine with 9 independent modules.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Google OAuth router
try:
    from api.auth_google import router as auth_google_router
    app.include_router(auth_google_router)
except Exception as _auth_err:
    logging.getLogger(__name__).warning("Could not mount auth_google router: %s", _auth_err)

# Initialise TRIDENT (singleton)
_trident: Optional[TRIDENT] = None


def get_trident() -> TRIDENT:
    global _trident
    if _trident is None:
        _trident = TRIDENT()
    return _trident


def _poller_running() -> bool:
    return _poller_proc is not None and _poller_proc.poll() is None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"])
async def health() -> Dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "TRIDENT",
        "version": "1.0.0",
    }


@app.post("/detect", response_model=TridentResult, tags=["Detection"])
async def detect_fraud(signal: FraudSignal) -> TridentResult:
    """
    Full fraud detection pipeline.
    Accepts email text, URL, and/or attachment path.
    Returns unified risk score + explanations.
    """
    try:
        trident = get_trident()
        result = trident.detect_fraud(signal)
        return result
    except Exception as exc:
        logger.exception("Error in detect_fraud")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/analyze-email", tags=["Detection"])
async def analyze_email(
    text: str = Query(..., description="Email body text to analyse")
) -> Dict:
    """Analyse email text only (AI detection + phishing + credentials + injection)."""
    try:
        trident = get_trident()
        signal = FraudSignal(email_text=text)
        result = trident.detect_fraud(signal)
        return {
            "risk_score": result.risk_score,
            "risk_band": result.risk_band,
            "recommended_action": result.recommended_action,
            "module_scores": result.module_scores,
            "module_details": result.module_details,
            "explanation": result.explanation,
            "top_factors": result.top_factors,
        }
    except Exception as exc:
        logger.exception("Error in analyze_email")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/analyze-url", tags=["Detection"])
async def analyze_url(
    url: str = Query(..., description="URL to analyse")
) -> Dict:
    """Analyse a single URL for malicious indicators."""
    try:
        trident = get_trident()
        return trident.url_detect.detect_malicious(url)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# Simple in-memory alerts store for local dev / UI popups.
# In production this should be backed by a durable store (Postgres/Redis).
_alerts: list = []
_alerts_lock = threading.Lock()


@app.post("/alerts", tags=["Alerts"])
async def push_alert(alert: Dict) -> Dict:
    """Push a small alert object (used by ingest runners)"""
    # Basic validation (expecting keys: subject, sender, risk_score, risk_band)
    if not isinstance(alert, dict):
        raise HTTPException(status_code=400, detail="alert must be a JSON object")
    entry = {"received_at": datetime.utcnow().isoformat() + "Z", "alert": alert}
    with _alerts_lock:
        _alerts.append(entry)
        # keep last 200
        if len(_alerts) > 200:
            _alerts[:] = _alerts[-200:]
    return {"status": "ok", "stored": True}


@app.get("/alerts", tags=["Alerts"])
async def get_alerts(limit: int = 10) -> Dict:
    """Return recent alerts (most recent first)."""
    with _alerts_lock:
        items = list(reversed(_alerts[-limit:]))
    return {"count": len(items), "alerts": items}


@app.delete("/alerts", tags=["Alerts"])
async def clear_alerts() -> Dict:
    """Clear all stored alerts."""
    with _alerts_lock:
        count = len(_alerts)
        _alerts.clear()
    return {"status": "ok", "cleared": count}


@app.post("/scan-file", tags=["Detection"])
async def scan_file(file: UploadFile = File(...)) -> Dict:
    """Upload and scan a file for malware / threats."""
    try:
        trident = get_trident()
        contents = await file.read()

        # Write to temp file
        suffix = os.path.splitext(file.filename or "upload")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            result = trident.malware.scan_attachment(tmp_path)
            result["original_filename"] = file.filename
            return result
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    except Exception as exc:
        logger.exception("Error in scan_file")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/check-credentials", tags=["Detection"])
async def check_credentials(
    text: str = Query(..., description="Text to scan for credentials")
) -> Dict:
    """Scan text for exposed credentials (API keys, passwords, credit cards, etc.)."""
    try:
        trident = get_trident()
        return trident.credentials.detect_credentials(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/check-injection", tags=["Detection"])
async def check_injection(
    text: str = Query(..., description="Text to check for prompt injection")
) -> Dict:
    """Check text for prompt injection / jailbreak patterns."""
    try:
        trident = get_trident()
        return trident.injection.detect_injection(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/reset-graph", tags=["System"])
async def reset_campaign_graph() -> Dict:
    """Reset the campaign correlation graph (start new session)."""
    try:
        trident = get_trident()
        trident.reset_graph()
        return {"status": "graph_reset", "message": "Campaign graph cleared."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# IMAP poller control + streaming output
# ---------------------------------------------------------------------------


@app.post("/poller/start", tags=["Poller"])
async def poller_start(payload: PollerStart) -> Dict:
    """Start the IMAP poller process, inheriting env plus optional overrides."""
    try:
        _start_poller(payload.env_overrides)
        return {
            "status": "started",
            "pid": _poller_proc.pid if _poller_proc else None,
            "running": _poller_running(),
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.exception("Failed to start poller")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/poller/stop", tags=["Poller"])
async def poller_stop() -> Dict:
    """Stop the IMAP poller process if running."""
    try:
        _stop_poller()
        return {"status": "stopped"}
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.exception("Failed to stop poller")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/poller/stream", tags=["Poller"])
async def poller_stream():
    """Server-Sent Events stream of live poller output and status."""

    async def event_stream():
        q: asyncio.Queue = asyncio.Queue()
        # seed with current status
        initial = {
            "type": "status",
            "data": "running" if _poller_running() else "stopped",
            "pid": _poller_proc.pid if _poller_proc else None,
        }
        await q.put(json.dumps(initial))

        with _stream_lock:
            _stream_subscribers.add(q)

        try:
            while True:
                msg = await q.get()
                yield f"data: {msg}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            with _stream_lock:
                _stream_subscribers.discard(q)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/campaign-status", tags=["Detection"])
async def campaign_status() -> Dict:
    """Get current campaign graph correlation status."""
    try:
        trident = get_trident()
        return trident.graph.correlate()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Mailbox connect / disconnect / test endpoints
# ---------------------------------------------------------------------------

def _get_token_store():
    from core.token_store import TokenStore
    key = os.environ.get("TOKEN_MASTER_KEY", "").strip()
    return TokenStore(master_key=key if key else None)


@app.post("/connect/basic", tags=["Mailbox"])
async def connect_basic(payload: BasicConnect) -> Dict:
    """Store app-password credentials (encrypted) for an owner."""
    try:
        store = _get_token_store()
        store.save_credentials(
            owner_id=payload.owner_id,
            provider="basic",
            email=payload.email,
            secret=payload.password,
            meta={"host": payload.host, "port": 993},
        )
        return {"status": "ok", "owner_id": payload.owner_id, "email": payload.email}
    except Exception as exc:
        logger.exception("Failed to store basic credentials")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/auth/disconnect", tags=["Mailbox"])
async def auth_disconnect(owner_id: str = "default") -> Dict:
    """Delete stored credentials/tokens for an owner."""
    try:
        store = _get_token_store()
        deleted = store.delete_credentials(owner_id)
        return {"status": "ok", "deleted": deleted}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/poller/connect-test", tags=["Mailbox"])
async def poller_connect_test(owner_id: str = "default") -> Dict:
    """
    Attempt an IMAP connection using stored credentials and return
    success/failure with a sample INBOX message count.
    """
    try:
        store = _get_token_store()
        creds = store.get_credentials(owner_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Token store error: {exc}")

    if creds is None:
        raise HTTPException(status_code=404, detail="No stored credentials for this owner")

    host = creds.get("meta", {}).get("host", "imap.gmail.com")
    port = creds.get("meta", {}).get("port", 993)
    email_addr = creds["email"]

    try:
        M = imaplib.IMAP4_SSL(host, port)

        if creds["provider"] == "google":
            # Use XOAUTH2
            from modules.gmail_xoauth2 import get_access_token, build_xoauth2_string
            access_token = get_access_token(owner_id, store)
            if not access_token:
                return {"success": False, "message": "Failed to obtain access token. Token may be revoked."}
            xoauth = build_xoauth2_string(email_addr, access_token)
            M.authenticate("XOAUTH2", lambda x: xoauth)
        else:
            # Basic auth
            M.login(email_addr, creds["secret"])

        typ, data = M.select("INBOX", readonly=True)
        msg_count = int(data[0]) if typ == "OK" else 0
        M.logout()

        return {
            "success": True,
            "message": f"Connected to {host} as {email_addr}",
            "inbox_count": msg_count,
            "provider": creds["provider"],
        }
    except Exception as exc:
        return {
            "success": False,
            "message": f"Connection failed: {exc}",
            "provider": creds["provider"],
        }
