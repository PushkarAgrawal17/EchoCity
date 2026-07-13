"""Unit tests for the NPCManager FSM and Event Publishing layer."""

import pytest
from unittest.mock import MagicMock
from app.agents.agent import Agent, Relationship
from app.agents.agent_state import AgentState
from app.agents.npc_manager import NPCManager
from app.events.event_bus import EventBus
from app.events.event_type import EventType
from app.simulation.location import Location
from app.simulation.location_type import LocationType


def test_npc_manager_planning_event_on_hour_boundary() -> None:
    event_bus = EventBus()
    published_events = []
    
    # Subscribe to EventBus to capture published events
    event_bus.subscribe(EventType.TICK, published_events.append)
    
    manager = NPCManager(event_bus)
    loc = Location(id="cafe", name="Cafe", type=LocationType.CAFE)
    agent = Agent(
        agent_id="agent_1",
        name="Alice",
        occupation="Healer",
        location=loc,
        daily_schedule={8: ("Inspect ward", "cafe", AgentState.WORKING)}
    )
    manager.register(agent)
    
    # Trigger update on the hour (e.g. 8:00, 28800 seconds)
    manager.update_all(28800.0, MagicMock())
    
    # Assertions
    assert len(published_events) == 1
    event = published_events[0]
    assert event.event_type == EventType.TICK
    assert event.payload["reasoning_task"] == "Planning"
    assert event.payload["agent_name"] == "Alice"
    assert event.payload["time"] == "08:00"


def test_npc_manager_theft_opportunity_at_bank() -> None:
    event_bus = EventBus()
    published_events = []
    
    event_bus.subscribe(EventType.THEFT_OPPORTUNITY, published_events.append)
    
    manager = NPCManager(event_bus)
    loc = Location(id="bank", name="Bank", type=LocationType.BANK)
    agent = Agent(
        agent_id="agent_1",
        name="Alice",
        location=loc,
        stress=0.85  # High stress (> 0.70)
    )
    manager.register(agent)
    
    # Trigger update (minute is not 0 to avoid hour boundary planning logs)
    manager.update_all(60.0, MagicMock())
    
    # Assertions
    assert len(published_events) == 1
    event = published_events[0]
    assert event.event_type == EventType.THEFT_OPPORTUNITY
    assert event.payload["agent_name"] == "Alice"
    assert event.payload["location"] == "Bank"


def test_npc_manager_relationship_changed_event() -> None:
    event_bus = EventBus()
    published_events = []
    
    event_bus.subscribe(EventType.RELATIONSHIP_CHANGED, published_events.append)
    
    manager = NPCManager(event_bus)
    rel = Relationship(
        trust=0.8,
        friendship=0.5,
        respect=0.5,
        fear=0.0,
        romantic=0.0,
        hidden_opinion="",
        shared_memory=""
    )
    agent = Agent(
        agent_id="agent_1",
        name="Alice",
        relationships={"bob": rel}
    )
    manager.register(agent)
    
    # Modify relationship value
    rel.trust = 0.5  # Significant change (> 0.05)
    
    # Trigger update
    manager.update_all(60.0, MagicMock())
    
    # Assertions
    assert len(published_events) == 1
    event = published_events[0]
    assert event.event_type == EventType.RELATIONSHIP_CHANGED
    assert event.payload["agent_id"] == "agent_1"
    assert event.payload["target_id"] == "bob"
    assert event.payload["old_trust"] == 0.8
    assert event.payload["new_trust"] == 0.5


def test_npc_manager_conversation_started_event() -> None:
    event_bus = EventBus()
    published_events = []
    
    event_bus.subscribe(EventType.CONVERSATION_STARTED, published_events.append)
    
    manager = NPCManager(event_bus)
    loc = Location(id="cafe", name="Cafe", type=LocationType.CAFE)
    
    # Two co-located agents
    a1 = Agent(agent_id="agent_1", name="Alice", location=loc, state=AgentState.IDLE)
    a2 = Agent(agent_id="agent_2", name="Bob", location=loc, state=AgentState.IDLE)
    
    manager.register(a1)
    manager.register(a2)
    
    # Trigger update
    manager.update_all(60.0, MagicMock())
    
    # Assertions
    assert len(published_events) == 1
    event = published_events[0]
    assert event.event_type == EventType.CONVERSATION_STARTED
    assert event.payload["speaker_name"] == "Alice"
    assert event.payload["listener_name"] == "Bob"
    assert event.payload["location"] == "Cafe"
