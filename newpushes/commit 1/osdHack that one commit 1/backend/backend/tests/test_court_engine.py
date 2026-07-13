"""Tests for CourtEngine."""

import pytest

from app.court.case_file import CaseFile
from app.court.court_engine import _REQUIRED_CORRECT_EVIDENCE, CourtEngine
from app.court.evidence import Evidence
from app.crime.crime_engine import CrimeEngine
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType


@pytest.fixture
def crime_engine() -> CrimeEngine:
    engine = CrimeEngine(MemoryManager())
    engine.create_crime()
    engine.seed_memories()
    return engine


def _make_evidence(evidence_id: str, subject_id: str | None) -> Evidence:
    return Evidence(
        id=evidence_id,
        memory=Memory(
            id=f"mem_{evidence_id}",
            summary="irrelevant",
            type=MemoryType.WITNESS,
            source="self",
            timestamp=0.0,
            confidence=0.9,
            subject_id=subject_id,
        ),
        collected_at=0.0,
    )


def test_verdict_success_with_enough_correct_evidence(crime_engine: CrimeEngine) -> None:
    crime = crime_engine.get_active_crime()
    case_file = CaseFile()
    case_file.add_evidence(_make_evidence("e1", crime.culprit_id))
    case_file.add_evidence(_make_evidence("e2", crime.culprit_id))

    verdict = CourtEngine(crime_engine).evaluate(case_file)

    assert verdict.success is True
    assert verdict.culprit_id == crime.culprit_id
    assert verdict.submitted_evidence_count == 2
    assert verdict.required_evidence_count == _REQUIRED_CORRECT_EVIDENCE


def test_verdict_failure_with_insufficient_correct_evidence(
    crime_engine: CrimeEngine,
) -> None:
    crime = crime_engine.get_active_crime()
    case_file = CaseFile()
    case_file.add_evidence(_make_evidence("e1", crime.culprit_id))
    case_file.add_evidence(_make_evidence("e2", "agent_99"))  # wrong subject

    verdict = CourtEngine(crime_engine).evaluate(case_file)

    assert verdict.success is False
    assert verdict.submitted_evidence_count == 2


def test_verdict_failure_with_empty_case_file(crime_engine: CrimeEngine) -> None:
    verdict = CourtEngine(crime_engine).evaluate(CaseFile())

    assert verdict.success is False
    assert verdict.submitted_evidence_count == 0


def test_evaluate_does_not_mutate_case_file(crime_engine: CrimeEngine) -> None:
    crime = crime_engine.get_active_crime()
    case_file = CaseFile()
    case_file.add_evidence(_make_evidence("e1", crime.culprit_id))

    CourtEngine(crime_engine).evaluate(case_file)

    assert len(case_file.list_evidence()) == 1
