"""Database session management and engine initialization."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings
from app.database.models import Base

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine for SQLite (using aiosqlite)
engine = create_async_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}, # Required for SQLite multi-thread access
    echo=False,
)

# Async session factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all SQLite database tables if they do not exist.

    Uses SQLAlchemy metadata reflection to create the schema asynchronously.
    """
    logger.info("Initializing SQLite database schema...")
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")
