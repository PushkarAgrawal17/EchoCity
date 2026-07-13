"""Integration test for GameFactory."""

from app.bootstrap.game_factory import GameFactory


def test_bootstrap_builds_complete_game() -> None:
    game = GameFactory.build()

    assert game.world is not None
    assert game.location_manager is not None
    assert game.shell is not None


def test_bootstrap_registers_locations() -> None:
    game = GameFactory.build()

    ids = {location.id for location in game.location_manager.list_locations()}
    assert ids == {"cafe", "court"}


def test_bootstrap_creates_expected_demo_agents() -> None:
    game = GameFactory.build()

    expected_ids = {
        "agent_1",
        "agent_2",
        "agent_3",
        "agent_4",
        "agent_5",
        "agent_6",
        "agent_7",
        "agent_8",
    }
    actual_ids = {agent.agent_id for agent in game.world.agent_manager}

    assert actual_ids == expected_ids
    assert game.world.agent_manager.get("agent_2").name == "Bob"


def test_bootstrap_seeds_crime() -> None:
    game = GameFactory.build()

    witness_memories = game.world.memory_manager.get_memories("agent_3")
    heard_memories = game.world.memory_manager.get_memories("agent_4")

    assert len(witness_memories) == 1
    assert any(memory.subject_id == "agent_2" for memory in heard_memories)
    assert witness_memories[0].subject_id == "agent_2"
    assert heard_memories[0].subject_id == "agent_2"


def test_bootstrap_propagates_gossip_before_returning() -> None:
    game = GameFactory.build()

    # Witness memories should still exist after gossip runs.
    assert len(game.world.memory_manager.get_memories("agent_3")) >= 1
    assert len(game.world.memory_manager.get_memories("agent_4")) >= 1

    # At least one agent outside the original witness/heard pair should
    # now know something, proving gossip actually propagated.
    other_agents = [a for a in game.world.agent_manager if a.agent_id not in {"agent_3", "agent_4"}]
    assert any(game.world.memory_manager.get_memories(agent.agent_id) for agent in other_agents)
