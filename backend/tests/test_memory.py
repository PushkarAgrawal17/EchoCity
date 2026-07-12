"""Unit tests for the Memory subsystem."""

import pytest

from app.agents.agent import Agent
from app.agents.agent_manager import AgentManager
from app.higher_self.higher_self_engine import HigherSelfEngine
from app.higher_self.influence import Influence
from app.higher_self.influence_type import InfluenceType
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType


def make_memory(memory_id: str = "m1") -> Memory:
    """Build a simple Memory for use in tests."""
    return Memory(
        id=memory_id,
        summary="Saw Emma leave the Cafe.",
        type=MemoryType.WITNESS,
        source="self",
        timestamp=10.0,
        confidence=0.9,
    )


def test_memory_is_immutable() -> None:
    """Memory should be frozen once created."""
    memory = make_memory()
    with pytest.raises(AttributeError):
        memory.summary = "changed"  # type: ignore[misc]


def test_add_and_get_memories() -> None:
    """Adding a memory should make it retrievable for that agent."""
    manager = MemoryManager()
    memory = make_memory()

    manager.add_memory("agent_1", memory)

    assert manager.get_memories("agent_1") == [memory]


def test_get_memories_for_unknown_agent_returns_empty() -> None:
    """An agent with no memories should return an empty list, not error."""
    manager = MemoryManager()
    assert manager.get_memories("nobody") == []


def test_share_memory_marks_shared() -> None:
    """share_memory should produce a new Memory with shared=True."""
    manager = MemoryManager()
    memory = make_memory()
    manager.add_memory("agent_1", memory)

    manager.share_memory("agent_1", "m1")

    shared_memory = manager.get_memories("agent_1")[0]
    assert shared_memory.shared is True
    assert shared_memory.id == memory.id


def test_share_unknown_memory_raises() -> None:
    """Sharing a memory that doesn't exist should raise KeyError."""
    manager = MemoryManager()
    manager.add_memory("agent_1", make_memory())

    with pytest.raises(KeyError):
        manager.share_memory("agent_1", "nonexistent")


def test_share_for_unknown_agent_raises() -> None:
    """Sharing for an agent with no memories should raise KeyError."""
    manager = MemoryManager()
    with pytest.raises(KeyError):
        manager.share_memory("nobody", "m1")


def test_remove_memory() -> None:
    """remove_memory should delete the memory from the agent's list."""
    manager = MemoryManager()
    manager.add_memory("agent_1", make_memory())

    manager.remove_memory("agent_1", "m1")

    assert manager.get_memories("agent_1") == []


def test_remove_unknown_memory_raises() -> None:
    """Removing a memory that doesn't exist should raise KeyError."""
    manager = MemoryManager()
    manager.add_memory("agent_1", make_memory())

    with pytest.raises(KeyError):
        manager.remove_memory("agent_1", "nonexistent")


def test_get_memory_returns_matching_memory() -> None:
    """get_memory should return the memory with the matching id."""
    manager = MemoryManager()
    memory = make_memory()
    manager.add_memory("agent_1", memory)

    assert manager.get_memory("agent_1", "m1") == memory


def test_get_memory_returns_none_when_not_found() -> None:
    """get_memory should return None if the memory id doesn't exist."""
    manager = MemoryManager()
    manager.add_memory("agent_1", make_memory())

    assert manager.get_memory("agent_1", "nonexistent") is None


def test_get_memory_returns_none_for_unknown_agent() -> None:
    """get_memory should return None if the agent has no memories."""
    manager = MemoryManager()

    assert manager.get_memory("nobody", "m1") is None


def test_next_memory_id_increments_and_is_unique() -> None:
    """next_memory_id should return a new, unique id each call."""
    manager = MemoryManager()

    first = manager.next_memory_id()
    second = manager.next_memory_id()

    assert first != second


def test_suggest_adds_one_memory() -> None:
    """SUGGEST should add exactly one memory to the target agent."""
    memory_manager = MemoryManager()
    agent_manager = AgentManager()
    agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
    engine = HigherSelfEngine(memory_manager, agent_manager)

    result = engine.apply(Influence(type=InfluenceType.SUGGEST, primary_target="agent_1"))

    assert result.success is True
    assert result.affected_agents == ["agent_1"]
    assert len(memory_manager.get_memories("agent_1")) == 1


def test_suggest_memory_has_no_subject_id() -> None:
    """SUGGEST must never point at a specific agent as subject."""
    memory_manager = MemoryManager()
    agent_manager = AgentManager()
    agent_manager.register(Agent(agent_id="agent_1", name="Agent One"))
    engine = HigherSelfEngine(memory_manager, agent_manager)

    engine.apply(Influence(type=InfluenceType.SUGGEST, primary_target="agent_1"))

    memory = memory_manager.get_memories("agent_1")[0]
    assert memory.subject_id is None