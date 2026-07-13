"""Defines the CaseFile: the player's selected set of Evidence."""

from app.court.evidence import Evidence


class CaseFile:
    """Holds the player's chosen Evidence for presentation.

    Owns no investigation logic — just an ordered, deduplicated
    collection of Evidence the player has selected.
    """

    def __init__(self) -> None:
        """Initialize an empty case file."""
        self._evidence: dict[str, Evidence] = {}

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the case file.

        Adding evidence already present (same ``evidence.id``) is a no-op.

        Args:
            evidence: The Evidence to add.
        """
        if evidence.id not in self._evidence:
            self._evidence[evidence.id] = evidence

    def remove_evidence(self, evidence_id: str) -> None:
        """Remove evidence from the case file by id.

        Args:
            evidence_id: The id of the Evidence to remove.

        Raises:
            KeyError: If no evidence with this id is in the case file.
        """
        if evidence_id not in self._evidence:
            raise KeyError(f"No evidence found with id '{evidence_id}'.")
        del self._evidence[evidence_id]

    def list_evidence(self) -> list[Evidence]:
        """Return all evidence in the case file, in insertion order.

        Returns:
            A list of Evidence in the order they were added.
        """
        return list(self._evidence.values())

    def clear(self) -> None:
        """Remove all evidence from the case file."""
        self._evidence.clear()
