"""
TRIDENT Database Setup - SQLite for Alerts Persistence

Replaces in-memory alert storage with durable SQLite database.
"""
import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from backend.config import settings

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = Path(settings.DATABASE_URL.replace("sqlite:///", ""))


def _get_connection() -> sqlite3.Connection:
    """Create a database connection with proper configuration."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
    conn.execute("PRAGMA foreign_keys=ON")  # Enable foreign key constraints
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Database connection context manager.

    Usage:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts")
            results = cursor.fetchall()
    """
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """
    Initialize the database and create tables if they don't exist.

    Alerts table schema:
      - id: Unique alert identifier (TEXT PRIMARY KEY)
      - timestamp: ISO 8601 timestamp of when alert was created
      - subject: Email subject line (for display in UI)
      - sender: Email sender address
      - risk_score: Risk score (0-100)
      - bucket: Risk band (CRITICAL/HIGH/MEDIUM/LOW)
      - result_json: Full TridentResult as JSON string
    """
    try:
        # Ensure parent directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        with get_db() as conn:
            cursor = conn.cursor()

            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    subject TEXT,
                    sender TEXT,
                    risk_score REAL NOT NULL,
                    bucket TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indices for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp
                ON alerts(timestamp DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_bucket
                ON alerts(bucket)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_risk_score
                ON alerts(risk_score DESC)
            """)

            conn.commit()
            logger.info(f"Database initialized at {DB_PATH}")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def reset_db() -> None:
    """
    Reset the database by dropping and recreating all tables.
    WARNING: This will delete all data!
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS alerts")
            conn.commit()

        logger.warning("Database reset - all tables dropped")
        init_db()

    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        raise


# Initialize database on module import
init_db()
