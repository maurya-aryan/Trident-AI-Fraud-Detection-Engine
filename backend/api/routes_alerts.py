"""
TRIDENT Alerts Routes

Alert management endpoints with SQLite persistence.
"""
import logging
from typing import Dict, List, Any

from fastapi import APIRouter, HTTPException, Query

from backend.services import alert_store
from core.data_models import TridentResult

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Alerts"])


@router.post("/alerts")
async def push_alert(alert: Dict) -> Dict:
    """
    Push a small alert object (used by ingest runners).

    Expected fields:
    - subject: Email subject line
    - sender: Email sender address
    - risk_score: Risk score (0-100)
    - risk_band: CRITICAL/HIGH/MEDIUM/LOW
    - trident_result: Full TridentResult dict
    """
    if not isinstance(alert, dict):
        raise HTTPException(status_code=400, detail="alert must be a JSON object")

    try:
        # Extract TridentResult from nested structure
        trident_result = alert.get("trident_result")
        if not trident_result:
            raise HTTPException(status_code=400, detail="trident_result field required")

        # Convert dict to TridentResult object
        result_obj = TridentResult(**trident_result)

        # Save to database
        alert_id = alert_store.save_alert(
            alert=result_obj,
            subject=alert.get("subject"),
            sender=alert.get("sender"),
        )

        return {"status": "ok", "stored": True, "alert_id": alert_id}

    except Exception as exc:
        logger.exception("Error saving alert")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/alerts")
async def get_alerts(
    bucket: str = Query(None, description="Filter by risk band (CRITICAL/HIGH/MEDIUM/LOW)"),
    limit: int = Query(100, ge=1, le=500, description="Max alerts to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> Dict[str, Any]:
    """
    Return recent alerts with optional filtering.

    Query params:
    - bucket: Filter by risk band (optional)
    - limit: Maximum number of alerts (default 100, max 500)
    - offset: Number to skip for pagination
    """
    try:
        alerts = alert_store.get_alerts(bucket=bucket, limit=limit, offset=offset)
        total = alert_store.get_alerts_count(bucket=bucket)

        return {
            "count": len(alerts),
            "total": total,
            "offset": offset,
            "alerts": alerts,
        }

    except Exception as exc:
        logger.exception("Error retrieving alerts")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/alerts/{alert_id}")
async def get_alert_by_id(alert_id: str) -> Dict[str, Any]:
    """Get a specific alert by its ID."""
    try:
        alert = alert_store.get_alert_by_id(alert_id)

        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

        return alert

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Error retrieving alert {alert_id}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/alerts/stats")
async def get_alert_stats() -> Dict[str, Any]:
    """
    Get aggregate alert statistics.

    Returns:
    - total: Total alert count
    - by_bucket: Counts and average scores per risk band
    """
    try:
        stats = alert_store.get_alerts_stats()
        return stats

    except Exception as exc:
        logger.exception("Error retrieving alert stats")
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/alerts")
async def clear_alerts() -> Dict:
    """Clear all stored alerts from the database."""
    try:
        count = alert_store.clear_alerts()
        return {"status": "ok", "cleared": count}

    except Exception as exc:
        logger.exception("Error clearing alerts")
        raise HTTPException(status_code=500, detail=str(exc))
