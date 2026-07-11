"""Defines the Crime value object."""

from dataclasses import dataclass

from app.crime.crime_status import CrimeStatus


@dataclass(frozen=True)
class Crime:
    """The single ground-truth crime for this investigation.

    Attributes:
        id: Unique identifier for this crime.
        title: Short display name.
        description: What actually happened (ground truth, not known
            in full by any single agent).
        culprit_id: agent_id of whoever committed the crime.
        victim_id: agent_id of whoever the crime was committed against.
        location_id: id of the Location where it happened.
        timestamp: Simulation time at which it happened.
        status: Current CrimeStatus.
    """

    id: str
    title: str
    description: str
    culprit_id: str
    victim_id: str
    location_id: str
    timestamp: float
    status: CrimeStatus
