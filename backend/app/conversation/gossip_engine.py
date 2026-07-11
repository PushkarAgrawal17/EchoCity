"""GossipEngine: decides WHEN agents gossip; delegates HOW to ConversationEngine."""

from app.agents.agent_manager import AgentManager
from app.memory.memory_manager import MemoryManager
from app.services.conversation import Conversation
from app.services.conversation_engine import ConversationEngine


class GossipEngine:
    """Automatically triggers deterministic conversations between agents
    who currently share a Location.

    Never transfers memories itself — all actual sharing is delegated to
    ConversationEngine. This class only decides which pairs of agents
    talk on a given tick.
    """

    def __init__(
        self,
        agent_manager: AgentManager,
        memory_manager: MemoryManager,
        conversation_engine: ConversationEngine,
    ) -> None:
        """Create a GossipEngine.

        Args:
            agent_manager: Source of truth for which agents exist and
                where they currently are.
            memory_manager: Used only to read a speaker's memories to
                pick which one to offer; never written to directly.
            conversation_engine: Performs the actual memory transfer.
        """
        self._agent_manager = agent_manager
        self._memory_manager = memory_manager
        self._conversation_engine = conversation_engine

    def process_tick(self, timestamp: float) -> None:
        """Run one gossip tick: pair up co-located agents and let each
        speaker share at most one memory.

        Args:
            timestamp: Current simulation time, stamped on any
                Conversation created this tick.
        """
        groups = self._group_agents_by_location()

        for location_id in sorted(groups):
            agent_ids = sorted(groups[location_id])
            for speaker_id, listener_id in self._pair_up(agent_ids):
                self._attempt_share(speaker_id, listener_id, timestamp)

    def _group_agents_by_location(self) -> dict[str, list[str]]:
        """Group agent_ids by the id of their current Location.

        Agents with no location (``agent.location is None``) are excluded.
        """
        groups: dict[str, list[str]] = {}
        for agent in self._agent_manager:
            if agent.location is None:
                continue
            groups.setdefault(agent.location.id, []).append(agent.agent_id)
        return groups

    @staticmethod
    def _pair_up(agent_ids: list[str]) -> list[tuple[str, str]]:
        """Pair up a sorted list of agent_ids two at a time, deterministically.

        An odd agent out (no partner) is left unpaired this tick.
        """
        return [(agent_ids[i], agent_ids[i + 1]) for i in range(0, len(agent_ids) - 1, 2)]

    def _attempt_share(self, speaker_id: str, listener_id: str, timestamp: float) -> None:
        """Have speaker share its first memory with listener, if it has one."""
        speaker_memories = self._memory_manager.get_memories(speaker_id)
        if not speaker_memories:
            return

        memory_id = speaker_memories[0].id
        conversation = Conversation(
            speaker_id=speaker_id,
            listener_id=listener_id,
            memory_id=memory_id,
            timestamp=timestamp,
        )
        self._conversation_engine.process_conversation(conversation)
