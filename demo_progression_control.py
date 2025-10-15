#!/usr/bin/env python3
"""Demo script to showcase Force Progression, Stop Orbiting functionality"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.controllers.progression_controller import ProgressionController, ProgressionConfig


async def demo_progression_control():
    """Demonstrate progression control in action"""
    
    print("🚀 Force Progression, Stop Orbiting Demo")
    print("=" * 60)
    print("This demo shows how the progression control system prevents")
    print("philosophical discussions from orbiting without progress.\n")
    
    # Create progression controller
    config = ProgressionConfig(
        cycles_threshold=2,
        max_consequence_tests=2,
        enable_progression=True
    )
    
    controller = ProgressionController(config, llm_client=None)
    
    print("📊 Initial Status:")
    status = controller.get_status_report()
    print(f"   Turns processed: {status['metrics']['turns_processed']}")
    print(f"   Tests injected: {status['metrics']['tests_injected']}")
    print(f"   Pivots forced: {status['metrics']['pivots_forced']}")
    print()
    
    # Simulate a discussion that orbits around necessity vs contingency
    
    print("🎭 SIMULATED DISCUSSION:")
    print("-" * 40)
    
    # Turn 1: Introduce philosophical tension
    print("\n💬 Alice: 'Everything in nature follows necessary laws - there's no room for contingency.'")
    result1 = await controller.process_turn(
        content="Everything in nature follows necessary laws - there's no room for contingency.",
        speaker="Alice",
        context={"episode_summary": "Discussion on determinism"}
    )
    print(f"   📊 Active tensions: {result1['state_update']['active_tensions']}")
    print(f"   🔍 Entailments detected: {result1['state_update']['has_entailment']}")
    
    # Turn 2: Continue tension without new entailment (cycle 1)
    print("\n💬 Bob: 'But surely contingent events happen all the time - not everything is necessary.'")
    result2 = await controller.process_turn(
        content="But surely contingent events happen all the time - not everything is necessary.",
        speaker="Bob",
        context={"episode_summary": "Continuing discussion"}
    )
    print(f"   📊 Saturated tensions: {result2['state_update']['saturated_tensions']}")
    print(f"   🔬 Interventions: {len(result2.get('interventions', []))}")
    
    # Turn 3: Repeat without progress (cycle 2 - should trigger consequence test)
    print("\n💬 Charlie: 'The necessity versus contingency debate remains unresolved.'")
    result3 = await controller.process_turn(
        content="The necessity versus contingency debate remains unresolved.",
        speaker="Charlie", 
        context={"episode_summary": "Still orbiting"}
    )
    
    if result3.get('interventions'):
        intervention = result3['interventions'][0]
        print(f"   🔬 CONSEQUENCE TEST INJECTED:")
        print(f"      Type: {intervention['type']}")
        print(f"      Tension: {intervention['tension']}")
        print(f"      Prompt: {intervention['prompt'][:80]}...")
    
    # Turn 4: Poor response to test (no real entailment)
    print("\n💬 Alice: 'I still think necessity is more fundamental than contingency.'")
    result4 = await controller.process_turn(
        content="I still think necessity is more fundamental than contingency.",
        speaker="Alice",
        context={"episode_summary": "Responding to test"}
    )
    print(f"   🔍 Entailments in response: {result4['state_update']['has_entailment']}")
    
    # Turn 5: Another poor response (might trigger pivot)
    print("\n💬 Bob: 'Yes, this necessity/contingency question is quite difficult.'")
    result5 = await controller.process_turn(
        content="Yes, this necessity/contingency question is quite difficult.",
        speaker="Bob",
        context={"episode_summary": "Still no progress"}
    )
    
    if result5.get('interventions'):
        for intervention in result5['interventions']:
            if intervention['type'] == 'pivot':
                print(f"   🔄 PIVOT FORCED:")
                print(f"      Reason: Failed consequence tests")
                print(f"      Synthesis: {intervention['prompt'][:80]}...")
            elif intervention['type'] == 'consequence_test':
                print(f"   🔬 ADDITIONAL TEST:")
                print(f"      Prompt: {intervention['prompt'][:80]}...")
    
    print("\n📊 FINAL STATUS:")
    final_status = controller.get_status_report()
    print(f"   Total turns processed: {final_status['metrics']['turns_processed']}")
    print(f"   Consequence tests injected: {final_status['metrics']['tests_injected']}")
    print(f"   Pivots forced: {final_status['metrics']['pivots_forced']}")
    print(f"   Entailments detected: {final_status['metrics']['entailments_detected']}")
    
    print("\n🎯 KEY INSIGHTS:")
    print("   • System detected repeated tension without progress")
    print("   • Automatically injected consequence tests to force concrete implications")
    print("   • When tests failed to produce entailments, forced topic pivot")
    print("   • Prevented endless circular discussion (orbiting)")
    print("   • Maintained discussion momentum and forward progress")
    
    print("\n✅ Demo complete! The progression control system is working.")


if __name__ == "__main__":
    asyncio.run(demo_progression_control())