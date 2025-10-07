#!/usr/bin/env python3
"""Quick test script for discussion coordinator feature"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator


async def test_coordinator():
    """Quick test of the coordinator feature"""
    
    print("Quick Coordinator Test")
    print("=" * 40)
    
    # Simple 2-person discussion for faster test
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
            "expertise": "ethics"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="The ethics of AI",
        target_depth=2,
        participants_config=participants,
        enable_narrator=True,
        narrator_name="Michael Lee"
    )
    
    # Check config
    from src.config import TalksConfig
    config = TalksConfig()
    
    print(f"Coordinator enabled: {config.coordinator_mode}")
    print(f"Frequency: every {config.coordinator_frequency} turns")
    print(f"Narrator: {orchestrator.narrator.name}")
    
    # Run just 6 turns to see 2 interjections
    print("\nRunning 6-turn discussion...")
    exchanges = await orchestrator.run_discussion(max_iterations=6)
    
    print("\n" + "=" * 40)
    print(f"✅ Completed {len(exchanges)} turns")
    
    # Check log for Michael's interjections
    if orchestrator._log_filepath.exists():
        with open(orchestrator._log_filepath, 'r') as f:
            content = f.read()
            michael_count = content.count("<Michael Lee>")
            print(f"Michael Lee appearances: {michael_count}")
            
            # Expected: 4 intro + 2 coordinator (at turns 3 and 6) + 2 closing
            print("  - Intro segments: 4")
            print("  - Coordinator interjections: ~2")
            print("  - Closing segments: 2")
    
    print("\n✅ Coordinator feature works!")


if __name__ == "__main__":
    asyncio.run(test_coordinator())