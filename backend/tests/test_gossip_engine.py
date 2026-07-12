"""Unit tests for the Automatic Gossip Engine."""

from app.agents.agent import Agent
from app.agents.agent_manager import AgentManager
from app.agents.agent_state import AgentState
from app.conversation.conversation_engine import ConversationEngine
from app.conversation.gossip_engine import GossipEngine
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType
from app.simulation.location import Location
from app.simulation.location_type import LocationType

CAFE = Location(id="cafe", name="The Cafe", type=LocationType.CAFE)
COURT = Location(id="court", name="The Court", type=LocationType.COURT)


def make_agent(agent_id: str, location: Location | None) -> Agent:
    """Build a simple Agent for use in tests."""
    return Agent(agent_id=agent_id, name=agent_id, state=AgentState.IDLE, location=location)


def make_memory(memory_id: str) -> Memory:
    """Build a simple witness Memory for use in tests."""
    return Memory(
        id=memory_id,
        summary="Saw something.",
        type=MemoryType.WITNESS,
        source="self",
        timestamp=0.0,
        confidence=0.9,
    )


def build_engine() -> tuple[AgentManager, MemoryManager, GossipEngine]:
    """Build a fresh AgentManager, MemoryManager, and wired GossipEngine."""
    agent_manager = AgentManager()
    memory_manager = MemoryManager()
    conversation_engine = ConversationEngine(memory_manager)
    gossip_engine = GossipEngine(agent_manager, memory_manager, conversation_engine)
    return agent_manager, memory_manager, gossip_engine


def test_agents_at_same_location_gossip() -> None:
    """Two co-located agents should share a memory during process_tick."""
    agent_manager, memory_manager, gossip_engine = build_engine()
    agent_manager.register(make_agent("agent_a", CAFE))
    agent_manager.register(make_agent("agent_b", CAFE))
    memory_manager.add_memory("agent_a", make_memory("m1"))

    gossip_engine.process_tick(timestamp=1.0)

    assert len(memory_manager.get_memories("agent_b")) == 1
    assert memory_manager.get_memories("agent_b")[0].id == "m1"


def test_agents_at_different_locations_do_not_gossip() -> None:
    """Agents in different Locations must never gossip with each other."""
    agent_manager, memory_manager, gossip_engine = build_engine()
    agent_manager.register(make_agent("agent_a", CAFE))
    agent_manager.register(make_agent("agent_b", COURT))
    memory_manager.add_memory("agent_a", make_memory("m1"))

    gossip_engine.process_tick(timestamp=1.0)

    assert memory_manager.get_memories("agent_b") == []


def test_agent_with_no_location_is_excluded() -> None:
    """An agent with location=None should never participate in gossip."""
    agent_manager, memory_manager, gossip_engine = build_engine()
    agent_manager.register(make_agent("agent_a", None))
    agent_manager.register(make_agent("agent_b", CAFE))
    memory_manager.add_memory("agent_a", make_memory("m1"))

    gossip_engine.process_tick(timestamp=1.0)

    assert memory_manager.get_memories("agent_b") == []


def test_speaker_with_no_memories_shares_nothing() -> None:
    """A speaker with an empty memory list should cause no error and no share."""
    agent_manager, memory_manager, gossip_engine = build_engine()
    agent_manager.register(make_agent("agent_a", CAFE))
    agent_manager.register(make_agent("agent_b", CAFE))

    gossip_engine.process_tick(timestamp=1.0)

    assert memory_manager.get_memories("agent_b") == []


def test_odd_agent_out_is_unpaired() -> None:
    """With 3 agents at one location, one is left without a partner this tick."""
    agent_manager, memory_manager, gossip_engine = build_engine()
    agent_manager.register(make_agent("agent_a", CAFE))
    agent_manager.register(make_agent("agent_b", CAFE))
    agent_manager.register(make_agent("agent_c", CAFE))
    memory_manager.add_memory("agent_a", make_memory("m1"))
    memory_manager.add_memory("agent_c", make_memory("m2"))

    gossip_engine.process_tick(timestamp=1.0)

    # agent_a (speaker) pairs with agent_b (listener); agent_c is unpaired.
    assert memory_manager.get_memories("agent_b")[0].id == "m1"
    assert memory_manager.get_memories("agent_c") == [make_memory("m2")]


def test_pairing_is_deterministic_across_runs() -> None:
    """Running process_tick twice on identically-seeded state should
    produce identical results (no duplication, same pairing)."""
    agent_manager, memory_manager, gossip_engine = build_engine()
    agent_manager.register(make_agent("agent_a", CAFE))
    agent_manager.register(make_agent("agent_b", CAFE))
    memory_manager.add_memory("agent_a", make_memory("m1"))

    gossip_engine.process_tick(timestamp=1.0)
    gossip_engine.process_tick(timestamp=2.0)

    assert len(memory_manager.get_memories("agent_b")) == 1


def test_speaker_rotates_through_memories_across_calls() -> None:
    """A speaker with multiple memories shares a different one each call,
    in order, and wraps back to the start once exhausted."""
    _, memory_manager, gossip_engine = build_engine()

    memory_manager.add_memory("agent_a", make_memory("m1"))
    memory_manager.add_memory("agent_a", make_memory("m2"))
    memory_manager.add_memory("agent_a", make_memory("m3"))

    # Test _attempt_share directly because process_tick() combines
    # pairing, rotation and memory selection. A fresh listener is used
    # each call so ConversationEngine's deduplication doesn't affect
    # the memory-rotation behavior being tested.
    expected_order = ["m1", "m2", "m3", "m1"]

    for i, expected_id in enumerate(expected_order):
        listener_id = f"listener_{i}"
        gossip_engine._attempt_share("agent_a", listener_id, timestamp=float(i))
        assert memory_manager.get_memories(listener_id)[-1].id == expected_id
