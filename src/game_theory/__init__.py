from dataclasses import dataclass
from typing import Optional


@dataclass
class DialogueMove:
    """A possible dialogue move by a participant"""
    move_type: str  # DEEPEN, CHALLENGE, SUPPORT, QUESTION, SYNTHESIZE, CONCLUDE
    target: Optional[str] = None  # participant_id or None for group
    intensity: float = 0.5  # 0-1


# Move types constant
MOVE_TYPES = [
    "DEEPEN",
    "CHALLENGE",
    "SUPPORT",
    "QUESTION",
    "SYNTHESIZE",
    "CONCLUDE"
]

# Export new classes
from .agent_objective import AgentObjective
from .strategic_coordinator import StrategicCoordinator

__all__ = [
    'DialogueMove',
    'MOVE_TYPES',
    'AgentObjective',
    'StrategicCoordinator'
]