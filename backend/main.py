"""
TRIDENT Backend - FastAPI Application Entry Point
"""
import sys
from pathlib import Path

# Ensure project root is importable
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.services.poller import get_poller

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("trident.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Manages startup and shutdown of background services.
    """
    logger.info("Starting TRIDENT application...")

    # Start IMAP poller if credentials are configured
    poller = get_poller()
    try:
        await poller.start()
        logger.info("IMAP poller started successfully")
    except Exception as e:
        logger.warning(f"Failed to start IMAP poller: {e}")
        logger.warning("Continuing without email polling - configure IMAP credentials to enable")

    yield

    logger.info("Shutting down TRIDENT application...")

    # Stop IMAP poller
    try:
        await poller.stop()
        logger.info("IMAP poller stopped")
    except Exception as e:
        logger.error(f"Error stopping poller: {e}")


# Create FastAPI application
app = FastAPI(
    title="TRIDENT AI-Fraud Detection API",
    description="Multi-modal fraud detection engine with 9 independent modules.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("TRIDENT API configured")

# Mount all API routes
from backend.api.router import router
app.include_router(router)

logger.info("API routes mounted")


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting TRIDENT API server on http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"API docs: http://localhost:{settings.API_PORT}/docs")

    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
