"""Application configuration.

Settings are loaded once from environment variables (and an optional .env
file) and exposed as a single immutable ``Settings`` instance via
``get_settings``. Other modules never read environment variables directly —
they depend on ``Settings`` through FastAPI's dependency injection.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Immutable application settings.

    Values are resolved in this order: environment variables, then a
    ``.env`` file in the backend root, then the defaults declared below.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "EchoCity"
    environment: str = Field(default="development")
    debug: bool = Field(default=True)

    # --- API ---
    api_host: str = Field(default="127.0.0.1")
    api_port: int = Field(default=8000)

    # --- Logging ---
    log_level: str = Field(default="INFO")

    # --- Database (placeholder; wired up in Milestone 2) ---
    database_url: str = Field(default="sqlite+aiosqlite:///./echocity.db")

    # --- Ollama ---
    ollama_model: str = Field(default="smollm2:1.7b-instruct")
    ollama_base_url: str = Field(default="http://localhost:11434")


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide ``Settings`` instance.

    Cached with ``lru_cache`` so the environment/`.env` file is parsed only
    once, while still being accessible through FastAPI's ``Depends`` for
    testability (it can be overridden per-test via dependency overrides).
    """
    return Settings()
