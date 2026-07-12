"""Defines the Influence value object."""

from dataclasses import dataclass

from app.higher_self.influence_type import InfluenceType


@dataclass(frozen=True)
class Influence:
    """An immutable expression of player intent toward one or two citizens.

    Influence describes *what* the player wants to nudge, not *how* it
    is realized. HigherSelfEngine alone decides how an Influence is
    translated into a change in the city's cognitive state.

    Attributes:
        type: The kind of intent being expressed.
        primary_target: The agent_id this influence is centered on.
        secondary_target: An optional second agent_id, for relational
            intents (e.g. CONNECT).
        reference: An optional pointer to existing information the
            intent should act on (e.g. for REMEMBER). Meaning of this
            value is owned entirely by HigherSelfEngine.
    """

    type: InfluenceType
    primary_target: str
    secondary_target: str | None = None
    reference: str | None = None