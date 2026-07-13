"""Entry point for the EchoCity backend.

Run with:
    uv run python -m app.main
"""

import uvicorn

from app.core.app_factory import create_app
from app.core.config import get_settings

app = create_app()


def run() -> None:
    """Start the Uvicorn server using the configured host and port."""
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
