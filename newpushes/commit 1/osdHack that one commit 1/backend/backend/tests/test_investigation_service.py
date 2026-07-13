"""Unit tests for the Investigation Service."""

from app.agents.agent import Agent
from app.agents.agent_manager import AgentManager
from app.agents.agent_state import AgentState
from app.investigation.investigation_service import InvestigationService
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType
from app.simulation.location import Location
from app.simulation.location_type import LocationType

CAFE = Location(id="cafe", name="The Cafe", type=LocationType.CAFE)
COURT = Location(id="court", name="The Court", type=LocationType.COURT)


def make_memory(memory_id: str) -> Memory:
    """Build a simple Memory for use in tests."""
    return Memory(
        id=memory_id,
        summary="Saw something.",
        type=MemoryType.WITNESS,
        source="self",
        timestamp=0.0,
        confidence=0.9,
    )


def build_service() -> tuple[AgentManager, MemoryManager, InvestigationService]:
    """Build a fresh AgentManager, MemoryManager, and wired InvestigationService."""
    agent_manager = AgentManager()
    memory_manager = MemoryManager()
    service = InvestigationService(agent_manager, memory_manager)
    return agent_manager, memory_manager, service


def test_get_agent_returns_matching_agent() -> None:
    """get_agent should return the agent with the matching id."""
    agent_manager, _, service = build_service()
    agent = Agent(agent_id="a1", name="Alice", state=AgentState.IDLE, location=CAFE)
    agent_manager.register(agent)

    assert service.get_agent("a1") is agent


def test_get_agent_returns_none_when_missing() -> None:
    """get_agent should return None for an unregistered id, not raise."""
    _, _, service = build_service()
    assert service.get_agent("nonexistent") is None


def test_list_agents_returns_all_registered_agents() -> None:
    """list_agents should return every registered agent."""
    agent_manager, _, service = build_service()
    a1 = Agent(agent_id="a1", name="Alice", state=AgentState.IDLE)
    a2 = Agent(agent_id="a2", name="Bob", state=AgentState.IDLE)
    agent_manager.register(a1)
    agent_manager.register(a2)

    agents = service.list_agents()

    assert len(agents) == 2
    assert a1 in agents
    assert a2 in agents


def test_get_agent_memories_returns_all_unfiltered() -> None:
    """get_agent_memories should return every memory, with no filtering."""
    _, memory_manager, service = build_service()
    memory_manager.add_memory("a1", make_memory("m1"))
    memory_manager.add_memory("a1", make_memory("m2"))

    memories = service.get_agent_memories("a1")

    assert len(memories) == 2


def test_get_agent_memories_returns_empty_for_unknown_agent() -> None:
    """An agent with no memories should return an empty list, not error."""
    _, _, service = build_service()
    assert service.get_agent_memories("nobody") == []


def test_observe_location_returns_agents_at_that_location() -> None:
    """observe_location should return only agents at the given location."""
    agent_manager, _, service = build_service()
    a1 = Agent(agent_id="a1", name="Alice", state=AgentState.IDLE, location=CAFE)
    a2 = Agent(agent_id="a2", name="Bob", state=AgentState.IDLE, location=COURT)
    agent_manager.register(a1)
    agent_manager.register(a2)

    result = service.observe_location("cafe")

    assert result == [a1]


def test_observe_location_excludes_agents_with_no_location() -> None:
    """Agents with location=None should never appear in observe_location results."""
    agent_manager, _, service = build_service()
    agent_manager.register(Agent(agent_id="a1", name="Alice", state=AgentState.IDLE, location=None))

    assert service.observe_location("cafe") == []


def test_observe_location_returns_empty_for_unknown_location() -> None:
    """A location_id with no agents present should return an empty list."""
    _, _, service = build_service()
    assert service.observe_location("court") == []
