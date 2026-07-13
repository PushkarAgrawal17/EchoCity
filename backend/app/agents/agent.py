"""Agent: represents a single NPC's simulation state.

An Agent contains their identity, traits, beliefs, daily schedule, needs,
inventory, secrets, and relationship map. It updates its state/location
deterministically based on the simulation clock.
"""

from dataclasses import dataclass, field
from typing import Any
from app.agents.agent_state import AgentState
from app.simulation.location import Location


@dataclass
class Relationship:
    """Represents a directional relationship from one agent to another."""
    trust: float
    friendship: float
    respect: float
    fear: float
    romantic: float
    hidden_opinion: str
    shared_memory: str


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

    # Personality and identity fields from NPC Bible
    age: int = 0
    occupation: str = ""
    home: str = ""
    personality: dict[str, Any] = field(default_factory=dict)
    speech_style: dict[str, Any] = field(default_factory=dict)
    habits: dict[str, Any] = field(default_factory=dict)
    inventory: list[str] = field(default_factory=list)
    secrets: dict[str, Any] = field(default_factory=dict)
    beliefs: dict[str, Any] = field(default_factory=dict)

    # Needs / Cognitive State
    stress: float = 0.0
    suspicion: float = 0.0
    energy: float = 1.0
    confidence: float = 1.0
    emotion: str = "neutral"

    # Relationships map: target_agent_id -> Relationship
    relationships: dict[str, Relationship] = field(default_factory=dict)

    # Schedule map: hour (int) -> (goal_description, location_id, state)
    daily_schedule: dict[int, tuple[str, str, AgentState]] = field(default_factory=dict)

    def update(self, current_time_seconds: float = 0.0, location_manager: Any = None) -> None:
        """Update this agent for the current simulation tick.

        Checks their daily schedule at the top of each simulation hour,
        and triggers state, goal, and location transitions.
        """
        if not self.daily_schedule or location_manager is None:
            return

        # Calculate simulation hour and minute
        # 1 tick = 60 simulation seconds
        hour = int((current_time_seconds % 86400) // 3600)
        minute = int((current_time_seconds % 3600) // 60)

        # Trigger schedule changes on the hour boundary
        if minute == 0:
            entry = self.daily_schedule.get(hour)
            if entry:
                goal, loc_id, state = entry
                self.goal = goal
                self.state = state
                
                # Retrieve the target Location object and move the agent
                target_loc = location_manager.get(loc_id)
                if target_loc:
                    self.location = target_loc
