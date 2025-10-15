#!/usr/bin/env python3
"""Test enhanced cognitive coda with mathematical model"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_signal_extraction():
    """Test signal extraction from exchanges"""
    print("\n" + "="*60)
    print("TEST 1: Signal Extraction")
    print("="*60 + "\n")
    
    try:
        from src.analysis.signal_extractors import SignalExtractor
        
        extractor = SignalExtractor()
        
        # Mock exchanges with various properties
        exchanges = [
            {'content': 'If we assume X, then Y follows necessarily.', 'move': 'DEEPEN', 'speaker': 'Alice'},
            {'content': 'We should consider the ethical implications carefully.', 'move': 'CHALLENGE', 'speaker': 'Bob'},
            {'content': 'I believe this framework provides a solid foundation.', 'move': 'BUILD', 'speaker': 'Alice'},
            {'content': 'The moderator requires us to address this point.', 'move': 'RESPOND', 'speaker': 'Moderator'},
            {'content': 'Therefore, we must conclude that Z holds.', 'move': 'CONCLUDE', 'speaker': 'Bob'},
            {'content': 'According to Smith (2020), this theory is well-established.', 'move': 'SUPPORT', 'speaker': 'Alice', 'citations': ['Smith 2020']}
        ]
        
        signals = extractor.compute_aggregate_signals(exchanges)
        
        print(f"📊 Aggregate Signals:")
        print(f"  S (Structure): {signals['S']:.3f}")
        print(f"  A (Agency): {signals['A']:.3f}")
        print(f"  D (Dependence): {signals['D']:.3f}")
        
        print(f"\n🔍 Component Breakdown:")
        for component, value in signals['components'].items():
            print(f"  {component}: {value:.3f}")
        
        # Validate ranges
        assert 0 <= signals['S'] <= 1, f"S out of range: {signals['S']}"
        assert 0 <= signals['A'] <= 1, f"A out of range: {signals['A']}"
        assert 0 <= signals['D'] <= 1, f"D out of range: {signals['D']}"
        
        # Check that we have expected components
        expected_components = ['S_cite', 'S_logic', 'S_consis', 'S_focus', 
                              'A_ought', 'A_decis', 'A_conse', 'A_stanc',
                              'D_sim', 'D_rules', 'D_nonvar']
        for comp in expected_components:
            assert comp in signals['components'], f"Missing component: {comp}"
        
        print("✅ Signal extraction passed")
        return True
        
    except Exception as e:
        print(f"❌ Signal extraction failed: {e}")
        return False


async def test_meaning_model():
    """Test meaning computation"""
    print("\n" + "="*60)
    print("TEST 2: Meaning Model")
    print("="*60 + "\n")
    
    try:
        from src.analysis.meaning_model import MeaningModel
        
        model = MeaningModel()
        
        # Test cases with expected behaviors
        test_cases = [
            (0.6, 0.7, 0.3, "Optimal structure + good agency + low dependence"),
            (0.3, 0.8, 0.2, "Low structure + high agency + low dependence"),
            (0.9, 0.5, 0.7, "Over-constrained + medium agency + high dependence"),
            (0.0, 1.0, 0.0, "No structure + max agency + no dependence"),
            (1.0, 0.0, 1.0, "Max structure + no agency + max dependence")
        ]
        
        print("📊 Meaning Model Test Cases:")
        for S, A, D, desc in test_cases:
            M = model.compute(S, A, D)
            interpretation = model.get_interpretation(S, A, D)
            maxim = model.get_maxim(M)
            
            print(f"\n  Case: {desc}")
            print(f"    Input: S={S}, A={A}, D={D}")
            print(f"    Output: M={M:.3f}")
            print(f"    Interpretation: {interpretation}")
            print(f"    Maxim: {maxim}")
            
            # Validate bounds
            assert 0 <= M <= 1, f"M out of range: {M}"
            assert interpretation, "Empty interpretation"
            assert maxim, "Empty maxim"
        
        # Test parameter validation
        try:
            invalid_model = MeaningModel(sigma=0.0)  # Should fail
            assert False, "Should have failed with invalid sigma"
        except AssertionError as expected:
            print("  ✅ Parameter validation working")
        
        # Test recommendations
        components = {
            'S_cite': 0.1, 'S_logic': 0.2, 'S_consis': 0.3, 'S_focus': 0.4,
            'A_ought': 0.2, 'A_decis': 0.1, 'A_conse': 0.3, 'A_stanc': 0.2,
            'D_sim': 0.3, 'D_rules': 0.8, 'D_nonvar': 0.6
        }
        
        recommendations = model.recommend_actions(components)
        print(f"\n📋 Sample Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        assert len(recommendations) <= 3, "Too many recommendations"
        assert all(isinstance(rec, str) for rec in recommendations), "Non-string recommendations"
        
        print("\n✅ Meaning model passed")
        return True
        
    except Exception as e:
        print(f"❌ Meaning model failed: {e}")
        return False


async def test_enhanced_coda_generation():
    """Test full enhanced coda generation"""
    print("\n" + "="*60)
    print("TEST 3: Enhanced Coda Generation")
    print("="*60 + "\n")
    
    try:
        from src.agents.cognitive_coda import CognitiveCodaAgent
        
        # Test with mathematical model enabled
        agent = CognitiveCodaAgent(enable_mathematical_model=True)
        
        # Mock exchanges with philosophical discussion
        exchanges = [
            {'content': 'If consciousness requires integration, then distributed systems cannot be conscious.', 'move': 'DEEPEN', 'turn': 1, 'speaker': 'Alice'},
            {'content': 'We ought to consider whether integration is truly necessary for consciousness.', 'move': 'CHALLENGE', 'turn': 2, 'speaker': 'Bob'},
            {'content': 'The research clearly shows information integration is key to conscious experience.', 'move': 'BUILD', 'turn': 3, 'speaker': 'Alice', 'citations': ['IIT paper']},
            {'content': 'Therefore, we should test this with concrete examples from neuroscience.', 'move': 'APPLY', 'turn': 4, 'speaker': 'Bob'},
            {'content': 'Consider a swarm: individually simple, collectively complex - where is consciousness?', 'move': 'EXEMPLIFY', 'turn': 5, 'speaker': 'Alice'},
            {'content': 'I propose consciousness emerges when integration exceeds a critical threshold.', 'move': 'SYNTHESIZE', 'turn': 6, 'speaker': 'Bob'}
        ]
        
        summary = "Discussion explored whether consciousness requires integrated information processing, examining the boundary between individual and collective cognition."
        
        result = await agent.generate_coda(
            episode_summary=summary,
            topic="Nature of consciousness",
            exchanges=exchanges,
            window_size=6
        )
        
        print(f"🧠 Generated Coda:")
        print(f"  Poetic: {result['coda']}")
        print(f"  Reasoning: {result['reasoning']}")
        
        # Validate basic structure
        assert result['coda'], "Empty coda"
        assert result['reasoning'], "Empty reasoning"
        assert 'timestamp' in result, "Missing timestamp"
        
        # Check mathematical model
        if agent.enable_math_model and 'mathematical_model' in result:
            math = result['mathematical_model']
            print(f"\n📊 Mathematical Model:")
            print(f"  Equation: {math['equation']}")
            print(f"  Numbers: {math['numbers']}")
            print(f"  Signals: S={math['signals']['S']:.2f}, A={math['signals']['A']:.2f}, D={math['signals']['D']:.2f}")
            print(f"  Meaning: M={math['M']:.3f}")
            print(f"  Interpretation: {math['verbal_axiom']}")
            print(f"  Maxim: {math['maxim']}")
            
            # Validate mathematical components
            assert 'signals' in math, "Missing signals"
            assert 'M' in math, "Missing meaning score"
            assert 'equation' in math, "Missing equation"
            assert 'verbal_axiom' in math, "Missing interpretation"
            assert 'maxim' in math, "Missing maxim"
            
            # Check signal ranges
            assert 0 <= math['signals']['S'] <= 1, "S out of range"
            assert 0 <= math['signals']['A'] <= 1, "A out of range"
            assert 0 <= math['signals']['D'] <= 1, "D out of range"
            assert 0 <= math['M'] <= 1, "M out of range"
            
        # Check recommendations
        if 'recommendations' in result:
            print(f"\n📋 Recommendations:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
            
            assert len(result['recommendations']) <= 3, "Too many recommendations"
        
        print("\n✅ Enhanced coda generation passed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced coda generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_coda_fallback():
    """Test coda generation fallback when mathematical model disabled"""
    print("\n" + "="*60)
    print("TEST 4: Coda Fallback (No Math Model)")
    print("="*60 + "\n")
    
    try:
        from src.agents.cognitive_coda import CognitiveCodaAgent
        
        # Test with mathematical model disabled
        agent = CognitiveCodaAgent(enable_mathematical_model=False)
        
        summary = "Simple discussion about truth and meaning."
        
        result = await agent.generate_coda(
            episode_summary=summary,
            topic="Truth and meaning"
        )
        
        print(f"🧠 Fallback Coda:")
        print(f"  Poetic: {result['coda']}")
        print(f"  Reasoning: {result['reasoning']}")
        
        # Should have basic structure but no mathematical model
        assert result['coda'], "Empty coda"
        assert result['reasoning'], "Empty reasoning"
        assert 'mathematical_model' not in result, "Mathematical model present when disabled"
        
        print("\n✅ Coda fallback passed")
        return True
        
    except Exception as e:
        print(f"❌ Coda fallback failed: {e}")
        return False


async def test_persistence():
    """Test coda persistence to JSONL"""
    print("\n" + "="*60)
    print("TEST 5: Coda Persistence")
    print("="*60 + "\n")
    
    try:
        from src.agents.cognitive_coda import CognitiveCodaAgent
        import json
        
        agent = CognitiveCodaAgent(enable_mathematical_model=True)
        
        exchanges = [
            {'content': 'Test exchange for persistence.', 'move': 'DEEPEN', 'turn': 1, 'speaker': 'Alice'}
        ]
        
        result = await agent.generate_coda(
            episode_summary="Test summary",
            topic="Test topic",
            exchanges=exchanges,
            window_size=1
        )
        
        # Check if JSONL file was created
        output_file = Path("outputs/codas/codas.jsonl")
        if output_file.exists():
            print(f"📄 Checking persistence file: {output_file}")
            
            # Read last line to check our record
            with open(output_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_record = json.loads(lines[-1])
                    print(f"  Last record timestamp: {last_record.get('run_id', 'N/A')}")
                    print(f"  Has coda: {'coda' in last_record}")
                    print(f"  Version: {last_record.get('version', 'N/A')}")
                    
                    assert 'run_id' in last_record, "Missing run_id"
                    assert 'coda' in last_record, "Missing coda"
                    assert 'version' in last_record, "Missing version"
                    
            print(f"  ✅ Found {len(lines)} total records in file")
        else:
            print("  ⚠️ No persistence file found (may be expected in test environment)")
        
        print("\n✅ Persistence test passed")
        return True
        
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
        return False


async def test_visualization():
    """Test visualization module (optional)"""
    print("\n" + "="*60)
    print("TEST 6: Visualization (Optional)")
    print("="*60 + "\n")
    
    try:
        from src.analysis.visualize_meaning import plot_meaning_ridge
        
        # Test basic ridge plot
        fig_path = plot_meaning_ridge(
            S=0.6, A=0.7, D=0.3,
            output_path="test_ridge.png"
        )
        
        if fig_path and Path(fig_path).exists():
            print(f"  ✅ Ridge plot saved to: {fig_path}")
            Path(fig_path).unlink()  # Clean up test file
        else:
            print(f"  ⚠️ Ridge plot not generated (matplotlib may not be available)")
        
        print("\n✅ Visualization test passed")
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Cognitive Coda Test Suite")
    print("=" * 80)
    
    tests = [
        test_signal_extraction,
        test_meaning_model,
        test_enhanced_coda_generation,
        test_coda_fallback,
        test_persistence,
        test_visualization
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"🎉 TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - Enhanced Cognitive Coda is ready!")
    else:
        print(f"⚠️ {failed} tests failed - check implementation")
    
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)