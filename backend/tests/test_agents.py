"""Unit tests for the agents subsystem."""

import pytest

from app.agents.agent import Agent
from app.agents.agent_manager import AgentManager
from app.agents.agent_state import AgentState


def make_agent(agent_id: str = "a1", name: str = "Noah") -> Agent:
    return Agent(agent_id=agent_id, name=name)


def test_agent_defaults() -> None:
    agent = make_agent()
    assert agent.state == AgentState.IDLE
    assert agent.goal is None
    assert agent.location is None


def test_agent_update_is_safe_noop() -> None:
    agent = make_agent()
    agent.update()  # should not raise


def test_register_and_get() -> None:
    manager = AgentManager()
    agent = make_agent()
    manager.register(agent)

    assert manager.get("a1") is agent


def test_get_missing_returns_none() -> None:
    manager = AgentManager()
    assert manager.get("missing") is None


def test_register_duplicate_raises() -> None:
    manager = AgentManager()
    manager.register(make_agent("a1"))

    with pytest.raises(ValueError):
        manager.register(make_agent("a1"))


def test_remove_existing_agent() -> None:
    manager = AgentManager()
    manager.register(make_agent("a1"))
    manager.remove("a1")

    assert manager.get("a1") is None


def test_remove_missing_agent_is_noop() -> None:
    manager = AgentManager()
    manager.remove("missing")  # should not raise


def test_iterate_over_agents() -> None:
    manager = AgentManager()
    manager.register(make_agent("a1"))
    manager.register(make_agent("a2"))

    ids = {agent.agent_id for agent in manager}
    assert ids == {"a1", "a2"}


def test_len_reflects_registered_count() -> None:
    manager = AgentManager()
    assert len(manager) == 0
    manager.register(make_agent("a1"))
    assert len(manager) == 1


def test_update_all_calls_update_on_every_agent() -> None:
    manager = AgentManager()
    call_log = []

    class TrackedAgent(Agent):
        def update(self) -> None:
            call_log.append(self.agent_id)

    manager.register(TrackedAgent(agent_id="a1", name="Noah"))
    manager.register(TrackedAgent(agent_id="a2", name="Emma"))

    manager.update_all()

    assert set(call_log) == {"a1", "a2"}