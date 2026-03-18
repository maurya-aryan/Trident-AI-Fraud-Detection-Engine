"""
TRIDENT Streamlit Dashboard Launcher

Starts the Streamlit dashboard interface for TRIDENT.

Usage:
    python scripts/run_streamlit.py
"""
import sys
import subprocess
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DASHBOARD_PATH = ROOT_DIR / "ui" / "dashboard.py"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("trident.streamlit")


def run_dashboard():
    """Launch the Streamlit dashboard."""
    if not DASHBOARD_PATH.exists():
        logger.error(f"Dashboard file not found: {DASHBOARD_PATH}")
        sys.exit(1)

    logger.info(f"Starting TRIDENT Dashboard: {DASHBOARD_PATH}")
    logger.info("Dashboard will open in your default browser...")

    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(DASHBOARD_PATH)],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Dashboard shut down by user")


if __name__ == "__main__":
    run_dashboard()
