#!/usr/bin/env python3
"""Test redundancy control and information yield"""

import asyncio
import logging
from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_redundancy_control():
    """Test that redundancy control works as designed"""
    
    print("🧪 Testing Redundancy Control Implementation")
    print("=" * 60)
    
    participants = [
        {"name": "Alice", "gender": "female", "personality": "analytical", "expertise": "logic"},
        {"name": "Bob", "gender": "male", "personality": "creative", "expertise": "ethics"}
    ]
    
    # Test with redundancy control enabled
    print("\n1. Testing with redundancy control ENABLED")
    print("-" * 40)
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="The nature of truth",
        target_depth=3,
        participants_config=participants,
        enable_narrator=True,
        enable_synthesizer=True,
        synthesis_frequency=12,  # Test fixed frequency
        enable_redundancy_control=True,
        max_dyad_volleys=2,
        similarity_threshold=0.85
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=24)
    
    # Verify constraints
    print(f"\n📊 Results with redundancy control:")
    print(f"  Total turns: {len(exchanges)}")
    print(f"  Dyad states: {len(orchestrator.group_state.dyads)}")
    
    # Check entailments
    entailment_counts = sum(
        len(e.get('entailments', [])) for e in exchanges
    )
    print(f"  Total entailments detected: {entailment_counts}")
    
    # Check dyad violations
    dyad_violations = 0
    for dyad in orchestrator.group_state.dyads.values():
        if dyad.volleys_used > dyad.max_volleys:
            dyad_violations += 1
    print(f"  Dyad violations: {dyad_violations}")
    
    # Check synthesis frequency
    synthesis_count = sum(1 for e in exchanges if e.get('move') == 'synthesis')
    expected_syntheses = len(exchanges) // 12
    print(f"  Syntheses generated: {synthesis_count} (expected: {expected_syntheses})")
    
    # Test information density
    if exchanges:
        total_words = sum(len(e['content'].split()) for e in exchanges)
        unique_entailments = set()
        for e in exchanges:
            for ent in e.get('entailments', []):
                unique_entailments.add(ent)
        
        density = len(unique_entailments) / total_words if total_words > 0 else 0
        print(f"  Information density: {density:.4f} (unique entailments per word)")
    
    print("\n✅ Redundancy control test completed")
    
    # Test comparison without redundancy control
    print("\n2. Testing with redundancy control DISABLED (comparison)")
    print("-" * 40)
    
    orchestrator_no_control = MultiAgentDiscussionOrchestrator(
        topic="The nature of truth",
        target_depth=3,
        participants_config=participants,
        enable_narrator=True,
        enable_synthesizer=True,
        synthesis_frequency=12,
        enable_redundancy_control=False  # Disabled for comparison
    )
    
    exchanges_no_control = await orchestrator_no_control.run_discussion(max_iterations=24)
    
    print(f"\n📊 Results without redundancy control:")
    print(f"  Total turns: {len(exchanges_no_control)}")
    print(f"  Entailments tracking: {'Not available' if not hasattr(orchestrator_no_control, 'entailment_detector') else 'Available'}")
    
    # Print comparison
    print("\n📈 Comparison Summary:")
    print(f"  Turns with control: {len(exchanges)} vs without: {len(exchanges_no_control)}")
    print(f"  Entailments with control: {entailment_counts} vs without: N/A")
    
    return {
        'with_control': len(exchanges),
        'without_control': len(exchanges_no_control),
        'entailments': entailment_counts,
        'dyad_violations': dyad_violations,
        'synthesis_count': synthesis_count
    }


async def test_entailment_detector():
    """Test entailment detection patterns"""
    print("\n3. Testing Entailment Detector")
    print("-" * 40)
    
    from src.utils.entailment_detector import EntailmentDetector
    
    detector = EntailmentDetector()
    
    test_cases = [
        ("If consciousness is computational, then AI could be conscious.", ["implication"]),
        ("We could test this by observing behavioral patterns.", ["test"]),
        ("In practice, this would mean reconsidering robot rights.", ["application"]),
        ("Unless, of course, consciousness requires biological substrates.", ["counterexample"]),
        ("This is just my opinion without any reasoning.", []),  # Should have no entailments
    ]
    
    for text, expected_types in test_cases:
        detected = detector.detect(text)
        detected_types = [e.value for e in detected]
        
        print(f"  Text: '{text[:50]}...'")
        print(f"    Expected: {expected_types}")
        print(f"    Detected: {detected_types}")
        print(f"    ✅ {'PASS' if set(detected_types) == set(expected_types) else 'FAIL'}")
        print()


async def test_redundancy_checker():
    """Test redundancy checking"""
    print("\n4. Testing Redundancy Checker")
    print("-" * 40)
    
    from src.utils.redundancy_checker import RedundancyChecker
    
    checker = RedundancyChecker(similarity_threshold=0.85)
    
    # Test similar texts
    text1 = "Consciousness is a fundamental aspect of reality."
    text2 = "Consciousness represents a basic element of existence."
    text3 = "Mathematics is the language of the universe."
    
    print(f"  Comparing similar texts:")
    print(f"    Text 1: '{text1}'")
    print(f"    Text 2: '{text2}'")
    
    similarity = checker.get_max_similarity(text2, [text1])
    is_redundant = checker.is_redundant(text2, [text1])
    
    print(f"    Similarity: {similarity:.3f}")
    print(f"    Is redundant: {is_redundant}")
    
    print(f"\n  Comparing different texts:")
    print(f"    Text 1: '{text1}'")
    print(f"    Text 3: '{text3}'")
    
    similarity2 = checker.get_max_similarity(text3, [text1])
    is_redundant2 = checker.is_redundant(text3, [text1])
    
    print(f"    Similarity: {similarity2:.3f}")
    print(f"    Is redundant: {is_redundant2}")


async def main():
    """Run all tests"""
    print("🚀 Starting Redundancy Control Test Suite")
    print("=" * 60)
    
    try:
        # Run main test
        results = await test_redundancy_control()
        
        # Run component tests
        await test_entailment_detector()
        await test_redundancy_checker()
        
        print("\n🎉 All tests completed successfully!")
        print(f"Final results: {results}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())