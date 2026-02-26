"""
TRIDENT FastAPI Routes
"""
import logging
import os
import tempfile
from typing import Dict, Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core.data_models import FraudSignal, TridentResult
from core.trident import TRIDENT
from datetime import datetime
import threading

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

# Initialise TRIDENT (singleton)
_trident: Optional[TRIDENT] = None


def get_trident() -> TRIDENT:
    global _trident
    if _trident is None:
        _trident = TRIDENT()
    return _trident


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


@app.get("/campaign-status", tags=["Detection"])
async def campaign_status() -> Dict:
    """Get current campaign graph correlation status."""
    try:
        trident = get_trident()
        return trident.graph.correlate()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
