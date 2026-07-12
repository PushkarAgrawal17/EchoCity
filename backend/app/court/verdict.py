"""Defines the Verdict value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Verdict:
    """The deterministic outcome of a Court evaluation.

    Attributes:
        success: Whether the case file was sufficient to convict.
        culprit_id: agent_id of the true culprit (ground truth).
        submitted_evidence_count: Total evidence pieces submitted.
        required_evidence_count: Minimum correct evidence needed to win.
        message: Human-readable explanation of the outcome.
    """

    success: bool
    culprit_id: str
    submitted_evidence_count: int
    required_evidence_count: int
    message: str
