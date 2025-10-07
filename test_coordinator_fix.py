#!/usr/bin/env python3
"""Test that coordinator addresses the correct next speaker"""

import asyncio
import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator
from src.config import TalksConfig


async def test_coordinator_fix():
    """Test that narrator addresses the person who actually speaks next"""
    
    print("Testing Coordinator-Speaker Consistency")
    print("=" * 50)
    
    # Reload config to ensure coordinator is enabled
    config = TalksConfig()
    config.reload()
    
    # Simple 3-person discussion
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
        },
        {
            "name": "Charlie",
            "gender": "male",
            "personality": "skeptical",
            "expertise": "science"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="Free will and determinism",
        target_depth=2,
        participants_config=participants,
        enable_narrator=True,
        narrator_name="Michael Lee"
    )
    
    print(f"Configuration:")
    print(f"- Coordinator mode: {config.coordinator_mode}")
    print(f"- Coordinator frequency: {config.coordinator_frequency}")
    print(f"- Participants: {', '.join([p['name'] for p in participants])}")
    
    # Run a short discussion
    print("\nRunning 6-turn discussion...")
    print("-" * 50)
    exchanges = await orchestrator.run_discussion(max_iterations=6)
    
    print("\n" + "=" * 50)
    print(f"Completed {len(exchanges)} turns")
    
    # Analyze the log for consistency
    if orchestrator._log_filepath.exists():
        with open(orchestrator._log_filepath, 'r') as f:
            content = f.read()
        
        # Extract discussion section
        if "## Discussion" in content:
            discussion = content.split("## Discussion")[1]
            if "## Closing" in discussion:
                discussion = discussion.split("## Closing")[0]
            
            # Find all Michael Lee interjections and following speakers
            michael_pattern = r'<Michael Lee>(.*?)</Michael Lee>'
            speaker_pattern = r'<(Alice|Bob|Charlie)>'
            
            michael_interjections = re.findall(michael_pattern, discussion, re.DOTALL)
            
            print("\nVerifying coordinator addresses correct speaker:")
            print("-" * 50)
            
            errors = []
            for interjection in michael_interjections:
                # Look for who Michael addresses in his interjection
                addressed_names = []
                for name in ["Alice", "Bob", "Charlie"]:
                    if name in interjection:
                        addressed_names.append(name)
                
                # Find the next speaker after this interjection in the full discussion
                interjection_pos = discussion.find(interjection)
                after_interjection = discussion[interjection_pos + len(interjection):]
                next_speaker_match = re.search(speaker_pattern, after_interjection)
                
                if next_speaker_match and addressed_names:
                    next_speaker = next_speaker_match.group(1)
                    # The last mentioned name is usually who's being addressed
                    addressed = addressed_names[-1] if addressed_names else None
                    
                    snippet = interjection[:100].replace('\n', ' ')
                    if addressed == next_speaker:
                        print(f"✓ Michael addresses {addressed}, {next_speaker} speaks next")
                        print(f"  Snippet: \"{snippet}...\"")
                    else:
                        print(f"✗ MISMATCH: Michael addresses {addressed}, but {next_speaker} speaks!")
                        print(f"  Snippet: \"{snippet}...\"")
                        errors.append((addressed, next_speaker))
            
            print("\n" + "=" * 50)
            if errors:
                print(f"❌ Found {len(errors)} mismatches!")
                print("The coordinator fix may not be working correctly.")
            else:
                print("✅ All coordinator interjections correctly address the next speaker!")
                print("The fix is working as intended.")
    
    print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(test_coordinator_fix())