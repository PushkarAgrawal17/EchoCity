"""Manages the player's collected Evidence."""

from collections.abc import Callable

from app.court.evidence import Evidence
from app.memory.memory import Memory


class EvidenceManager:
    """Owns the collection of Evidence the player has gathered.

    Simplest possible implementation: an in-memory dict keyed by the
    underlying memory's id, so collecting the same memory twice is a
    no-op rather than creating a duplicate.
    """

    def __init__(self, current_time: Callable[[], float] = lambda: 0.0) -> None:
        """Initialize an empty evidence collection.

        Args:
            current_time: Callable returning the current time to stamp
                newly collected Evidence with. Defaults to a constant
                0.0 until the simulation Clock is wired in.
        """
        self._current_time = current_time
        self._evidence_by_memory_id: dict[str, Evidence] = {}


    def collect(self, memory: Memory) -> tuple[Evidence, bool]:
        """Collect a memory as evidence.

        If this memory has already been collected, returns the existing
        Evidence unchanged rather than creating a duplicate.

        Args:
            memory: The Memory to collect as evidence.

        Returns:
            A tuple of (Evidence, created), where created is True only
            if this call produced a new Evidence.
        """
        existing = self._evidence_by_memory_id.get(memory.id)
        if existing is not None:
            return existing, False

        evidence = Evidence(
            id=f"evidence_{memory.id}", memory=memory, collected_at=self._current_time()
        )
        self._evidence_by_memory_id[memory.id] = evidence
        return evidence, True


    def list_evidence(self) -> list[Evidence]:
        """Return all collected evidence.

        Returns:
            A list of every Evidence collected so far.
        """
        return list(self._evidence_by_memory_id.values())

    def remove(self, evidence_id: str) -> None:
        """Remove one piece of evidence by its id.

        Args:
            evidence_id: The id of the Evidence to remove.

        Raises:
            KeyError: If no evidence with this id exists.
        """
        for memory_id, evidence in self._evidence_by_memory_id.items():
            if evidence.id == evidence_id:
                del self._evidence_by_memory_id[memory_id]
                return
        raise KeyError(f"No evidence found with id '{evidence_id}'.")

    def clear(self) -> None:
        """Remove all collected evidence."""
        self._evidence_by_memory_id.clear()