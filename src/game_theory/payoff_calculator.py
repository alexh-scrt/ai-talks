import numpy as np
from typing import Dict, Tuple
from src.states.participant_state import ParticipantState, PersonalityArchetype
from src.states.group_state import GroupDiscussionState
from src.game_theory import DialogueMove


class PayoffCalculator:
    """Calculates utility payoffs for each possible dialogue move"""
    
    def calculate_move_payoffs(
        self,
        speaker: ParticipantState,
        group_state: GroupDiscussionState
    ) -> Dict[str, float]:
        """
        Calculate utility for each possible dialogue move
        
        Returns: Dict of move_type -> payoff score
        """
        payoffs = {}
        
        other_participants = group_state.get_other_participants(speaker.participant_id)
        recent_speakers = group_state.get_recent_speakers(n=2)
        
        # DEEPEN move payoff
        depth_gap = group_state.target_depth - speaker.depth_explored
        recent_deepening = any(
            e.get("move") == "DEEPEN" 
            for e in group_state.exchanges[-3:] if group_state.exchanges
        )
        
        payoffs["DEEPEN"] = (
            depth_gap * 0.3 +
            speaker.curiosity_level * 0.4 +
            (0.3 if not recent_deepening else 0.1)
        )
        
        # CHALLENGE move payoff
        can_challenge = len(recent_speakers) > 0
        if can_challenge and recent_speakers[-1] in group_state.participants:
            last_speaker_id = recent_speakers[-1]
            last_speaker = group_state.get_participant(last_speaker_id)
            relationship = speaker.relationships.get(last_speaker_id, 0.0)
            
            payoffs["CHALLENGE"] = (
                (1.0 if speaker.personality == PersonalityArchetype.SKEPTICAL else 0.5) * 0.3 +
                last_speaker.confidence_level * 0.3 +
                max(0, -relationship) * 0.2 +
                (0.2 if speaker.confidence_level > 0.6 else 0.1)
            )
        else:
            payoffs["CHALLENGE"] = 0.0
        
        # SUPPORT move payoff
        if can_challenge and recent_speakers and recent_speakers[-1] in group_state.participants:
            last_speaker_id = recent_speakers[-1]
            relationship = speaker.relationships.get(last_speaker_id, 0.0)
            respect = speaker.respect_levels.get(last_speaker_id, 0.5)
            
            payoffs["SUPPORT"] = (
                (1.0 if speaker.personality == PersonalityArchetype.COLLABORATIVE else 0.5) * 0.3 +
                max(0, relationship) * 0.4 +
                respect * 0.3
            )
        else:
            payoffs["SUPPORT"] = 0.0
        
        # QUESTION move payoff
        payoffs["QUESTION"] = (
            (1.0 if speaker.personality == PersonalityArchetype.ANALYTICAL else 0.6) * 0.4 +
            speaker.curiosity_level * 0.3 +
            (0.3 if speaker.questions_asked < 3 else 0.1)
        )
        
        # SYNTHESIZE move payoff
        num_recent_perspectives = len(set(recent_speakers))
        disagreement_level = 1.0 - group_state.convergence_level
        sweet_spot = abs(disagreement_level - 0.5) < 0.3
        
        payoffs["SYNTHESIZE"] = (
            (1.0 if speaker.personality in [PersonalityArchetype.CREATIVE, PersonalityArchetype.ANALYTICAL] else 0.5) * 0.3 +
            min(num_recent_perspectives / 3, 1.0) * 0.3 +
            (0.4 if sweet_spot else 0.2)
        )
        
        # CONCLUDE move payoff
        depth_reached = group_state.max_depth_reached >= group_state.target_depth
        aspects_sufficient = len(group_state.aspects_explored) >= group_state.target_depth * 3
        
        payoffs["CONCLUDE"] = (
            (0.4 if depth_reached else 0.0) +
            (0.3 if aspects_sufficient else 0.0) +
            (0.3 if group_state.novelty_score < 0.3 else 0.0)
        )
        
        return payoffs
    
    def recommend_move_and_target(
        self,
        speaker: ParticipantState,
        group_state: GroupDiscussionState
    ) -> Tuple[DialogueMove, float]:
        """
        Recommend both move type and target
        
        Returns: (DialogueMove, confidence)
        """
        payoffs = self.calculate_move_payoffs(speaker, group_state)
        
        best_move_type = max(payoffs.items(), key=lambda x: x[1])[0]
        confidence = payoffs[best_move_type]
        
        # Determine target
        target = None
        if best_move_type in ["CHALLENGE", "SUPPORT", "QUESTION"]:
            recent_speakers = group_state.get_recent_speakers(n=2)
            if recent_speakers and recent_speakers[-1] in group_state.participants:
                target = recent_speakers[-1]
        
        # Determine intensity
        intensity_map = {
            PersonalityArchetype.ASSERTIVE: 0.8,
            PersonalityArchetype.SKEPTICAL: 0.7,
            PersonalityArchetype.CAUTIOUS: 0.4,
            PersonalityArchetype.COLLABORATIVE: 0.5,
            PersonalityArchetype.ANALYTICAL: 0.6,
            PersonalityArchetype.CREATIVE: 0.7
        }
        intensity = intensity_map[speaker.personality]
        
        move = DialogueMove(
            move_type=best_move_type,
            target=target,
            intensity=intensity
        )
        
        return move, confidence