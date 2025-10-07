import pytest
from src.agents.participant_agent import ParticipantAgent
from src.states.participant_state import Gender, PersonalityArchetype
from src.states.group_state import GroupDiscussionState
from src.game_theory import DialogueMove


@pytest.mark.asyncio
async def test_agent_state_update():
    """Agent should update state after speaking"""
    
    agent = ParticipantAgent(
        participant_id="test",
        name="Test",
        gender=Gender.FEMALE,
        personality=PersonalityArchetype.COLLABORATIVE,
        expertise="test",
        session_id="test_session"
    )
    
    initial_turns = agent.state.speaking_turns
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=3
    )
    
    move = DialogueMove(move_type="DEEPEN")
    
    await agent._update_state("test response", move, group_state)
    
    assert agent.state.speaking_turns == initial_turns + 1


@pytest.mark.asyncio
async def test_agent_relationship_update():
    """Agent should update relationships based on moves"""
    
    agent = ParticipantAgent(
        participant_id="agent1",
        name="Agent1",
        gender=Gender.MALE,
        personality=PersonalityArchetype.SKEPTICAL,
        expertise="test",
        session_id="test_session"
    )
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=3
    )
    
    # Support move should increase relationship
    move = DialogueMove(move_type="SUPPORT", target="agent2")
    await agent._update_state("I agree", move, group_state)
    
    assert agent.state.relationships.get("agent2", 0) > 0
    

def test_agent_prompt_building():
    """Test that prompts are built correctly"""
    
    agent = ParticipantAgent(
        participant_id="test",
        name="Test Agent",
        gender=Gender.NON_BINARY,
        personality=PersonalityArchetype.ANALYTICAL,
        expertise="logic",
        session_id="test_session"
    )
    
    group_state = GroupDiscussionState(
        topic="What is truth?",
        target_depth=3
    )
    
    move = DialogueMove(move_type="DEEPEN")
    
    prompt = agent._build_prompt(topic="What is truth?", group_state=group_state, move=move)
    
    assert "Test Agent" in prompt
    assert "analytical" in prompt
    assert "logic" in prompt
    assert "they/them" in prompt
    assert "What is truth?" in prompt