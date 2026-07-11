"""Manages storage and retrieval of Memories per agent."""

from dataclasses import replace

from app.memory.memory import Memory


class MemoryManager:
    """Owns all Memories, grouped by the agent that holds them.

    Simplest possible implementation: an in-memory dict of
    agent_id -> list[Memory]. No persistence, no ranking, no AI.
    """

    def __init__(self) -> None:
        """Initialize an empty memory store."""
        self._memories: dict[str, list[Memory]] = {}

    def add_memory(self, agent_id: str, memory: Memory) -> None:
        """Add a memory to the given agent's memory list.

        Args:
            agent_id: The agent who holds this memory.
            memory: The Memory to add.
        """
        self._memories.setdefault(agent_id, []).append(memory)

    def get_memories(self, agent_id: str) -> list[Memory]:
        """Return all memories held by the given agent.

        Args:
            agent_id: The agent whose memories to retrieve.

        Returns:
            A list of Memory objects. Empty list if the agent has none.
        """
        return list(self._memories.get(agent_id, []))

    def share_memory(self, agent_id: str, memory_id: str) -> None:
        """Mark a memory as shared.

        Since Memory is immutable, the original is replaced in-place
        within the agent's list with a copy that has ``shared=True``.

        Args:
            agent_id: The agent who holds the memory.
            memory_id: The id of the memory to mark as shared.

        Raises:
            KeyError: If the agent or memory is not found.
        """
        memories = self._memories.get(agent_id)
        if memories is None:
            raise KeyError(f"No memories found for agent '{agent_id}'.")

        for index, memory in enumerate(memories):
            if memory.id == memory_id:
                memories[index] = replace(memory, shared=True)
                return

        raise KeyError(f"Memory '{memory_id}' not found for agent '{agent_id}'.")

    def remove_memory(self, agent_id: str, memory_id: str) -> None:
        """Remove a memory from an agent's memory list.

        Args:
            agent_id: The agent who holds the memory.
            memory_id: The id of the memory to remove.

        Raises:
            KeyError: If the agent or memory is not found.
        """
        memories = self._memories.get(agent_id)
        if memories is None:
            raise KeyError(f"No memories found for agent '{agent_id}'.")

        for index, memory in enumerate(memories):
            if memory.id == memory_id:
                del memories[index]
                return

        raise KeyError(f"Memory '{memory_id}' not found for agent '{agent_id}'.")
