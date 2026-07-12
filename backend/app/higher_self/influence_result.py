"""Defines the InfluenceResult value object."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InfluenceResult:
    """The outcome of applying an Influence, described in world terms.

    InfluenceResult never exposes internal implementation details such
    as Memory objects. It only describes whether the influence took
    effect and who was affected.

    Attributes:
        success: Whether the influence was successfully applied.
        message: A human-readable description of the outcome.
        affected_agents: The agent_ids whose cognitive state changed.
    """

    success: bool
    message: str
    affected_agents: list[str] = field(default_factory=list)