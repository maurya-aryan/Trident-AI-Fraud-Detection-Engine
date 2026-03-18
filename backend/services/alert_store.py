"""
TRIDENT Alert Storage Service

SQLite-backed alert persistence replacing in-memory list.
Provides CRUD operations for alert management.
"""
import json
import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from core.data_models import TridentResult
from backend.database import get_db

logger = logging.getLogger(__name__)


def save_alert(
    alert: TridentResult,
    subject: Optional[str] = None,
    sender: Optional[str] = None,
) -> str:
    """
    Save a TridentResult alert to the database.

    Args:
        alert: TridentResult object to save
        subject: Email subject line (optional, extracted from context)
        sender: Email sender address (optional, extracted from context)

    Returns:
        str: The alert ID

    Raises:
        Exception: If database insert fails
    """
    try:
        # Generate unique alert ID
        alert_id = str(uuid.uuid4())

        # Serialize TridentResult to JSON
        result_json = alert.model_dump_json()

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO alerts (id, timestamp, subject, sender, risk_score, bucket, result_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert_id,
                    alert.timestamp,
                    subject or "Unknown Subject",
                    sender or "Unknown Sender",
                    alert.risk_score,
                    alert.risk_band,
                    result_json,
                ),
            )
            conn.commit()

        logger.info(f"Saved alert {alert_id} - {alert.risk_band} ({alert.risk_score:.1f})")
        return alert_id

    except Exception as e:
        logger.error(f"Failed to save alert: {e}")
        raise


def get_alerts(
    bucket: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Retrieve alerts from the database with optional filtering.

    Args:
        bucket: Filter by risk band (CRITICAL, HIGH, MEDIUM, LOW). None = all alerts.
        limit: Maximum number of alerts to return (default 100)
        offset: Number of alerts to skip for pagination

    Returns:
        List of alert dictionaries with full TridentResult data

    Example:
        # Get all CRITICAL alerts
        critical_alerts = get_alerts(bucket="CRITICAL", limit=50)

        # Get most recent 10 alerts of any type
        recent = get_alerts(limit=10)
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # Build query with optional bucket filter
            if bucket:
                query = """
                    SELECT id, timestamp, subject, sender, risk_score, bucket, result_json
                    FROM alerts
                    WHERE bucket = ?
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """
                cursor.execute(query, (bucket.upper(), limit, offset))
            else:
                query = """
                    SELECT id, timestamp, subject, sender, risk_score, bucket, result_json
                    FROM alerts
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """
                cursor.execute(query, (limit, offset))

            rows = cursor.fetchall()

            # Convert rows to dictionaries
            alerts = []
            for row in rows:
                alert_dict = {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "subject": row["subject"],
                    "sender": row["sender"],
                    "risk_score": row["risk_score"],
                    "bucket": row["bucket"],
                    "result": json.loads(row["result_json"]),
                }
                alerts.append(alert_dict)

            logger.debug(
                f"Retrieved {len(alerts)} alerts "
                f"(bucket={bucket}, limit={limit}, offset={offset})"
            )
            return alerts

    except Exception as e:
        logger.error(f"Failed to retrieve alerts: {e}")
        raise


def get_alert_by_id(alert_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific alert by ID.

    Args:
        alert_id: Unique alert identifier

    Returns:
        Alert dictionary with full TridentResult data, or None if not found
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, timestamp, subject, sender, risk_score, bucket, result_json
                FROM alerts
                WHERE id = ?
                """,
                (alert_id,),
            )
            row = cursor.fetchone()

            if not row:
                logger.warning(f"Alert {alert_id} not found")
                return None

            alert_dict = {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "subject": row["subject"],
                "sender": row["sender"],
                "risk_score": row["risk_score"],
                "bucket": row["bucket"],
                "result": json.loads(row["result_json"]),
            }

            logger.debug(f"Retrieved alert {alert_id}")
            return alert_dict

    except Exception as e:
        logger.error(f"Failed to retrieve alert {alert_id}: {e}")
        raise


def clear_alerts() -> int:
    """
    Delete all alerts from the database.

    Returns:
        int: Number of alerts deleted
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM alerts")
            count = cursor.fetchone()["count"]

            cursor.execute("DELETE FROM alerts")
            conn.commit()

        logger.warning(f"Cleared {count} alerts from database")
        return count

    except Exception as e:
        logger.error(f"Failed to clear alerts: {e}")
        raise


def get_alerts_count(bucket: Optional[str] = None) -> int:
    """
    Get the total count of alerts, optionally filtered by bucket.

    Args:
        bucket: Filter by risk band (CRITICAL, HIGH, MEDIUM, LOW). None = all alerts.

    Returns:
        int: Total count of alerts
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            if bucket:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM alerts WHERE bucket = ?",
                    (bucket.upper(),),
                )
            else:
                cursor.execute("SELECT COUNT(*) as count FROM alerts")

            result = cursor.fetchone()
            return result["count"]

    except Exception as e:
        logger.error(f"Failed to count alerts: {e}")
        raise


def get_alerts_stats() -> Dict[str, Any]:
    """
    Get aggregate statistics about alerts.

    Returns:
        Dictionary with total count, counts per bucket, and average risk scores
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM alerts")
            total = cursor.fetchone()["total"]

            # Get counts and averages per bucket
            cursor.execute(
                """
                SELECT bucket, COUNT(*) as count, AVG(risk_score) as avg_score
                FROM alerts
                GROUP BY bucket
                """
            )
            bucket_stats = {
                row["bucket"]: {
                    "count": row["count"],
                    "avg_score": round(row["avg_score"], 2),
                }
                for row in cursor.fetchall()
            }

            return {
                "total": total,
                "by_bucket": bucket_stats,
            }

    except Exception as e:
        logger.error(f"Failed to get alert stats: {e}")
        raise
