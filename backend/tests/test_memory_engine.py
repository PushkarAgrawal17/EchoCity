"""Unit tests for the MemoryEngine subsystem."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.llm.llm_service import LLMService
from app.memory.memory_engine import MemoryEngine
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType
from app.memory.memory import Memory


def test_memory_engine_extract_participants() -> None:
    text = "Emma Brooks argued with Thomas near the Cafe. Marcus watched."
    participants = MemoryEngine.extract_participants(text)
    
    assert "Emma Brooks" in participants
    # Thomas first name match maps to Thomas in custom map if we want, or just static list
    # Wait, the first names bob/alice/carol/dave map to their simple names in our names_map
    assert "Marcus Hale" in participants
    assert "Ethan Cross" not in participants


def test_memory_engine_is_complex_event() -> None:
    assert MemoryEngine.is_complex_event("Marcus walks to the bank") == False
    assert MemoryEngine.is_complex_event("Sophia is baking pastries") == False
    assert MemoryEngine.is_complex_event("Emma Brooks says: 'I know what you did!'") == True
    assert MemoryEngine.is_complex_event("Witnessed Thomas hiding a bag near the market") == True


@pytest.mark.asyncio
async def test_perceive_routine_event_bypass_llm() -> None:
    llm_mock = MagicMock(spec=LLMService)
    # Since it's routine, it shouldn't call LLMService.reason
    llm_mock.reason = AsyncMock()
    
    memory_manager = MemoryManager()
    engine = MemoryEngine(llm_mock, memory_manager)
    
    memory = await engine.perceive_event(
        agent_id="agent_1",
        agent_name="Alice",
        agent_occupation="Healer",
        raw_event_description="Walking to the clinic for daily duties",
        location_name="Clinic",
        timestamp=3600.0
    )
    
    assert memory.summary == "Walking to the clinic for daily duties"
    assert memory.emotion == "neutral"
    assert memory.importance == 0.1
    assert memory.tags == ["routine"]
    assert "Alice" in memory.participants
    
    # Verify LLM was bypassed
    llm_mock.reason.assert_not_called()
    # Verify stored in manager
    assert len(memory_manager.get_memories("agent_1")) == 1


@pytest.mark.asyncio
async def test_perceive_complex_event_llm_called() -> None:
    llm_mock = MagicMock(spec=LLMService)
    llm_mock.reason = AsyncMock(return_value={
        "summary": "Argued with Thomas about missing plans.",
        "emotion": "concerned",
        "importance": 0.8,
        "tags": ["social", "argument"]
    })
    
    memory_manager = MemoryManager()
    engine = MemoryEngine(llm_mock, memory_manager)
    
    memory = await engine.perceive_event(
        agent_id="agent_1",
        agent_name="Alice",
        agent_occupation="Healer",
        raw_event_description="Alice says: 'I know you stole the structural building plans, Thomas!'",
        location_name="Cafe",
        timestamp=7200.0,
        memory_type=MemoryType.PERSONAL
    )
    
    assert memory.summary == "Argued with Thomas about missing plans."
    assert memory.emotion == "concerned"
    assert memory.importance == 0.8
    assert "Alice" in memory.participants
    assert "social" in memory.tags
    
    # Verify LLM was called
    llm_mock.reason.assert_called_once_with(
        "event_compression",
        {
            "agent_name": "Alice",
            "occupation": "Healer",
            "raw_event": "Alice says: 'I know you stole the structural building plans, Thomas!'"
        }
    )
    # Verify stored
    assert len(memory_manager.get_memories("agent_1")) == 1
