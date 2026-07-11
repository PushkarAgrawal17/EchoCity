"""Unit tests for the Conversation / Gossip subsystem."""

import pytest

from app.conversation.conversation import Conversation
from app.conversation.conversation_engine import ConversationEngine
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType


def make_memory(memory_id: str = "m1") -> Memory:
    """Build a simple witness Memory for use in tests."""
    return Memory(
        id=memory_id,
        summary="Saw the culprit leave the Cafe.",
        type=MemoryType.WITNESS,
        source="self",
        timestamp=5.0,
        confidence=0.8,
    )


def test_share_memory_gives_listener_a_copy() -> None:
    """Listener should receive the memory after share_memory."""
    memory_manager = MemoryManager()
    memory_manager.add_memory("speaker", make_memory())
    engine = ConversationEngine(memory_manager)

    engine.share_memory("speaker", "listener", "m1")

    listener_memories = memory_manager.get_memories("listener")
    assert len(listener_memories) == 1
    assert listener_memories[0].id == "m1"


def test_shared_copy_has_speaker_as_source() -> None:
    """The listener's copy should have source set to the speaker's id."""
    memory_manager = MemoryManager()
    memory_manager.add_memory("speaker", make_memory())
    engine = ConversationEngine(memory_manager)

    engine.share_memory("speaker", "listener", "m1")

    copy = memory_manager.get_memories("listener")[0]
    assert copy.source == "speaker"


def test_shared_copy_preserves_timestamp_and_confidence() -> None:
    """timestamp and confidence must be preserved exactly on the copy."""
    memory_manager = MemoryManager()
    original = make_memory()
    memory_manager.add_memory("speaker", original)
    engine = ConversationEngine(memory_manager)

    engine.share_memory("speaker", "listener", "m1")

    copy = memory_manager.get_memories("listener")[0]
    assert copy.timestamp == original.timestamp
    assert copy.confidence == original.confidence


def test_speaker_memory_marked_shared() -> None:
    """The speaker's original memory should be marked shared=True."""
    memory_manager = MemoryManager()
    memory_manager.add_memory("speaker", make_memory())
    engine = ConversationEngine(memory_manager)

    engine.share_memory("speaker", "listener", "m1")

    speaker_memory = memory_manager.get_memories("speaker")[0]
    assert speaker_memory.shared is True


def test_sharing_same_memory_twice_does_not_duplicate() -> None:
    """Sharing the same memory_id to the same listener twice should not
    create a second copy in the listener's memory list."""
    memory_manager = MemoryManager()
    memory_manager.add_memory("speaker", make_memory())
    engine = ConversationEngine(memory_manager)

    engine.share_memory("speaker", "listener", "m1")
    engine.share_memory("speaker", "listener", "m1")

    assert len(memory_manager.get_memories("listener")) == 1


def test_share_unknown_memory_raises() -> None:
    """Sharing a memory the speaker doesn't have should raise KeyError."""
    memory_manager = MemoryManager()
    engine = ConversationEngine(memory_manager)

    with pytest.raises(KeyError):
        engine.share_memory("speaker", "listener", "nonexistent")


def test_process_conversation_shares_the_memory() -> None:
    """process_conversation should perform the same effect as share_memory."""
    memory_manager = MemoryManager()
    memory_manager.add_memory("speaker", make_memory())
    engine = ConversationEngine(memory_manager)

    conversation = Conversation(
        speaker_id="speaker", listener_id="listener", memory_id="m1", timestamp=5.0
    )
    engine.process_conversation(conversation)

    assert len(memory_manager.get_memories("listener")) == 1
