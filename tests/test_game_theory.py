import pytest
from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype
from src.states.group_state import GroupDiscussionState
from src.game_theory.turn_selector import TurnSelector
from src.game_theory.payoff_calculator import PayoffCalculator


def test_speaking_urgency_addressed():
    """Participant who was addressed should have high urgency"""
    
    participant = ParticipantState(
        participant_id="test",
        name="Test",
        gender=Gender.FEMALE,
        personality=PersonalityArchetype.COLLABORATIVE,
        expertise_area="test",
        was_addressed=True
    )
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=3,
        participants={"test": participant}
    )
    
    selector = TurnSelector()
    urgency = selector.calculate_speaking_urgency(participant, group_state)
    
    assert urgency > 0.4  # Should be high due to was_addressed


def test_move_payoff_deepen():
    """DEEPEN payoff should be high when depth gap exists"""
    
    participant = ParticipantState(
        participant_id="test",
        name="Test",
        gender=Gender.MALE,
        personality=PersonalityArchetype.ANALYTICAL,
        expertise_area="test",
        depth_explored=1,
        curiosity_level=0.9
    )
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=5,
        participants={"test": participant}
    )
    
    calculator = PayoffCalculator()
    payoffs = calculator.calculate_move_payoffs(participant, group_state)
    
    assert payoffs["DEEPEN"] > 0.5  # Should be high


def test_turn_selection_fairness():
    """Turn selection should eventually balance across participants"""
    
    participants = {
        "p1": ParticipantState(
            participant_id="p1",
            name="P1",
            gender=Gender.FEMALE,
            personality=PersonalityArchetype.ASSERTIVE,
            expertise_area="test",
            speaking_turns=10  # Has spoken a lot
        ),
        "p2": ParticipantState(
            participant_id="p2",
            name="P2",
            gender=Gender.MALE,
            personality=PersonalityArchetype.CAUTIOUS,
            expertise_area="test",
            speaking_turns=1  # Hasn't spoken much
        )
    }
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=3,
        participants=participants,
        dominant_speaker="p1"
    )
    
    selector = TurnSelector()
    
    # Run multiple selections
    selections = []
    for _ in range(100):
        selections.append(selector.select_next_speaker(group_state))
    
    # P2 should be selected more often
    p2_count = selections.count("p2")
    assert p2_count > 40  # At least 40% of the time