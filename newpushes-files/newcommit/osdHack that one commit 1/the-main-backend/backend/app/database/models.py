"""SQLAlchemy ORM models for EchoCity persistence."""

from typing import Any
from sqlalchemy import Boolean, Float, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


class WorldStateModel(Base):
    """Persists global simulation state."""
    __tablename__ = "world_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    tick_count: Mapped[int] = mapped_column(Integer, default=0)
    current_time: Mapped[float] = mapped_column(Float, default=0.0)
    is_running: Mapped[bool] = mapped_column(Boolean, default=False)
    active_scene: Mapped[str] = mapped_column(String(50), default="cafe")
    scene_step: Mapped[int] = mapped_column(Integer, default=0)


class LocationModel(Base):
    """Persists a physical location within EchoCity."""
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))


class AgentModel(Base):
    """Persists an agent's current state and traits."""
    __tablename__ = "agents"

    agent_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(50))
    goal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Demographic & narrative details
    age: Mapped[int] = mapped_column(Integer, default=0)
    occupation: Mapped[str] = mapped_column(String(100), default="")
    home: Mapped[str] = mapped_column(String(100), default="")

    # JSON configurations
    personality: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    speech_style: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    habits: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    inventory: Mapped[list[str]] = mapped_column(JSON, default=list)
    secrets: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    beliefs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Needs
    stress: Mapped[float] = mapped_column(Float, default=0.0)
    suspicion: Mapped[float] = mapped_column(Float, default=0.0)
    energy: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    emotion: Mapped[str] = mapped_column(String(50), default="neutral")


class MemoryModel(Base):
    """Persists a memory held by a specific agent."""
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    memory_id: Mapped[str] = mapped_column(String(50))
    agent_id: Mapped[str] = mapped_column(String(50))
    summary: Mapped[str] = mapped_column(String(500))
    type: Mapped[str] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(50))
    timestamp: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    shared: Mapped[bool] = mapped_column(Boolean, default=False)
    subject_id: Mapped[str | None] = mapped_column(String(50), nullable=True)


class RelationshipModel(Base):
    """Persists a relationship link from one agent to a target agent."""
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(String(50))
    target_agent_id: Mapped[str] = mapped_column(String(50))
    trust: Mapped[float] = mapped_column(Float)
    friendship: Mapped[float] = mapped_column(Float)
    respect: Mapped[float] = mapped_column(Float)
    fear: Mapped[float] = mapped_column(Float)
    romantic: Mapped[float] = mapped_column(Float)
    hidden_opinion: Mapped[str] = mapped_column(String(500))
    shared_memory: Mapped[str] = mapped_column(String(500))


class DiaryModel(Base):
    """Persists a diary entry written by an agent."""
    __tablename__ = "diaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(String(50))
    day: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(100), default="")
    text: Mapped[str] = mapped_column(String(2000))


class NarrativeEventModel(Base):
    """Persists generated narrative feed events."""
    __tablename__ = "narrative_events"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    day: Mapped[int] = mapped_column(Integer)
    time: Mapped[str] = mapped_column(String(20))
    location: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))
    participants: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_dialogue: Mapped[bool] = mapped_column(Boolean, default=False)
    speaker: Mapped[str | None] = mapped_column(String(100), nullable=True)
    narrative: Mapped[str] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(50), default="completed")
