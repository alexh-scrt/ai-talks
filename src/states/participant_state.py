from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"


class PersonalityArchetype(Enum):
    ANALYTICAL = "analytical"
    COLLABORATIVE = "collaborative"
    ASSERTIVE = "assertive"
    CAUTIOUS = "cautious"
    CREATIVE = "creative"
    SKEPTICAL = "skeptical"


@dataclass
class ParticipantState:
    """State for each discussion participant"""
    
    # Identity
    participant_id: str
    name: str
    gender: Gender
    personality: PersonalityArchetype
    expertise_area: str
    core_beliefs: List[str] = field(default_factory=list)
    
    # Strategic Objective
    objective: Optional['AgentObjective'] = None
    
    # Dynamic discussion state
    confidence_level: float = 0.7
    curiosity_level: float = 0.8
    engagement_level: float = 0.8
    
    # Social dynamics
    relationships: Dict[str, float] = field(default_factory=dict)
    respect_levels: Dict[str, float] = field(default_factory=dict)
    
    # Conversation tracking
    speaking_turns: int = 0
    words_spoken: int = 0
    questions_asked: int = 0
    positions_taken: List[str] = field(default_factory=list)
    agreements_made: List[str] = field(default_factory=list)
    challenges_made: List[str] = field(default_factory=list)
    
    # Topic exploration
    depth_explored: int = 1
    aspects_covered: Set[str] = field(default_factory=set)
    
    # Turn-taking state
    wants_to_speak: float = 0.5
    last_spoke_turn: int = -1
    was_addressed: bool = False
    
    def __post_init__(self):
        """Initialize objective from personality if not provided"""
        if self.objective is None:
            # Import here to avoid circular import
            from src.game_theory.agent_objective import AgentObjective
            self.objective = AgentObjective.from_personality(self.personality.value)
            logger.debug(f"{self.name}'s objective initialized: {self.objective.get_dominant_objective()}")
    
    def update_relationship(self, other_id: str, delta: float):
        """Update relationship with another participant"""
        current = self.relationships.get(other_id, 0.0)
        self.relationships[other_id] = max(-1.0, min(1.0, current + delta))
    
    def update_respect(self, other_id: str, delta: float):
        """Update respect for another participant"""
        current = self.respect_levels.get(other_id, 0.5)
        self.respect_levels[other_id] = max(0.0, min(1.0, current + delta))
    
    def get_pronouns(self) -> str:
        """Get pronouns based on gender"""
        return {
            Gender.MALE: "he/him",
            Gender.FEMALE: "she/her",
            Gender.NON_BINARY: "they/them"
        }[self.gender]
    
    def __repr__(self) -> str:
        return (
            f"ParticipantState(name='{self.name}', "
            f"personality={self.personality.value}, "
            f"expertise='{self.expertise_area}', "
            f"turns={self.speaking_turns})"
        )