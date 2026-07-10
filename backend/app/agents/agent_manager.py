"""AgentManager: registers, removes, retrieves, and updates Agents.

A lightweight registry only. No simulation logic, scheduling, AI, or
EventBus knowledge — those belong to other subsystems.
"""

import logging
from collections.abc import Iterator

from app.agents.agent import Agent

logger = logging.getLogger(__name__)


class AgentManager:
    """Owns the collection of all Agents in the simulation.

    Attributes:
        None (internal storage is private; access agents via the methods
        below).
    """

    def __init__(self) -> None:
        """Create an empty AgentManager."""
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        """Add an agent to the manager.

        Args:
            agent: The agent to register.

        Raises:
            ValueError: If an agent with the same ``agent_id`` is already
                registered. A duplicate ID is a data-integrity bug worth
                surfacing immediately, unlike removing something already
                gone (see ``remove``).
        """
        if agent.agent_id in self._agents:
            raise ValueError(f"Agent with id '{agent.agent_id}' is already registered.")

        self._agents[agent.agent_id] = agent

    def remove(self, agent_id: str) -> None:
        """Remove an agent from the manager, if present.

        Args:
            agent_id: ID of the agent to remove.

        Removing an ID that is not registered is not an error — it just
        logs a warning and does nothing, since the caller's desired end
        state (agent absent) is already true.
        """
        if agent_id not in self._agents:
            logger.warning("AgentManager.remove() called with unknown agent_id '%s'.", agent_id)
            return

        del self._agents[agent_id]

    def get(self, agent_id: str) -> Agent | None:
        """Retrieve an agent by ID.

        Args:
            agent_id: ID of the agent to retrieve.

        Returns:
            The matching Agent, or ``None`` if no such agent is registered.
        """
        return self._agents.get(agent_id)

    def __iter__(self) -> Iterator[Agent]:
        """Iterate over all registered agents."""
        return iter(self._agents.values())

    def __len__(self) -> int:
        """Return the number of registered agents."""
        return len(self._agents)

    def update_all(self) -> None:
        """Update every registered agent for the current tick."""
        for agent in self._agents.values():
            agent.update()