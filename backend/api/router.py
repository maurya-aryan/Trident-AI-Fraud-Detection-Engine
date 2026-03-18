"""
TRIDENT API Router

Central router that mounts all sub-routers.
"""
from fastapi import APIRouter

from backend.api import routes_email, routes_alerts, routes_auth

# Create main API router
router = APIRouter()

# Mount detection routes
router.include_router(routes_email.router)

# Mount alert management routes
router.include_router(routes_alerts.router)

# Mount authentication routes with /auth prefix
router.include_router(routes_auth.router, prefix="/auth")


# Health check endpoint
@router.get("/health", tags=["System"])
async def health():
    """System health check."""
    return {
        "status": "healthy",
        "service": "TRIDENT",
        "version": "1.0.0",
    }
