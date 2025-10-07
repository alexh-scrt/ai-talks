#!/usr/bin/env python3
"""
Simple test to verify the Talks system is working
"""

import asyncio
from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator


async def test_simple_discussion():
    """Test a simple 2-person discussion"""
    
    participants = [
        {
            "name": "Alice",
            "gender": "female",
            "personality": "analytical",
            "expertise": "philosophy"
        },
        {
            "name": "Bob",
            "gender": "male",
            "personality": "creative",
            "expertise": "science"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="What is consciousness?",
        target_depth=2,
        participants_config=participants
    )
    
    print("Starting test discussion...")
    print(f"Topic: What is consciousness?")
    print(f"Participants: Alice (analytical philosopher) and Bob (creative scientist)")
    print("-" * 60)
    
    # Run a short discussion
    exchanges = await orchestrator.run_discussion(max_iterations=5)
    
    print(f"\nDiscussion complete!")
    print(f"Total exchanges: {len(exchanges)}")
    print(f"Aspects explored: {len(orchestrator.group_state.aspects_explored)}")
    
    # Print the exchanges
    for exchange in exchanges:
        print(f"\n{exchange['speaker']} ({exchange['move']}): {exchange['content']}")
    
    return True


if __name__ == "__main__":
    print("Testing Talks system...")
    success = asyncio.run(test_simple_discussion())
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")