"""FastAPI application factory.

Keeps ``main.py`` a trivial entry point and keeps app construction
(middleware, routers, startup/shutdown hooks) in one testable place.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Run startup and shutdown logic around the application's lifetime.

    Milestone 0 only logs startup/shutdown. Future milestones will start
    and stop the simulation loop here (World, Scheduler, EventBus, ...).
    """
    settings = get_settings()
    setup_logging(settings)
    logger.info("Starting %s (environment=%s)", settings.app_name, settings.environment)

    yield

    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.include_router(health_router)

    return app
