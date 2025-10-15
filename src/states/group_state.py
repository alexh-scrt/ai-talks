from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
import json
from .dyad_state import DyadState
from .tension_state import TensionState


@dataclass
class GroupDiscussionState:
    """Global state for the entire group discussion"""
    
    # Topic
    topic: str
    target_depth: int
    
    # Participants
    participants: Dict[str, 'ParticipantState'] = field(default_factory=dict)
    participant_order: List[str] = field(default_factory=list)
    
    # Discussion progress
    turn_number: int = 0
    exchanges: List[Dict] = field(default_factory=list)
    
    # Depth tracking (shared across all participants)
    aspects_explored: Set[str] = field(default_factory=set)
    max_depth_reached: int = 1
    
    # Group dynamics
    dominant_speaker: Optional[str] = None
    coalitions: List[Set[str]] = field(default_factory=list)
    active_disagreement: bool = False
    
    # Termination tracking
    convergence_level: float = 0.0
    novelty_score: float = 1.0
    
    # Redundancy control tracking
    dyads: Dict[Tuple[str, str], DyadState] = field(default_factory=dict)
    tensions: Dict[Tuple[str, str], TensionState] = field(default_factory=dict)
    last_speaker_id: Optional[str] = None
    current_tension: Optional[Tuple[str, str]] = None
    
    def get_participant(self, participant_id: str) -> 'ParticipantState':
        """Get participant state by ID"""
        return self.participants[participant_id]
    
    def get_other_participants(self, participant_id: str) -> List['ParticipantState']:
        """Get all other participants"""
        return [p for pid, p in self.participants.items() if pid != participant_id]
    
    def get_recent_speakers(self, n: int = 3) -> List[str]:
        """Get last N speakers"""
        if not self.exchanges:
            return []
        return [e["speaker_id"] for e in self.exchanges[-n:] if "speaker_id" in e]
    
    def add_exchange(self, exchange: Dict):
        """Add exchange and update turn number"""
        self.exchanges.append(exchange)
        self.turn_number += 1
    
    def get_dyad_state(self, speaker_a: str, speaker_b: str) -> DyadState:
        """Get or create dyad state for two speakers"""
        pair = tuple(sorted([speaker_a, speaker_b]))
        if pair not in self.dyads:
            self.dyads[pair] = DyadState(pair=pair, max_volleys=2)
        return self.dyads[pair]
    
    def update_dyad(self, current_speaker: str):
        """Update dyad tracking after a turn"""
        if self.last_speaker_id and self.last_speaker_id != current_speaker:
            dyad = self.get_dyad_state(self.last_speaker_id, current_speaker)
            dyad.increment()
        self.last_speaker_id = current_speaker
    
    def get_tension_state(self, concept_a: str, concept_b: str) -> TensionState:
        """Get or create tension state"""
        pair = tuple(sorted([concept_a, concept_b]))
        if pair not in self.tensions:
            self.tensions[pair] = TensionState(pair=pair)
        return self.tensions[pair]
    
    def to_json(self) -> str:
        """Serialize state to JSON for storage"""
        state_dict = {
            "topic": self.topic,
            "target_depth": self.target_depth,
            "turn_number": self.turn_number,
            "exchanges": self.exchanges,
            "aspects_explored": list(self.aspects_explored),
            "max_depth_reached": self.max_depth_reached,
            "dominant_speaker": self.dominant_speaker,
            "active_disagreement": self.active_disagreement,
            "convergence_level": self.convergence_level,
            "novelty_score": self.novelty_score
        }
        return json.dumps(state_dict, indent=2)
    
    def __repr__(self) -> str:
        return (
            f"GroupDiscussionState(topic='{self.topic}', "
            f"depth={self.target_depth}, "
            f"participants={len(self.participants)}, "
            f"turns={self.turn_number})"
        )