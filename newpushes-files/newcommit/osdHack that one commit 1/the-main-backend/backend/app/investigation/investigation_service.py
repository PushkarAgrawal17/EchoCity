"""InvestigationService: read-only query layer for the player-facing shell/frontend."""

from app.agents.agent import Agent
from app.agents.agent_manager import AgentManager
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager


class InvestigationService:
    """Provides read-only queries over Agents and Memories.

    Never modifies simulation state. Depends only on AgentManager and
    MemoryManager — no ConversationEngine, GossipEngine, or CrimeEngine.
    """

    def __init__(self, agent_manager: AgentManager, memory_manager: MemoryManager) -> None:
        """Create an InvestigationService.

        Args:
            agent_manager: Source of agent data.
            memory_manager: Source of memory data.
        """
        self._agent_manager = agent_manager
        self._memory_manager = memory_manager

    def get_agent(self, agent_id: str) -> Agent | None:
        """Return one agent's information, no memories included.

        Args:
            agent_id: ID of the agent to look up.

        Returns:
            The matching Agent, or None if no such agent is registered.
        """
        return self._agent_manager.get(agent_id)

    def list_agents(self) -> list[Agent]:
        """Return every registered agent.

        Returns:
            A list of all Agents currently known to the simulation.
        """
        return list(self._agent_manager)

    def get_agent_memories(self, agent_id: str) -> list[Memory]:
        """Return every memory currently owned by an agent, unfiltered.

        Args:
            agent_id: ID of the agent whose memories to retrieve.

        Returns:
            A list of Memory objects. Empty list if the agent has none.
        """
        return self._memory_manager.get_memories(agent_id)

    def observe_location(self, location_id: str) -> list[Agent]:
        """Return every agent currently present at the given location.

        Args:
            location_id: ID of the Location to check.

        Returns:
            A list of Agents whose current location matches location_id.
            Agents with no location are excluded.
        """
        return [
            agent
            for agent in self._agent_manager
            if agent.location is not None and agent.location.id == location_id
        ]
