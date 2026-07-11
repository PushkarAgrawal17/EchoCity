"""Handles deterministic memory sharing between agents via conversation."""

from dataclasses import replace

from app.memory.memory_manager import MemoryManager
from app.services.conversation import Conversation


class ConversationEngine:
    """Coordinates memory sharing between agents.

    Never modifies Agents directly. All state changes go through
    MemoryManager. Purely deterministic — no dialogue, no AI.
    """

    def __init__(self, memory_manager: MemoryManager) -> None:
        """Create a ConversationEngine bound to a MemoryManager.

        Args:
            memory_manager: The MemoryManager used to read and write memories.
        """
        self._memory_manager = memory_manager

    def share_memory(self, speaker_id: str, listener_id: str, memory_id: str) -> None:
        """Share one memory from speaker to listener.

        The listener receives a copy with ``source`` set to the speaker's
        agent_id; ``timestamp`` and ``confidence`` are preserved. If the
        listener already holds a memory with this id, nothing happens
        (no duplication). The speaker's original memory is marked shared.

        Args:
            speaker_id: agent_id of whoever is sharing the memory.
            listener_id: agent_id of whoever is receiving the memory.
            memory_id: id of the Memory to share.

        Raises:
            KeyError: If the speaker does not hold a memory with this id.
        """
        speaker_memories = self._memory_manager.get_memories(speaker_id)
        original = next((m for m in speaker_memories if m.id == memory_id), None)
        if original is None:
            raise KeyError(f"Speaker '{speaker_id}' has no memory '{memory_id}'.")

        listener_memories = self._memory_manager.get_memories(listener_id)
        already_has_it = any(m.id == memory_id for m in listener_memories)
        if already_has_it:
            return

        copy = replace(original, source=speaker_id)
        self._memory_manager.add_memory(listener_id, copy)
        self._memory_manager.share_memory(speaker_id, memory_id)

    def process_conversation(self, conversation: Conversation) -> None:
        """Execute a single Conversation as a memory-share.

        Args:
            conversation: The Conversation describing who shares what
                with whom, and when.
        """
        self.share_memory(
            speaker_id=conversation.speaker_id,
            listener_id=conversation.listener_id,
            memory_id=conversation.memory_id,
        )
