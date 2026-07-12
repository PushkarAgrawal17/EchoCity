"""Agent: represents a single NPC's simulation state.

An Agent is pure state — identity, current state, current goal, current
location. It has no memory, relationships, emotions, schedule, dialogue,
or AI. Those are separate subsystems introduced in later milestones.
"""

from dataclasses import dataclass

from app.agents.agent_state import AgentState
from app.simulation.location import Location


@dataclass
class Agent:
    """A single NPC's simulation state.

    Attributes:
        agent_id: Unique, stable identifier for this agent.
        name: Display name.
        state: Current AgentState.
        goal: Free-text description of what the agent is currently trying
            to do. ``None`` means the agent has no active goal.
        location: The Location this agent currently occupies. ``None``
            means location is not yet set.
    """

    agent_id: str
    name: str
    state: AgentState = AgentState.IDLE
    goal: str | None = None
    location: Location | None = None

    def update(self) -> None:
        """Update this agent for the current simulation tick.

        Placeholder for now — Agent has no autonomous behavior yet. Future
        milestones will drive state transitions, goal selection, and
        movement from here.
        """
