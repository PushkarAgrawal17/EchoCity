"""Ollama client for local CPU-only Qwen inference."""

import logging
from typing import Any
import httpx

logger = logging.getLogger(__name__)


class OllamaClient:
    """Async client for interacting with the local Ollama instance.

    Uses httpx for non-blocking HTTP requests, configured with a 30s timeout
    suitable for CPU-only inference of small models.
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:3b") -> None:
        """Create an OllamaClient.

        Args:
            base_url: Base URL of the Ollama server.
            model: Model name to pull and execute (default: qwen2.5:3b).
        """
        self.base_url = base_url
        self.model = model
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def generate(
        self, prompt: str, system_prompt: str | None = None, format_type: str | None = None
    ) -> str:
        """Send a generation request to Ollama.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            format_type: Optional format constraint (e.g. "json").

        Returns:
            The raw text response from the model.

        Raises:
            httpx.HTTPError: If the request fails or returns an error code.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        if format_type:
            payload["format"] = format_type

        response = await self._client.post("/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        return str(data.get("response", ""))

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        await self._client.aclose()
