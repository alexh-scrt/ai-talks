# src/game_theory/agent_objective.py

from dataclasses import dataclass
from typing import Dict, Optional
from src.game_theory import DialogueMove


@dataclass
class AgentObjective:
    """
    Explicit utility vector for strategic decision-making.
    
    Each agent has an objective that guides their strategic choices
    in discussion. These are not rigid rules but weighted preferences
    that influence move selection and scoring.
    
    All objective dimensions range from 0.0 to 1.0, where:
    - 0.0 = No weight/importance
    - 0.5 = Moderate weight
    - 1.0 = Maximum weight/priority
    """
    
    # Core objective dimensions (all 0.0 to 1.0)
    truth_seeking: float = 0.5          # Prioritize empirical accuracy and logical rigor
    ethical_coherence: float = 0.5       # Maintain moral consistency and principles
    metaphoric_elegance: float = 0.5     # Use vivid analogies and creative expression
    empirical_grounding: float = 0.5     # Cite evidence and concrete examples
    dialectical_tension: float = 0.5     # Create productive disagreement and debate

    def get_dominant_objective(self) -> str:
        """
        Return the highest-weighted objective.
        
        Returns:
            Name of the dominant objective dimension
        """
        objectives = {
            "truth_seeking": self.truth_seeking,
            "ethical_coherence": self.ethical_coherence,
            "metaphoric_elegance": self.metaphoric_elegance,
            "empirical_grounding": self.empirical_grounding,
            "dialectical_tension": self.dialectical_tension
        }
        return max(objectives.items(), key=lambda x: x[1])[0]
    
    def get_objective_vector(self) -> Dict[str, float]:
        """Return objectives as a dictionary"""
        return {
            "truth_seeking": self.truth_seeking,
            "ethical_coherence": self.ethical_coherence,
            "metaphoric_elegance": self.metaphoric_elegance,
            "empirical_grounding": self.empirical_grounding,
            "dialectical_tension": self.dialectical_tension
        }

    def score_move(self, move: DialogueMove, context: Dict) -> float:
        """
        Score how well a move aligns with this agent's objectives.
        
        Args:
            move: The dialogue move being evaluated
            context: Contextual information about the move
                - uses_metaphor: bool
                - cites_evidence: bool
                - challenges_assumption: bool
                - builds_consensus: bool
                - logical_structure: bool
                - ethical_consideration: bool
                - uses_tool_results: bool
        
        Returns:
            Alignment score (0.0 to 1.0)
        """
        score = 0.0
        
        # Move type base scoring
        if move.move_type == "CHALLENGE":
            score += self.dialectical_tension * 0.4
            score += self.truth_seeking * 0.3
            if context.get("challenges_assumption"):
                score += self.truth_seeking * 0.2
        
        elif move.move_type == "SUPPORT":
            score += self.ethical_coherence * 0.4
            score -= self.dialectical_tension * 0.2  # Reduces tension
            if context.get("builds_consensus"):
                score += self.ethical_coherence * 0.2
        
        elif move.move_type == "DEEPEN":
            score += self.truth_seeking * 0.5
            score += self.empirical_grounding * 0.3
        
        elif move.move_type == "QUESTION":
            score += self.truth_seeking * 0.4
            score += self.empirical_grounding * 0.3
        
        elif move.move_type == "SYNTHESIZE":
            score += self.ethical_coherence * 0.4
            score += self.truth_seeking * 0.3
        
        elif move.move_type == "CONCLUDE":
            # Conclude aligns with completion, not specific objectives
            score += 0.3
        
        # Context-based bonuses
        if context.get("uses_metaphor"):
            score += self.metaphoric_elegance * 0.2
        
        if context.get("cites_evidence") or context.get("uses_tool_results"):
            score += self.empirical_grounding * 0.3
        
        if context.get("logical_structure"):
            score += self.truth_seeking * 0.2
        
        if context.get("ethical_consideration"):
            score += self.ethical_coherence * 0.2
        
        # Normalize to 0-1 range
        return min(1.0, max(0.0, score))

    @staticmethod
    def from_personality(personality: str) -> 'AgentObjective':
        """
        Create objective vector from personality type.
        
        Maps personality archetypes to objective preferences.
        
        Args:
            personality: One of analytical, skeptical, creative, 
                        collaborative, assertive, cautious
        
        Returns:
            AgentObjective tuned to that personality
        """
        mapping = {
            "analytical": AgentObjective(
                truth_seeking=0.9,
                empirical_grounding=0.8,
                dialectical_tension=0.5,
                ethical_coherence=0.6,
                metaphoric_elegance=0.3
            ),
            "skeptical": AgentObjective(
                dialectical_tension=0.9,
                truth_seeking=0.7,
                empirical_grounding=0.6,
                ethical_coherence=0.4,
                metaphoric_elegance=0.4
            ),
            "creative": AgentObjective(
                metaphoric_elegance=0.9,
                truth_seeking=0.5,
                ethical_coherence=0.6,
                dialectical_tension=0.5,
                empirical_grounding=0.4
            ),
            "collaborative": AgentObjective(
                ethical_coherence=0.9,
                truth_seeking=0.6,
                dialectical_tension=0.3,
                metaphoric_elegance=0.5,
                empirical_grounding=0.5
            ),
            "assertive": AgentObjective(
                dialectical_tension=0.7,
                ethical_coherence=0.7,
                truth_seeking=0.6,
                empirical_grounding=0.5,
                metaphoric_elegance=0.4
            ),
            "cautious": AgentObjective(
                empirical_grounding=0.9,
                truth_seeking=0.8,
                ethical_coherence=0.7,
                dialectical_tension=0.3,
                metaphoric_elegance=0.3
            )
        }
        
        return mapping.get(personality, AgentObjective())

    def __repr__(self) -> str:
        dominant = self.get_dominant_objective()
        return f"AgentObjective(dominant={dominant})"