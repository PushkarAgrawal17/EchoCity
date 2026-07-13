"""Unit tests for the CaseFile subsystem."""

import pytest

from app.court.case_file import CaseFile
from app.court.evidence import Evidence
from app.memory.memory import Memory
from app.memory.memory_type import MemoryType


def make_evidence(evidence_id: str, memory_id: str) -> Evidence:
    """Build a simple Evidence for use in tests."""
    memory = Memory(
        id=memory_id,
        summary="Saw something.",
        type=MemoryType.WITNESS,
        source="self",
        timestamp=1.0,
        confidence=0.9,
    )
    return Evidence(id=evidence_id, memory=memory, collected_at=1.0)


def test_add_evidence_appears_in_list() -> None:
    """Added evidence should be retrievable via list_evidence."""
    case_file = CaseFile()
    evidence = make_evidence("e1", "m1")

    case_file.add_evidence(evidence)

    assert case_file.list_evidence() == [evidence]


def test_add_duplicate_evidence_does_not_duplicate() -> None:
    """Adding the same evidence id twice should not create two entries."""
    case_file = CaseFile()
    evidence = make_evidence("e1", "m1")

    case_file.add_evidence(evidence)
    case_file.add_evidence(evidence)

    assert len(case_file.list_evidence()) == 1


def test_list_evidence_preserves_insertion_order() -> None:
    """Evidence should be listed in the order it was added."""
    case_file = CaseFile()
    e1 = make_evidence("e1", "m1")
    e2 = make_evidence("e2", "m2")
    e3 = make_evidence("e3", "m3")

    case_file.add_evidence(e2)
    case_file.add_evidence(e1)
    case_file.add_evidence(e3)

    assert case_file.list_evidence() == [e2, e1, e3]


def test_remove_evidence_deletes_it() -> None:
    """remove_evidence should remove the matching entry."""
    case_file = CaseFile()
    evidence = make_evidence("e1", "m1")
    case_file.add_evidence(evidence)

    case_file.remove_evidence("e1")

    assert case_file.list_evidence() == []


def test_remove_unknown_evidence_raises() -> None:
    """Removing an id not in the case file should raise KeyError."""
    case_file = CaseFile()
    with pytest.raises(KeyError):
        case_file.remove_evidence("nonexistent")


def test_clear_removes_all_evidence() -> None:
    """clear should empty the case file."""
    case_file = CaseFile()
    case_file.add_evidence(make_evidence("e1", "m1"))
    case_file.add_evidence(make_evidence("e2", "m2"))

    case_file.clear()

    assert case_file.list_evidence() == []
