import numpy as np
from typing import Dict
from src.states.participant_state import ParticipantState, PersonalityArchetype
from src.states.group_state import GroupDiscussionState


class TurnSelector:
    """Selects next speaker using game-theoretic urgency calculation"""
    
    def calculate_speaking_urgency(
        self,
        participant: ParticipantState,
        group_state: GroupDiscussionState
    ) -> float:
        """
        Calculate how much this participant wants to speak RIGHT NOW
        
        Returns: 0.0-1.0 urgency score
        """
        urgency = 0.0
        
        # Factor 1: Personality-based baseline (30%)
        personality_urgency = {
            PersonalityArchetype.ASSERTIVE: 0.7,
            PersonalityArchetype.COLLABORATIVE: 0.5,
            PersonalityArchetype.ANALYTICAL: 0.4,
            PersonalityArchetype.CREATIVE: 0.6,
            PersonalityArchetype.CAUTIOUS: 0.3,
            PersonalityArchetype.SKEPTICAL: 0.5
        }
        urgency += personality_urgency[participant.personality] * 0.3
        
        # Factor 2: Time since last spoke (20%)
        turns_since_spoke = group_state.turn_number - participant.last_spoke_turn
        if participant.last_spoke_turn == -1:
            time_factor = 0.5
        else:
            time_factor = min(1.0, turns_since_spoke / 5)
        urgency += time_factor * 0.2
        
        # Factor 3: Was just addressed (40%)
        if participant.was_addressed:
            urgency += 0.4
        
        # Factor 4: High confidence (10%)
        urgency += participant.confidence_level * 0.1
        
        # Factor 5: Engagement level (20%)
        urgency += participant.engagement_level * 0.2
        
        # Fairness adjustments
        if group_state.dominant_speaker == participant.participant_id:
            urgency *= 0.7
        
        # Balance turns
        if len(group_state.participants) > 0:
            avg_turns = np.mean([p.speaking_turns for p in group_state.participants.values()])
            if participant.speaking_turns < avg_turns * 0.5:
                urgency *= 1.3
        
        return min(1.0, urgency)
    
    def select_next_speaker(self, group_state: GroupDiscussionState) -> str:
        """
        Determine who speaks next using game theory
        
        Returns: participant_id of next speaker
        """
        urgency_scores = {}
        
        for pid, participant in group_state.participants.items():
            urgency = self.calculate_speaking_urgency(participant, group_state)
            urgency_scores[pid] = urgency
        
        # Add randomness (80% game theory, 20% random)
        randomized_scores = {
            pid: score * 0.8 + np.random.random() * 0.2
            for pid, score in urgency_scores.items()
        }
        
        next_speaker = max(randomized_scores.items(), key=lambda x: x[1])[0]
        
        return next_speaker