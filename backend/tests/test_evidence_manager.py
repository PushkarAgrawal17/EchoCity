"""Unit tests for the Evidence subsystem."""

import pytest

from app.court.evidence_manager import EvidenceManager
from app.memory.memory import Memory
from app.memory.memory_type import MemoryType


def make_memory(memory_id: str = "m1") -> Memory:
    """Build a simple Memory for use in tests."""
    return Memory(
        id=memory_id,
        summary="Saw the culprit leave the Cafe.",
        type=MemoryType.WITNESS,
        source="self",
        timestamp=5.0,
        confidence=0.9,
    )


def test_collect_returns_evidence_wrapping_the_memory() -> None:
    """collect should return Evidence containing the original memory."""
    manager = EvidenceManager()
    memory = make_memory()

    evidence = manager.collect(memory, collected_at=10.0)

    assert evidence.memory == memory
    assert evidence.collected_at == 10.0


def test_collect_same_memory_twice_does_not_duplicate() -> None:
    """Collecting the same memory twice should not create two entries."""
    manager = EvidenceManager()
    memory = make_memory()

    first = manager.collect(memory, collected_at=10.0)
    second = manager.collect(memory, collected_at=20.0)

    assert first is second
    assert len(manager.list_evidence()) == 1


def test_list_evidence_returns_all_collected() -> None:
    """list_evidence should return every distinct piece of evidence."""
    manager = EvidenceManager()
    manager.collect(make_memory("m1"), collected_at=1.0)
    manager.collect(make_memory("m2"), collected_at=2.0)

    assert len(manager.list_evidence()) == 2


def test_remove_deletes_evidence() -> None:
    """remove should delete evidence by its evidence id."""
    manager = EvidenceManager()
    evidence = manager.collect(make_memory("m1"), collected_at=1.0)

    manager.remove(evidence.id)

    assert manager.list_evidence() == []


def test_remove_unknown_id_raises() -> None:
    """Removing a nonexistent evidence id should raise KeyError."""
    manager = EvidenceManager()
    with pytest.raises(KeyError):
        manager.remove("nonexistent")


def test_clear_removes_all_evidence() -> None:
    """clear should empty the entire evidence collection."""
    manager = EvidenceManager()
    manager.collect(make_memory("m1"), collected_at=1.0)
    manager.collect(make_memory("m2"), collected_at=2.0)

    manager.clear()

    assert manager.list_evidence() == []
