"""NPCManager: manages agents as FSMs and translates transitions into published events."""

import logging
from typing import Any, Dict, Optional
from app.agents.agent import Agent
from app.agents.agent_manager import AgentManager
from app.agents.agent_state import AgentState
from app.events.event import Event
from app.events.event_bus import EventBus
from app.events.event_type import EventType

logger = logging.getLogger(__name__)


class NPCManager(AgentManager):
    """NPC Manager for EchoCity.

    Extends AgentManager to treat NPCs as deterministic finite state machines.
    Monitors NPC state/need changes during tick updates and publishes events
    to the EventBus when cognitive reasoning (LLM tasks) is required.
    
    CRITICAL: This manager never communicates directly with the LLM.
    """

    def __init__(self, event_bus: EventBus) -> None:
        """Create an NPCManager.

        Args:
            event_bus: The simulation's EventBus.
        """
        super().__init__()
        self.event_bus = event_bus
        # Track previous states to detect state transitions
        self._prev_stress: Dict[str, float] = {}
        self._prev_trust: Dict[str, Dict[str, float]] = {}

    def register(self, agent: Agent) -> None:
        """Register an NPC/Agent and initialize tracking states."""
        super().register(agent)
        self._prev_stress[agent.agent_id] = agent.stress
        self._prev_trust[agent.agent_id] = {
            target_id: rel.trust for target_id, rel in agent.relationships.items()
        }

    def update_all(self, current_time_seconds: float = 0.0, location_manager: Any = None) -> None:
        """Advance the FSM for all NPCs and publish events when reasoning is needed."""
        # 1. Step the FSM state machine for each registered NPC
        for agent in self._agents.values():
            old_state = agent.state
            old_location = agent.location
            old_goal = agent.goal

            try:
                agent.update(current_time_seconds, location_manager)
            except TypeError:
                agent.update()

            # 2. Extract clock details
            hour = int((current_time_seconds % 86400) // 3600)
            minute = int((current_time_seconds % 3600) // 60)

            # 3. Detect schedule/planning transitions (at the start of each hour)
            if minute == 0:
                self.event_bus.publish(
                    Event(
                        event_type=EventType.TICK,
                        timestamp=current_time_seconds,
                        payload={
                            "reasoning_task": "Planning",
                            "agent_id": agent.agent_id,
                            "agent_name": agent.name,
                            "occupation": agent.occupation,
                            "traits": agent.personality,
                            "needs": {
                                "energy": agent.energy,
                                "confidence": agent.confidence,
                                "suspicion": agent.suspicion
                            },
                            "time": f"{hour:02d}:00",
                            "schedule_activity": agent.goal or "Routine duties"
                        }
                    )
                )

            # 4. Detect theft opportunity (stress > 0.70 at the Bank)
            if agent.stress > 0.70 and agent.location and agent.location.name == "Bank":
                self.event_bus.publish(
                    Event(
                        event_type=EventType.THEFT_OPPORTUNITY,
                        timestamp=current_time_seconds,
                        payload={
                            "agent_id": agent.agent_id,
                            "agent_name": agent.name,
                            "location": agent.location.name,
                            "opportunity": "Vault keys left unattended due to distraction"
                        }
                    )
                )

            # 5. Detect relationship change events
            prev_agent_trusts = self._prev_trust.get(agent.agent_id, {})
            for target_id, rel in agent.relationships.items():
                prev_trust = prev_agent_trusts.get(target_id, rel.trust)
                if abs(rel.trust - prev_trust) > 0.05:
                    self.event_bus.publish(
                        Event(
                            event_type=EventType.RELATIONSHIP_CHANGED,
                            timestamp=current_time_seconds,
                            payload={
                                "agent_id": agent.agent_id,
                                "target_id": target_id,
                                "old_trust": prev_trust,
                                "new_trust": rel.trust
                            }
                        )
                    )
                prev_agent_trusts[target_id] = rel.trust
            self._prev_trust[agent.agent_id] = prev_agent_trusts

            # 6. Detect Court started (detective is working/investigating at the Court)
            if agent.agent_id == "ethan_cross" and agent.location and agent.location.name == "Court":
                # Find if any other agent is at the Court (potential trial)
                other_present = [
                    other.name for other in self._agents.values()
                    if other.agent_id != "ethan_cross" and other.location and other.location.name == "Court"
                ]
                if other_present:
                    self.event_bus.publish(
                        Event(
                            event_type=EventType.COURT_STARTED,
                            timestamp=current_time_seconds,
                            payload={
                                "detective_name": agent.name,
                                "participants": other_present,
                                "location": "Court"
                            }
                        )
                    )

        # 7. Detect co-location/dialogue starting (Conversation Started)
        # Scan for co-located agents not working/sleeping who can gossip
        co_located_groups: Dict[str, list] = {}
        for agent in self._agents.values():
            if agent.location:
                co_located_groups.setdefault(agent.location.name, []).append(agent)

        for loc_name, group in co_located_groups.items():
            if len(group) >= 2:
                # Find interactive candidates
                interactives = [
                    a for a in group 
                    if a.state not in (AgentState.SLEEPING, AgentState.WORKING)
                ]
                if len(interactives) >= 2:
                    speaker, listener = interactives[0], interactives[1]
                    self.event_bus.publish(
                        Event(
                            event_type=EventType.CONVERSATION_STARTED,
                            timestamp=current_time_seconds,
                            payload={
                                "speaker_id": speaker.agent_id,
                                "speaker_name": speaker.name,
                                "listener_id": listener.agent_id,
                                "listener_name": listener.name,
                                "location": loc_name
                            }
                        )
                    )
