#!/usr/bin/env python3
"""Test coordinator interjecting at every turn (frequency: 0)"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator
from src.config import TalksConfig


async def test_every_turn():
    """Test coordinator with frequency 0 (every turn)"""
    
    print("Testing Coordinator Every Turn (frequency: 0)")
    print("=" * 50)
    
    # Verify config
    config = TalksConfig()
    config.reload()  # Reload to get latest talks.yml
    print(f"Current coordinator_frequency: {config.coordinator_frequency}")
    
    if config.coordinator_frequency != 0:
        print("⚠️  WARNING: coordinator_frequency is not 0 in talks.yml")
        print("   Please set it to 0 to test every-turn interjections")
        return
    
    # Simple 2-person discussion
    participants = [
        {
            "name": "Alice",
            "gender": "female", 
            "personality": "analytical",
            "expertise": "logic"
        },
        {
            "name": "Bob",
            "gender": "male",
            "personality": "creative",
            "expertise": "ethics"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="Free will",
        target_depth=2,
        participants_config=participants,
        enable_narrator=True,
        narrator_name="Michael Lee"
    )
    
    print(f"Narrator: {orchestrator.narrator.name}")
    print(f"Coordinator mode: {config.coordinator_mode}")
    print(f"Expected: Michael should interject after EVERY turn\n")
    
    # Run just 4 turns
    print("Running 4-turn discussion...")
    print("-" * 50)
    exchanges = await orchestrator.run_discussion(max_iterations=4)
    
    print("\n" + "=" * 50)
    print(f"Completed {len(exchanges)} turns\n")
    
    # Count Michael's appearances
    if orchestrator._log_filepath.exists():
        with open(orchestrator._log_filepath, 'r') as f:
            content = f.read()
            
            # Count Michael Lee blocks
            michael_count = content.count("<Michael Lee>")
            
            # Split into sections
            intro_count = content.split("## Discussion")[0].count("<Michael Lee>")
            discussion_section = content.split("## Discussion")[1] if "## Discussion" in content else ""
            discussion_count = discussion_section.split("## Closing")[0].count("<Michael Lee>") if discussion_section else 0
            closing_count = content.split("## Closing")[1].count("<Michael Lee>") if "## Closing" in content else 0
            
            print(f"Michael Lee appearances: {michael_count}")
            print(f"  - In Introduction: {intro_count} (expected: 4)")
            print(f"  - In Discussion: {discussion_count} (expected: {len(exchanges)-1} coordinator interjections)")  
            print(f"  - In Closing: {closing_count} (expected: 2)")
            
            # With frequency 0, Michael should interject after each turn except the first
            expected_interjections = len(exchanges) - 1
            if discussion_count >= expected_interjections:
                print(f"\n✅ SUCCESS: Coordinator interjected {discussion_count} times (expected at least {expected_interjections})")
            else:
                print(f"\n❌ FAIL: Only {discussion_count} interjections, expected at least {expected_interjections}")
    
    print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(test_every_turn())