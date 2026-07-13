"""Unit tests for the LLMService isolated reasoning layer."""

import json
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.llm.llm_service import LLMService


@pytest.mark.asyncio
async def test_llm_service_conversation_success() -> None:
    client_mock = AsyncMock()
    client_mock.generate.return_value = '{"dialogue": "Sophia: How are you? Marcus: Good."}'
    
    service = LLMService(client_mock)
    result = await service.reason("Conversation", {"speaker": "Marcus", "listener": "Sophia"})

    assert result == {"dialogue": "Sophia: How are you? Marcus: Good."}
    client_mock.generate.assert_called_once()


@pytest.mark.asyncio
async def test_llm_service_planning_success() -> None:
    client_mock = AsyncMock()
    client_mock.generate.return_value = '{"goal": "Treat patients", "focus": "Ward round", "expected_mood": "busy"}'
    
    service = LLMService(client_mock)
    result = await service.reason("Planning", {})

    assert result == {
        "goal": "Treat patients",
        "focus": "Ward round",
        "expected_mood": "busy"
    }


@pytest.mark.asyncio
async def test_llm_service_missing_keys_fallback() -> None:
    client_mock = AsyncMock()
    # Returns JSON but missing the expected mood key
    client_mock.generate.return_value = '{"goal": "Inspect vault", "focus": "Bank ledgers"}'
    
    service = LLMService(client_mock)
    result = await service.reason("Planning", {})

    assert result["goal"] == "Inspect vault"
    assert result["focus"] == "Bank ledgers"
    # Fills in fallback default value
    assert result["expected_mood"] == "calm"


@pytest.mark.asyncio
async def test_llm_service_malformed_json_fallback() -> None:
    client_mock = AsyncMock()
    client_mock.generate.return_value = "invalid text response from model"
    
    service = LLMService(client_mock)
    result = await service.reason("Higher Self Reasoning", {})

    # Falls back gracefully since it is malformed JSON
    assert result == {"narrative": "A passing thought shifts their focus."}


@pytest.mark.asyncio
async def test_llm_service_connection_error_fallback() -> None:
    client_mock = AsyncMock()
    client_mock.generate.side_effect = ConnectionError("Could not connect to Ollama")
    
    service = LLMService(client_mock)
    result = await service.reason("Crime Decision", {})

    # Falls back to standard schema keys on network failure
    assert result == {
        "commit_crime": False,
        "crime_type": "none",
        "rationale": "N/A",
        "method": "N/A"
    }
