#!/usr/bin/env python3
"""Test suite for enhanced Agency signal extraction"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.signal_extractors import SignalExtractor


def test_enhanced_agency_extraction():
    """Test enhanced agency extraction with windowing and sub-signals"""
    print("Testing enhanced agency extraction...")
    
    # Create test exchanges with rich agency patterns
    test_exchanges = [
        {'content': 'We should act with courage and take responsibility.'},  # A_ought + A_decis
        {'content': 'I choose to proceed despite doubt and commit to this path.'},  # A_decis + A_stance  
        {'content': 'Therefore, this implies that we must act ethically.'},  # A_conseq + A_ought
        {'content': 'We must take responsibility and stand by our principles.'},  # A_ought + A_stance
        {'content': 'I decide to commit and proceed with authenticity.'},  # A_decis + A_ought
        {'content': 'Therefore we should act under ambiguity and choose meaning. <!-- decision_rule -->'},  # Tagged + multiple
        {'content': 'I will maintain this stance and hold to my commitment.'},  # A_decis + A_stance
        {'content': 'This leads to consequences, therefore we ought to proceed.'},  # A_conseq + A_ought
    ]
    
    # Test enhanced agency computation
    extractor = SignalExtractor()
    result = extractor.compute_agency_score(test_exchanges, window_size=8)
    
    print(f"Enhanced Agency Results:")
    print(f"  Overall A: {result['A']:.3f}")
    print(f"  A_ought: {result['A_ought']:.3f}")
    print(f"  A_decis: {result['A_decis']:.3f}")
    print(f"  A_conseq: {result['A_conseq']:.3f}")
    print(f"  A_stance: {result['A_stance']:.3f}")
    
    # Validate results
    assert result['A'] >= 0.45, f"Agency score too low: {result['A']:.3f}"
    assert 0 <= result['A'] <= 1, "Agency score out of bounds"
    assert all(0 <= result[k] <= 1 for k in ['A_ought', 'A_decis', 'A_conseq', 'A_stance']), "Sub-scores out of bounds"
    
    # Test that decision rule tag is detected
    assert result['A_decis'] > 0.5, f"Decision rule tag not detected properly: {result['A_decis']:.3f}"
    
    print("✅ Enhanced agency extraction tests passed")
    return result


def test_negation_damping():
    """Test negation damping functionality"""
    print("\nTesting negation damping...")
    
    # Test exchanges with negated statements
    negated_exchanges = [
        {'content': 'We should not act hastily.'},  # Negated ought
        {'content': 'I will never choose that path.'},  # Negated decis
        {'content': 'This does not lead to consequences.'},  # Negated conseq
    ]
    
    positive_exchanges = [
        {'content': 'We should act with wisdom.'},  # Positive ought
        {'content': 'I will choose this path.'},  # Positive decis
        {'content': 'This leads to important consequences.'},  # Positive conseq
    ]
    
    extractor = SignalExtractor()
    
    negated_result = extractor.compute_agency_score(negated_exchanges, window_size=8)
    positive_result = extractor.compute_agency_score(positive_exchanges, window_size=8)
    
    print(f"Negated statements A: {negated_result['A']:.3f}")
    print(f"Positive statements A: {positive_result['A']:.3f}")
    
    # Positive statements should score higher than negated ones
    assert positive_result['A'] > negated_result['A'], "Negation damping not working"
    
    print("✅ Negation damping tests passed")
    return negated_result, positive_result


def test_windowing():
    """Test windowing functionality"""
    print("\nTesting windowing...")
    
    # Create 12 exchanges - first 8 with no agency, last 4 with high agency
    old_exchanges = [
        {'content': f'Generic statement {i}.'} for i in range(8)
    ]
    
    recent_exchanges = [
        {'content': 'We should act with courage.'},
        {'content': 'I choose to proceed.'},
        {'content': 'Therefore, this implies action.'},
        {'content': 'I stand by this decision.'}
    ]
    
    all_exchanges = old_exchanges + recent_exchanges
    
    extractor = SignalExtractor()
    
    # Test with full history (should be low due to early generic statements)
    full_result = extractor.compute_agency_score(all_exchanges, window_size=12)
    
    # Test with window of 4 (should be high due to recent agency-rich statements)
    windowed_result = extractor.compute_agency_score(all_exchanges, window_size=4)
    
    print(f"Full history A: {full_result['A']:.3f}")
    print(f"Windowed (4) A: {windowed_result['A']:.3f}")
    
    # Windowed result should be higher
    assert windowed_result['A'] > full_result['A'], "Windowing not working properly"
    
    print("✅ Windowing tests passed")
    return full_result, windowed_result


def test_soft_cap():
    """Test soft cap with diminishing returns"""
    print("\nTesting soft cap...")
    
    # Create exchanges with excessive agency patterns
    excessive_exchanges = [
        {'content': 'We should act. We must proceed. We ought to choose. We should decide.'} for _ in range(5)
    ]
    
    extractor = SignalExtractor()
    result = extractor.compute_agency_score(excessive_exchanges, window_size=8)
    
    print(f"Excessive agency A: {result['A']:.3f}")
    
    # Should be capped below 1.0 due to soft cap
    assert result['A'] < 1.0, "Soft cap not working - score should be < 1.0"
    assert result['A'] > 0.6, "Soft cap too aggressive - score should still be reasonably high"
    
    print("✅ Soft cap tests passed")
    return result


def run_all_tests():
    """Run all enhanced agency tests"""
    print("🧪 Starting Enhanced Agency Signal Extraction Test Suite")
    print("=" * 60)
    
    try:
        test_enhanced_agency_extraction()
        test_negation_damping()
        test_windowing()
        test_soft_cap()
        
        print("\n" + "=" * 60)
        print("🎉 ALL ENHANCED AGENCY TESTS PASSED!")
        print("✅ Agency scoring should now achieve target range 0.45-0.65")
        print("✅ Windowing, negation damping, and soft caps working correctly")
        print("✅ Decision rule tags detected properly")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)