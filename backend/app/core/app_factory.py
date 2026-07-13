"""FastAPI application factory.

Keeps ``main.py`` a trivial entry point and keeps app construction
(middleware, routers, startup/shutdown hooks) in one testable place.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)


async def simulation_loop(app: FastAPI) -> None:
    """Asynchronous background loop task. Ticks the simulation every 30 seconds if running."""
    logger.info("Simulation loop worker started.")
    while True:
        try:
            await asyncio.sleep(30.0)
            if hasattr(app.state, "game") and app.state.game.world.is_running:
                # Advance simulation by exactly one tick
                app.state.game.world.tick()

                # Persist updated simulation frame to SQLite
                if hasattr(app.state, "db_repo"):
                    await app.state.db_repo.save_world(app.state.game.world)
        except asyncio.CancelledError:
            logger.info("Simulation loop worker cancelled.")
            break
        except Exception as e:
            logger.error("Error inside simulation worker tick: %s", str(e))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Run startup and shutdown logic around the application's lifetime."""
    settings = get_settings()
    setup_logging(settings)
    logger.info("Starting %s (environment=%s)", settings.app_name, settings.environment)

    # 1. Initialize SQLite Database
    from app.database.session import init_db, async_session_maker
    from app.database.repositories import SimulationRepository
    
    await init_db()
    db_repo = SimulationRepository(async_session_maker)
    app.state.db_repo = db_repo

    # 2. Construct the global Game object graph (demo=False for production)
    from app.bootstrap.game_factory import GameFactory
    game = GameFactory.build(demo=False)
    game.world.db_repo = db_repo
    app.state.game = game

    # 3. Load saved state from database or seed it
    loaded = await db_repo.load_world(game.world)
    if not loaded:
        logger.info("First boot detected. Seeding initial world state into SQLite...")
        await db_repo.save_world(game.world)

    # Start simulation world
    app.state.game.world.start()

    # Start simulation background loop
    loop_task = asyncio.create_task(simulation_loop(app))

    yield

    # Cancel task on shutdown
    loop_task.cancel()
    await asyncio.gather(loop_task, return_exceptions=True)

    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Enable CORS for cross-origin frontend requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)

    from app.api.command import router as command_router
    app.include_router(command_router)

    from app.api.simulation import router as simulation_router
    app.include_router(simulation_router)

    from app.api.websocket import router as websocket_router
    app.include_router(websocket_router)

    return app
