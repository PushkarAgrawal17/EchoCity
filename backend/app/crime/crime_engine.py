"""Creates the one hardcoded crime and seeds witness memories."""

from app.crime.crime import Crime
from app.crime.crime_status import CrimeStatus
from app.memory.memory import Memory
from app.memory.memory_manager import MemoryManager
from app.memory.memory_type import MemoryType

_CRIME_ID = "crime_1"
_CULPRIT_ID = "agent_2"
_VICTIM_ID = "agent_1"
_LOCATION_ID = "cafe"
_CRIME_TIMESTAMP = 0.0

_WITNESS_AGENT_ID = "agent_3"
_HEARD_AGENT_ID = "agent_4"


class CrimeEngine:
    """Owns the single ground-truth crime for the MVP investigation.

    Never modifies Agents directly. All knowledge distribution to agents
    happens exclusively through MemoryManager.
    """

    def __init__(self, memory_manager: MemoryManager) -> None:
        """Create a CrimeEngine bound to a MemoryManager.

        Args:
            memory_manager: The MemoryManager used to seed witness memories.
        """
        self._memory_manager = memory_manager
        self._crime: Crime | None = None

    def create_crime(self) -> Crime:
        """Create and store the one hardcoded crime.

        Idempotent: calling this again returns the same Crime instance
        rather than creating a second one.

        Returns:
            The created (or already-existing) Crime.
        """
        if self._crime is None:
            self._crime = Crime(
                id=_CRIME_ID,
                title="Theft of the Silver Necklace",
                description=(
                    f"{_CULPRIT_ID} stole a necklace from {_VICTIM_ID} at the Cafe."
                ),
                culprit_id=_CULPRIT_ID,
                victim_id=_VICTIM_ID,
                location_id=_LOCATION_ID,
                timestamp=_CRIME_TIMESTAMP,
                status=CrimeStatus.UNSOLVED,
            )
        return self._crime

    def get_active_crime(self) -> Crime:
        """Return the currently active crime.

        Returns:
            The active Crime.

        Raises:
            RuntimeError: If create_crime() has not been called yet.
        """
        if self._crime is None:
            raise RuntimeError("No active crime. Call create_crime() first.")
        return self._crime

    def seed_memories(self) -> None:
        """Give deterministic, hardcoded memories to specific agents.

        One agent directly witnesses the crime; another only hears about
        it secondhand. Requires create_crime() to have been called first.

        Raises:
            RuntimeError: If create_crime() has not been called yet.
        """
        crime = self.get_active_crime()

        self._memory_manager.add_memory(
            _WITNESS_AGENT_ID,
            Memory(
                id="mem_witness_1",
                summary=f"Saw {crime.culprit_id} take something from {crime.victim_id}.",
                type=MemoryType.WITNESS,
                source="self",
                timestamp=crime.timestamp,
                confidence=0.9,
            ),
        )

        self._memory_manager.add_memory(
            _HEARD_AGENT_ID,
            Memory(
                id="mem_heard_1",
                summary=f"Heard that {crime.culprit_id} might have stolen something.",
                type=MemoryType.HEARD,
                source=_WITNESS_AGENT_ID,
                timestamp=crime.timestamp,
                confidence=0.5,
            ),
        )
