"""Smoke test: the app builds and the health endpoint responds."""

import httpx
import pytest

from app.core.app_factory import create_app


@pytest.mark.asyncio
async def test_health_check() -> None:
    """The /health endpoint should report ok status."""
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "EchoCity"
