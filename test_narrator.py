#!/usr/bin/env python3
"""Test script for narrator functionality"""

import asyncio
from src.agents.narrator_agent import NarratorAgent
from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype

async def test_narrator():
    """Test the narrator agent"""
    
    # Create narrator
    narrator = NarratorAgent(name="Michael Lee", web_search=False)
    
    # Create sample participants
    participants = [
        ParticipantState(
            participant_id="sophia",
            name="Sophia",
            gender=Gender.FEMALE,
            personality=PersonalityArchetype.COLLABORATIVE,
            expertise_area="ethics"
        ),
        ParticipantState(
            participant_id="marcus",
            name="Marcus",
            gender=Gender.MALE,
            personality=PersonalityArchetype.SKEPTICAL,
            expertise_area="logic"
        )
    ]
    
    topic = "What is the nature of consciousness?"
    
    print("Testing Narrator Agent\n" + "="*50 + "\n")
    
    # Test individual methods
    print("1. Welcome Introduction:")
    welcome = await narrator.introduce_show()
    print(welcome)
    print("\n" + "-"*50 + "\n")
    
    print("2. Topic Introduction:")
    topic_intro = await narrator.introduce_topic(topic)
    print(topic_intro)
    print("\n" + "-"*50 + "\n")
    
    print("3. Participant Introductions:")
    participant_intro = await narrator.introduce_participants(participants)
    print(participant_intro)
    print("\n" + "-"*50 + "\n")
    
    print("4. Transition to Discussion:")
    transition = await narrator.prompt_discussion_start(topic, "Sophia")
    print(transition)
    print("\n" + "="*50 + "\n")
    
    print("Full Introduction Sequence:")
    print("-"*50)
    full_intro = await narrator.generate_full_introduction(
        topic=topic,
        participants=participants,
        first_speaker="Sophia"
    )
    
    for segment in full_intro:
        print(f"\n[{segment['type'].upper()}] {segment['speaker']}:")
        print(segment['content'])
    
    print("\n" + "="*50)
    print("✅ Narrator test complete!")

if __name__ == "__main__":
    asyncio.run(test_narrator())