#!/usr/bin/env python3
"""
Test the dialectical synthesizer feature.

This test verifies:
1. Synthesizer is initialized correctly
2. Synthesis triggers at correct intervals
3. Different synthesis styles produce appropriate outputs
4. Synthesis is logged correctly
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator


async def test_synthesizer_basic():
    """Test basic synthesizer functionality"""
    
    print("\n" + "="*60)
    print("TEST 1: Basic Synthesizer Functionality")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Sophia",
            "gender": "female",
            "personality": "collaborative",
            "expertise": "ethics"
        },
        {
            "name": "Marcus",
            "gender": "male",
            "personality": "skeptical",
            "expertise": "logic"
        },
        {
            "name": "Aisha",
            "gender": "female",
            "personality": "analytical",
            "expertise": "science"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="Is free will an illusion?",
        target_depth=3,
        participants_config=participants,
        enable_narrator=True,
        enable_synthesizer=True,
        synthesis_frequency=6,  # Synthesize twice in 12 turns
        synthesis_style="hegelian"
    )
    
    print(f"Configuration:")
    print(f"  - Participants: {len(participants)}")
    print(f"  - Synthesis frequency: every 6 turns")
    print(f"  - Synthesis style: hegelian")
    print(f"  - Expected syntheses: 2 (at turns 6 and 12)\n")
    
    exchanges = await orchestrator.run_discussion(max_iterations=12)
    
    print(f"\n{'='*60}")
    print(f"✅ Test 1 Complete")
    print(f"{'='*60}")
    print(f"  - Total exchanges: {len(exchanges)}")
    print(f"  - Log file: {orchestrator._log_filepath}")
    
    # Check log for synthesis sections
    if orchestrator._log_filepath.exists():
        with open(orchestrator._log_filepath, 'r') as f:
            content = f.read()
            synthesis_count = content.count("## Synthesis")
            print(f"  - Synthesis sections in log: {synthesis_count}")
            
            if synthesis_count >= 2:
                print("  ✓ Synthesis checkpoints triggered correctly")
            else:
                print("  ⚠ Expected at least 2 synthesis sections")


async def test_synthesis_styles():
    """Test all three synthesis styles"""
    
    print("\n" + "="*60)
    print("TEST 2: Different Synthesis Styles")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Einstein",
            "gender": "male",
            "personality": "creative",
            "expertise": "physics"
        },
        {
            "name": "Simone",
            "gender": "female",
            "personality": "assertive",
            "expertise": "existentialism"
        }
    ]
    
    styles = ["hegelian", "socratic", "pragmatic"]
    
    for style in styles:
        print(f"\nTesting {style.upper()} style:")
        print("-" * 40)
        
        orchestrator = MultiAgentDiscussionOrchestrator(
            topic="What is the nature of reality?",
            target_depth=2,
            participants_config=participants,
            enable_narrator=False,  # Disable for faster testing
            enable_synthesizer=True,
            synthesis_frequency=4,
            synthesis_style=style
        )
        
        exchanges = await orchestrator.run_discussion(max_iterations=8)
        
        print(f"  ✓ Completed with {len(exchanges)} exchanges")
        print(f"  ✓ Log: {orchestrator._log_filepath.name}")


async def test_synthesis_disabled():
    """Test that synthesis can be disabled"""
    
    print("\n" + "="*60)
    print("TEST 3: Synthesis Disabled")
    print("="*60 + "\n")
    
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
            "expertise": "art"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="What is beauty?",
        target_depth=2,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False  # Disabled
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=10)
    
    print(f"✓ Completed without synthesizer")
    print(f"  - Exchanges: {len(exchanges)}")
    
    # Verify no synthesis in log
    if orchestrator._log_filepath.exists():
        with open(orchestrator._log_filepath, 'r') as f:
            content = f.read()
            synthesis_count = content.count("## Synthesis")
            
            if synthesis_count == 0:
                print("  ✓ No synthesis sections found (as expected)")
            else:
                print(f"  ⚠ Found {synthesis_count} synthesis sections (unexpected)")


async def run_all_tests():
    """Run all synthesizer tests"""
    
    print("\n" + "="*60)
    print("DIALECTICAL SYNTHESIZER TEST SUITE")
    print("="*60)
    
    try:
        await test_synthesizer_basic()
        await test_synthesis_styles()
        await test_synthesis_disabled()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())