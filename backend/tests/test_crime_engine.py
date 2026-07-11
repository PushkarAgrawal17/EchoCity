"""Unit tests for the Crime Engine subsystem."""

import pytest

from app.crime.crime_engine import CrimeEngine
from app.crime.crime_status import CrimeStatus
from app.memory.memory_manager import MemoryManager


def test_create_crime_returns_unsolved_crime() -> None:
    """create_crime should produce a Crime with UNSOLVED status."""
    engine = CrimeEngine(MemoryManager())
    crime = engine.create_crime()

    assert crime.status == CrimeStatus.UNSOLVED
    assert crime.culprit_id != crime.victim_id


def test_create_crime_is_idempotent() -> None:
    """Calling create_crime twice should return the same Crime instance."""
    engine = CrimeEngine(MemoryManager())
    first = engine.create_crime()
    second = engine.create_crime()

    assert first is second


def test_get_active_crime_before_creation_raises() -> None:
    """get_active_crime should fail loudly if no crime exists yet."""
    engine = CrimeEngine(MemoryManager())
    with pytest.raises(RuntimeError):
        engine.get_active_crime()


def test_get_active_crime_returns_created_crime() -> None:
    """get_active_crime should return the crime created by create_crime."""
    engine = CrimeEngine(MemoryManager())
    created = engine.create_crime()

    assert engine.get_active_crime() is created


def test_seed_memories_before_creation_raises() -> None:
    """seed_memories should fail loudly if create_crime wasn't called."""
    engine = CrimeEngine(MemoryManager())
    with pytest.raises(RuntimeError):
        engine.seed_memories()


def test_seed_memories_creates_witness_and_heard_memories() -> None:
    """seed_memories should give a witness a direct memory and a
    second agent a secondhand ('heard') memory of the same crime."""
    memory_manager = MemoryManager()
    engine = CrimeEngine(memory_manager)
    engine.create_crime()

    engine.seed_memories()

    witness_memories = memory_manager.get_memories("agent_3")
    heard_memories = memory_manager.get_memories("agent_4")

    assert len(witness_memories) == 1
    assert witness_memories[0].type.value == "witness"

    assert len(heard_memories) == 1
    assert heard_memories[0].type.value == "heard"


def test_seed_memories_does_not_touch_unrelated_agents() -> None:
    """Agents not part of the hardcoded seed should have no memories."""
    memory_manager = MemoryManager()
    engine = CrimeEngine(memory_manager)
    engine.create_crime()

    engine.seed_memories()

    assert memory_manager.get_memories("agent_1") == []
    assert memory_manager.get_memories("agent_2") == []
