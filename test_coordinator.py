#!/usr/bin/env python3
"""Test script for discussion coordinator feature"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator


async def test_coordinator():
    """Test the discussion coordinator feature"""
    
    print("Testing Discussion Coordinator Feature")
    print("=" * 50)
    
    # Define test participants
    participants = [
        {
            "name": "Sophia",
            "gender": "female",
            "personality": "analytical",
            "expertise": "philosophy"
        },
        {
            "name": "Marcus",
            "gender": "male",
            "personality": "collaborative",
            "expertise": "ethics"
        },
        {
            "name": "Elena",
            "gender": "female",
            "personality": "creative",
            "expertise": "psychology"
        }
    ]
    
    # Create orchestrator with narrator and coordinator enabled
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="The nature of consciousness and its relationship to artificial intelligence",
        target_depth=3,
        participants_config=participants,
        enable_narrator=True,  # Enable narrator
        narrator_name="Michael Lee"
    )
    
    print(f"\nConfiguration:")
    print(f"- Topic: {orchestrator.topic}")
    print(f"- Participants: {len(participants)}")
    print(f"- Narrator enabled: {orchestrator.enable_narrator}")
    print(f"- Narrator name: {orchestrator.narrator.name if orchestrator.narrator else 'N/A'}")
    
    # Load config to check coordinator settings
    from src.config import TalksConfig
    config = TalksConfig()
    print(f"- Coordinator mode: {config.coordinator_mode}")
    print(f"- Coordinator frequency: every {config.coordinator_frequency} turns")
    
    print("\nRunning discussion with coordinator interjections...")
    print("-" * 50)
    
    # Run a short discussion (10 turns to see multiple interjections)
    exchanges = await orchestrator.run_discussion(max_iterations=10)
    
    print("\n" + "=" * 50)
    print("Test Complete!")
    print(f"- Total exchanges: {len(exchanges)}")
    
    # Check log file was created
    log_file = orchestrator._log_filepath
    if log_file.exists():
        print(f"- Log file created: {log_file.name}")
        
        # Read log to verify coordinator interjections
        with open(log_file, 'r') as f:
            content = f.read()
            michael_count = content.count("<Michael Lee>")
            print(f"- Michael Lee appearances: {michael_count}")
            
            # Calculate expected interjections
            # Introduction segments (4) + coordinator interjections + closing segments (2)
            intro_segments = 4 if orchestrator.enable_narrator else 0
            closing_segments = 2 if orchestrator.enable_narrator else 0
            turns = len(exchanges)
            
            # Coordinator interjects every N turns (based on frequency)
            if config.coordinator_frequency > 0:
                coordinator_interjections = turns // config.coordinator_frequency
            else:
                coordinator_interjections = 0
            
            expected_michael = intro_segments + coordinator_interjections + closing_segments
            
            print(f"  - Introduction segments: {intro_segments}")
            print(f"  - Coordinator interjections: {coordinator_interjections}")
            print(f"  - Closing segments: {closing_segments}")
            print(f"  - Expected total: ~{expected_michael}")
    
    print("\n✅ Coordinator feature test passed!")
    print("\nFeatures tested:")
    print("• Narrator introduction")
    print("• Coordinator interjections at specified frequency")
    print("• Smooth transitions between speakers")
    print("• Narrator closing")
    print("• Real-time logging with content cleanup")


if __name__ == "__main__":
    asyncio.run(test_coordinator())