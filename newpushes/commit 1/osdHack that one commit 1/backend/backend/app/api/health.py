"""Health-check endpoint.

Proves the FastAPI wiring works end to end. Contains no business logic,
per the API layer rules in the backend blueprint.
"""

from fastapi import APIRouter

from app.core.dependencies import SettingsDep

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(settings: SettingsDep) -> dict[str, str]:
    """Return basic liveness information about the running application."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }
