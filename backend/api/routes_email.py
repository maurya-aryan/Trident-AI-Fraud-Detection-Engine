"""
TRIDENT Detection Routes

Email fraud detection endpoints.
"""
import logging
import os
import tempfile
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, File, Query, UploadFile

from core.data_models import FraudSignal, TridentResult
from core.trident import TRIDENT

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Detection"])

# TRIDENT singleton instance
_trident: Optional[TRIDENT] = None


def get_trident() -> TRIDENT:
    """Get or create the global TRIDENT instance."""
    global _trident
    if _trident is None:
        _trident = TRIDENT()
        logger.info("TRIDENT engine initialized")
    return _trident


@router.post("/detect", response_model=TridentResult)
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


@router.post("/analyze-email")
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


@router.post("/analyze-url")
async def analyze_url(
    url: str = Query(..., description="URL to analyse")
) -> Dict:
    """Analyse a single URL for malicious indicators."""
    try:
        trident = get_trident()
        return trident.url_detect.detect_malicious(url)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/scan-file")
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


@router.post("/check-credentials")
async def check_credentials(
    text: str = Query(..., description="Text to scan for credentials")
) -> Dict:
    """Scan text for exposed credentials (API keys, passwords, credit cards, etc.)."""
    try:
        trident = get_trident()
        return trident.credentials.detect_credentials(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/check-injection")
async def check_injection(
    text: str = Query(..., description="Text to check for prompt injection")
) -> Dict:
    """Check text for prompt injection / jailbreak patterns."""
    try:
        trident = get_trident()
        return trident.injection.detect_injection(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/reset-graph")
async def reset_campaign_graph() -> Dict:
    """Reset the campaign correlation graph (start new session)."""
    try:
        trident = get_trident()
        trident.reset_graph()
        return {"status": "graph_reset", "message": "Campaign graph cleared."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/campaign-status")
async def campaign_status() -> Dict:
    """Get current campaign graph correlation status."""
    try:
        trident = get_trident()
        return trident.graph.correlate()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
