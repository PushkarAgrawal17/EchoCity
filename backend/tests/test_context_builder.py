"""Unit tests for the ContextBuilder layer."""

import pytest
from app.llm.context_builder import ContextBuilder
from app.agents.agent import Agent, Relationship
from app.agents.agent_state import AgentState
from app.memory.memory import Memory
from app.memory.memory_type import MemoryType
from app.simulation.location import Location
from app.simulation.location_type import LocationType


def test_context_builder_conversation() -> None:
    loc = Location(id="cafe", name="Cafe", type=LocationType.CAFE)
    speaker = Agent(
        agent_id="agent_1",
        name="Alice",
        state=AgentState.IDLE,
        location=loc,
        occupation="Healer",
        speech_style={"vocabulary": "rich", "tone": "formal", "sentence_length": "long", "favorite_expressions": ["Indeed", "Alas", "Oh"]}
    )
    listener = Agent(
        agent_id="agent_2",
        name="Bob",
        state=AgentState.IDLE,
        location=loc,
        occupation="Builder",
        speech_style={"vocabulary": "simple", "tone": "cheerful"}
    )
    memory = Memory(
        id="mem_1",
        summary="Thomas is hiding building plans near the market.",
        type=MemoryType.PERSONAL,
        source="self",
        timestamp=0.0,
        confidence=1.0
    )

    ctx = ContextBuilder.build(
        reasoning_task="Conversation",
        current_agent=speaker,
        nearby_agents=[listener],
        current_scene=loc,
        relevant_memories=[memory]
    )

    assert ctx["speaker"] == "Alice"
    assert ctx["speaker_occupation"] == "Healer"
    assert ctx["speaker_speech"]["vocabulary"] == "rich"
    assert len(ctx["speaker_speech"]["favorite_expressions"]) == 2  # Capped at 2
    assert ctx["listener"] == "Bob"
    assert ctx["listener_occupation"] == "Builder"
    assert ctx["location"] == "Cafe"
    assert ctx["memory"] == "Thomas is hiding building plans near the market."


def test_context_builder_planning() -> None:
    agent = Agent(
        agent_id="agent_1",
        name="Alice",
        occupation="Healer",
        personality={
            "big_five": {"openness": 0.8, "conscientiousness": 0.5, "extraversion": 0.3, "agreeableness": 0.9, "neuroticism": 0.2}
        },
        stress=0.45,
        suspicion=0.1
    )

    ctx = ContextBuilder.build(
        reasoning_task="Planning",
        current_agent=agent,
        current_scene={"time": "08:00", "schedule_activity": "Homeroom supervision"}
    )

    assert ctx["agent_name"] == "Alice"
    assert ctx["occupation"] == "Healer"
    assert ctx["traits"] == "O:80, C:50, E:30, A:90, N:20"
    assert "Stress:45%" in ctx["needs"]
    assert "Suspicion:10%" in ctx["needs"]
    assert ctx["time"] == "08:00"
    assert ctx["schedule_activity"] == "Homeroom supervision"


def test_context_builder_crime_decision() -> None:
    agent = Agent(
        agent_id="agent_1",
        name="Alice",
        occupation="Healer",
        personality={
            "big_five": {"openness": 0.8, "conscientiousness": 0.5}
        },
        secrets={"regret": "Has debts to repay"},
        stress=0.75,
        suspicion=0.2
    )

    ctx = ContextBuilder.build(
        reasoning_task="Crime Decision",
        current_agent=agent,
        current_scene={"opportunity": "Unsupervised bank vault"}
    )

    assert ctx["agent_name"] == "Alice"
    assert ctx["opportunity"] == "Unsupervised bank vault"
    assert ctx["stress"] == "75%"
    assert ctx["suspicion"] == "20%"
    assert ctx["personality"] == "O:80, C:50"
    assert ctx["secrets"] == "Has debts to repay"


def test_context_builder_witness_reasoning() -> None:
    agent = Agent(
        agent_id="agent_1",
        name="Alice"
    )
    rel = Relationship(
        trust=0.3,
        friendship=0.2,
        respect=0.4,
        fear=0.6,
        romantic=0.0,
        hidden_opinion="Untrustworthy",
        shared_memory="Met once"
    )
    relationships = {"culprit_id": rel}
    mem = Memory(
        id="mem_w",
        summary="Saw Marcus stealing gold coins from the market.",
        type=MemoryType.WITNESS,
        source="self",
        timestamp=0.0,
        confidence=1.0
    )

    ctx = ContextBuilder.build(
        reasoning_task="Witness Reasoning",
        current_agent=agent,
        relevant_memories=[mem],
        relationships=relationships,
        player_influence={"culprit_id": "culprit_id"}
    )

    assert ctx["agent_name"] == "Alice"
    assert ctx["witnessed_event"] == "Saw Marcus stealing gold coins from the market."
    assert ctx["trust_in_culprit"] == 0.3
    assert ctx["fear_of_culprit"] == 0.6


def test_context_builder_diary_generation() -> None:
    agent = Agent(
        agent_id="agent_1",
        name="Alice",
        occupation="Healer",
        personality={"traits": ["diligent", "compassionate"]}
    )
    m1 = Memory(id="m1", summary="Treated a patient.", type=MemoryType.PERSONAL, source="self", timestamp=0.0, confidence=1.0)
    m2 = Memory(id="m2", summary="Argued with Thomas.", type=MemoryType.PERSONAL, source="self", timestamp=0.0, confidence=1.0)

    ctx = ContextBuilder.build(
        reasoning_task="Diary Generation",
        current_agent=agent,
        relevant_memories=[m1, m2],
        player_influence=["Previous entry text."]
    )

    assert ctx["agent_name"] == "Alice"
    assert ctx["occupation"] == "Healer"
    assert ctx["personality"] == {"traits": ["diligent", "compassionate"]}
    assert ctx["recent_memories"] == ["Treated a patient.", "Argued with Thomas."]
    assert ctx["previous_entries"] == ["Previous entry text."]
