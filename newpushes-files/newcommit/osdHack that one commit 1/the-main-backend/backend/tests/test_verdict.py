"""Tests for the Verdict value object."""

import pytest

from app.court.verdict import Verdict


def test_verdict_is_immutable() -> None:
    verdict = Verdict(
        success=True,
        culprit_id="agent_2",
        submitted_evidence_count=2,
        required_evidence_count=2,
        message="ok",
    )
    with pytest.raises(AttributeError):
        verdict.success = False  # type: ignore[misc]


def test_verdict_fields() -> None:
    verdict = Verdict(
        success=False,
        culprit_id="agent_2",
        submitted_evidence_count=1,
        required_evidence_count=2,
        message="Not enough evidence.",
    )
    assert verdict.success is False
    assert verdict.culprit_id == "agent_2"
    assert verdict.submitted_evidence_count == 1
    assert verdict.required_evidence_count == 2
