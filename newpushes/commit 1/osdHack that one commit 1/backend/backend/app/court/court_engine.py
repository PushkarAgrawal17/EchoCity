"""Evaluates a submitted CaseFile against the active Crime."""

from app.court.case_file import CaseFile
from app.court.verdict import Verdict
from app.crime.crime_engine import CrimeEngine

_REQUIRED_CORRECT_EVIDENCE = 2


class CourtEngine:
    """Produces a deterministic Verdict from a CaseFile.

    Never mutates the Crime, CaseFile, or any Evidence it evaluates.
    """

    def __init__(self, crime_engine: CrimeEngine) -> None:
        """Create a CourtEngine bound to a CrimeEngine.

        Args:
            crime_engine: Source of the active ground-truth Crime.
        """
        self._crime_engine = crime_engine

    def evaluate(self, case_file: CaseFile) -> Verdict:
        """Evaluate a CaseFile against the active Crime.

        Args:
            case_file: The player's submitted evidence.

        Returns:
            A Verdict describing whether the case succeeded.
        """
        crime = self._crime_engine.get_active_crime()
        evidence_list = case_file.list_evidence()

        correct_count = sum(
            1 for evidence in evidence_list if evidence.memory.subject_id == crime.culprit_id
        )

        success = correct_count >= _REQUIRED_CORRECT_EVIDENCE
        message = (
            "The evidence conclusively points to the culprit."
            if success
            else "The evidence is insufficient to convict."
        )

        return Verdict(
            success=success,
            culprit_id=crime.culprit_id,
            submitted_evidence_count=len(evidence_list),
            required_evidence_count=_REQUIRED_CORRECT_EVIDENCE,
            message=message,
        )
