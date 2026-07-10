"""AgentState: the set of states an Agent can occupy."""

from enum import Enum, auto


class AgentState(Enum):
    """Discrete states an Agent can be in.

    State transitions are not implemented here — this enum only defines
    the possible values. Deciding *when* an agent changes state belongs to
    future milestones (state machine / decision logic).
    """

    IDLE = auto()
    WALKING = auto()
    WORKING = auto()
    SLEEPING = auto()
    TALKING = auto()