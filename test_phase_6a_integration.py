#!/usr/bin/env python3
"""
Phase 6A Integration Tests - CT Cleanup & Agency Recalibration

This test suite validates the complete Phase 6A implementation including:
1. CT Cleanup post-processing
2. Decision Rule Injection 
3. Enhanced Agency Extraction with windowing
4. Enhanced Coda display with sub-scores
5. End-to-end pipeline integration
"""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.ct_cleanup import ConsequenceTestCleanup
from src.analysis.decision_rule_injector import DecisionRuleInjector
from src.analysis.signal_extractors import SignalExtractor
from src.agents.cognitive_coda import CognitiveCodaAgent


def test_ct_cleanup_integration():
    """Test CT cleanup with realistic dialogue content"""
    print("Testing CT Cleanup integration...")
    
    # Sample transcript with verbose CT blocks
    test_transcript = """
**Simone:** We should suspend judgment until more evidence arrives. The question of whether consciousness can be fully explained by physical processes remains deeply uncertain.

Consequence Test: This uncertainty about consciousness raises fundamental questions about the nature of mind and its relationship to matter. If we suspend judgment on consciousness until we have complete neurological understanding, we might wait indefinitely, as the hard problem of consciousness may be inherently resistant to empirical resolution. The implications extend to questions of free will, moral responsibility, and the very foundations of ethics. Some argue that we must act on provisional understanding while remaining epistemically humble about our limitations.

**Aristotle:** Sometimes we must act despite uncertainty, drawing on practical wisdom.

**Descartes:** But sometimes we must choose to act under ambiguity, committing to provisional maxims.

Consequence Test: The tension between action and uncertainty reveals a deeper philosophical problem about the relationship between knowledge and ethics. If doubt doesn't suspend action, we see examples like Pascal's wager where agents still choose under ambiguity, making commitments that transcend purely empirical justification. This suggests that practical reason operates according to different criteria than theoretical reason, and that authentic existence might require embracing uncertainty rather than demanding proof.

**Hypatia:** Mathematical reasoning might provide a framework here.
"""
    
    # Test CT cleanup
    processor = ConsequenceTestCleanup()
    cleaned_transcript = processor.replace_ct_blocks(test_transcript)
    
    # Verify cleanup
    ct_lines = [line for line in cleaned_transcript.split('\n') if line.startswith('Consequence Test:')]
    
    print(f"  Original CT blocks: {test_transcript.count('Consequence Test:')}")
    print(f"  Cleaned CT lines: {len(ct_lines)}")
    
    # Verify all CT blocks are one-liners
    for line in ct_lines:
        assert len(line) < 300, f"CT line too long: {len(line)} chars"
    
    # Verify templates match expected patterns
    for line in ct_lines:
        is_ct_true = processor.CT_TRUE in line
        is_ct_false = processor.CT_FALSE in line
        assert is_ct_true or is_ct_false, f"CT line doesn't match template: {line}"
    
    # Verify speaker tags preserved
    assert "**Simone:**" in cleaned_transcript
    assert "**Aristotle:**" in cleaned_transcript
    assert "**Descartes:**" in cleaned_transcript
    assert "**Hypatia:**" in cleaned_transcript
    
    print("  ✅ CT cleanup integration test passed")
    return cleaned_transcript


def test_decision_rule_injection():
    """Test decision rule injection with agent coverage"""
    print("Testing Decision Rule injection...")
    
    # Test turns without decision language
    test_turns = [
        {'speaker': 'simone', 'content': 'Consciousness remains a mystery.'},
        {'speaker': 'aristotle', 'content': 'Indeed, it puzzles many philosophers.'},
        {'speaker': 'descartes', 'content': 'The mind-body problem is complex.'},
        {'speaker': 'hypatia', 'content': 'Mathematics might illuminate this.'},
        {'speaker': 'lao', 'content': 'Perhaps simplicity is the answer.'},
        {'speaker': 'simone', 'content': 'These questions are difficult.'},
        {'speaker': 'aristotle', 'content': 'Practical wisdom is needed.'},
        {'speaker': 'descartes', 'content': 'Clear thinking is essential.'}
    ]
    
    # Test injection
    injector = DecisionRuleInjector(window_size=8)
    
    # Check which agents need rules
    agents_needing_rules = injector.check_agent_coverage(test_turns)
    print(f"  Agents needing rules: {agents_needing_rules}")
    
    # Test injection for each agent
    enhanced_turns = []
    for turn in test_turns:
        content = turn['content']
        speaker = turn['speaker']
        
        if injector.needs_decision_rule(speaker, test_turns):
            enhanced_content = injector.inject_rule(speaker, content)
            enhanced_turns.append({'speaker': speaker, 'content': enhanced_content})
            print(f"  Injected rule for {speaker}")
        else:
            enhanced_turns.append(turn)
    
    # Verify rules were injected
    rule_count = sum(1 for turn in enhanced_turns if '<!-- decision_rule -->' in turn['content'])
    assert rule_count > 0, "No decision rules were injected"
    
    # Verify agent-specific rule content
    for turn in enhanced_turns:
        if '<!-- decision_rule -->' in turn['content']:
            speaker = turn['speaker']
            content = turn['content']
            
            # Check for agent-specific language
            if speaker == 'simone':
                assert any(word in content for word in ['ambiguity', 'authentic', 'absurd']), \
                    f"Simone rule doesn't match voice: {content}"
            elif speaker == 'aristotle':
                assert any(word in content for word in ['courage', 'virtue', 'wisdom']), \
                    f"Aristotle rule doesn't match voice: {content}"
    
    print("  ✅ Decision rule injection test passed")
    return enhanced_turns


def test_enhanced_agency_extraction():
    """Test enhanced agency extraction with real dialogue patterns"""
    print("Testing Enhanced Agency extraction...")
    
    # Create exchanges with mixed agency patterns
    test_exchanges = [
        {'content': 'We should act with courage despite uncertainty.'},  # A_ought + A_decis
        {'content': 'I choose not to proceed with this approach.'},  # A_decis (negated)
        {'content': 'Therefore, this implies we must take responsibility.'},  # A_conseq + A_ought
        {'content': 'We never should abandon our principles.'},  # A_ought (negated)
        {'content': 'I will commit to this path authentically.'},  # A_decis + A_ought
        {'content': 'Therefore we should act under ambiguity. <!-- decision_rule -->'},  # Tagged decision
        {'content': 'I maintain this stance firmly.'},  # A_stance
        {'content': 'This leads to consequences, so we ought to proceed.'},  # A_conseq + A_ought
    ]
    
    # Test enhanced extraction
    extractor = SignalExtractor()
    result = extractor.compute_agency_score(test_exchanges, window_size=8)
    
    print(f"  Enhanced Agency Results:")
    print(f"    Overall A: {result['A']:.3f}")
    print(f"    A_ought: {result['A_ought']:.3f}")
    print(f"    A_decis: {result['A_decis']:.3f}")
    print(f"    A_conseq: {result['A_conseq']:.3f}")
    print(f"    A_stance: {result['A_stance']:.3f}")
    
    # Verify results
    assert result['A'] >= 0.45, f"Agency too low: {result['A']:.3f}"
    assert all(0 <= result[k] <= 1 for k in ['A_ought', 'A_decis', 'A_conseq', 'A_stance'])
    assert result['A_decis'] > 0.5, f"Decision rule tag not detected: {result['A_decis']:.3f}"
    
    # Test negation damping worked
    assert result['A_ought'] > result['A_decis'], "Negation damping may not be working properly"
    
    print("  ✅ Enhanced agency extraction test passed")
    return result


async def test_enhanced_coda_integration():
    """Test enhanced coda with mathematical model integration"""
    print("Testing Enhanced Coda integration...")
    
    # Create agency-rich exchanges
    test_exchanges = [
        {'content': 'We should act ethically despite uncertainty.'},
        {'content': 'I choose to proceed with commitment.'},
        {'content': 'Therefore, this implies we must take responsibility.'},
        {'content': 'I stand by these principles firmly.'},
        {'content': 'We ought to embrace authentic action.'},
        {'content': 'Therefore we should choose meaning. <!-- decision_rule -->'},
        {'content': 'This leads to practical consequences.'},
        {'content': 'I will maintain this ethical stance.'}
    ]
    
    episode_summary = """
    The discussion explored the relationship between ethical action and epistemic uncertainty.
    Participants grappled with whether to suspend judgment or act despite incomplete knowledge.
    Key themes: authenticity, practical wisdom, moral responsibility, decision-making under ambiguity.
    """
    
    # Test enhanced coda generation
    coda_agent = CognitiveCodaAgent(
        name="Integration Test Coda",
        enable_mathematical_model=True
    )
    
    result = await coda_agent.generate_coda(
        episode_summary=episode_summary,
        topic="Ethics and Uncertainty",
        exchanges=test_exchanges,
        window_size=8
    )
    
    print(f"  Generated Coda: {result['coda']}")
    
    # Verify mathematical model integration
    assert 'mathematical_model' in result, "Mathematical model not generated"
    
    math_model = result['mathematical_model']
    components = math_model.get('components', {})
    
    # Verify agency sub-components present
    agency_keys = ['A_ought', 'A_decis', 'A_conseq', 'A_stance']
    for key in agency_keys:
        assert key in components, f"Missing agency component: {key}"
        assert 0 <= components[key] <= 1, f"Component {key} out of range: {components[key]}"
    
    # Verify agency in target range
    A = math_model['signals']['A']
    assert A >= 0.45, f"Agency too low in coda: {A:.3f}"
    
    # Test formatted output
    formatted = await coda_agent.process(
        episode_summary=episode_summary,
        topic="Ethics and Uncertainty",
        exchanges=test_exchanges
    )
    
    # Verify sub-scores displayed
    for key in agency_keys:
        assert f"{key}:" in formatted, f"Sub-score {key} not displayed"
    
    # Verify status/next action present
    assert ('**Next:**' in formatted or '**Status:**' in formatted), "Missing action recommendation"
    
    print(f"  Agency: {A:.3f} (target ≥0.45)")
    print("  ✅ Enhanced coda integration test passed")
    return result


async def test_end_to_end_pipeline():
    """Test complete Phase 6A pipeline end-to-end"""
    print("Testing End-to-End Phase 6A pipeline...")
    
    # 1. Start with raw transcript containing verbose CTs
    raw_transcript = """
**Simone:** We should act authentically even under uncertainty.

Consequence Test: This raises questions about the nature of authentic action when we lack complete knowledge. If authenticity requires acting according to our deepest values even when uncertain about outcomes, then we must develop frameworks for decision-making that don't depend on certainty. This connects to existentialist themes about choosing meaning in an absurd universe where complete knowledge is impossible.

**Aristotle:** Practical wisdom guides us when theoretical knowledge fails.

**Descartes:** I will proceed with methodical doubt but practical maxims.

Consequence Test: The tension between doubt and action reveals different modes of reasoning. If doubt doesn't suspend all action, we see that practical reason operates according to different criteria than theoretical reason. Examples include Pascal's wager and other cases where agents choose under ambiguity, suggesting that commitment transcends purely empirical justification.

**Hypatia:** Mathematical consistency provides a framework for ethical reasoning.
"""
    
    # 2. Apply CT cleanup
    ct_processor = ConsequenceTestCleanup()
    cleaned_transcript = ct_processor.replace_ct_blocks(raw_transcript)
    
    print(f"  Step 1 - CT Cleanup: {raw_transcript.count('Consequence Test:')} -> {len([l for l in cleaned_transcript.split('\\n') if l.startswith('Consequence Test:')])}")
    
    # 3. Extract turns for decision rule injection
    # Simulate dialogue turns
    turns = [
        {'speaker': 'simone', 'content': 'We should act authentically even under uncertainty.'},
        {'speaker': 'aristotle', 'content': 'Practical wisdom guides us when theoretical knowledge fails.'},
        {'speaker': 'descartes', 'content': 'I will proceed with methodical doubt but practical maxims.'},
        {'speaker': 'hypatia', 'content': 'Mathematical consistency provides a framework for ethical reasoning.'}
    ]
    
    # 4. Apply decision rule injection
    injector = DecisionRuleInjector()
    enhanced_turns = []
    for turn in turns:
        content = turn['content']
        if injector.needs_decision_rule(turn['speaker'], turns):
            content = injector.inject_rule(turn['speaker'], content)
        enhanced_turns.append({'speaker': turn['speaker'], 'content': content})
    
    rules_injected = sum(1 for t in enhanced_turns if '<!-- decision_rule -->' in t['content'])
    print(f"  Step 2 - Decision Rules: {rules_injected} rules injected")
    
    # 5. Enhanced agency extraction
    extractor = SignalExtractor()
    agency_result = extractor.compute_agency_score(enhanced_turns, window_size=8)
    
    print(f"  Step 3 - Agency Extraction: A={agency_result['A']:.3f}")
    
    # 6. Enhanced coda generation
    episode_summary = "Discussion on ethical action under uncertainty, exploring authenticity, practical wisdom, and decision-making frameworks."
    
    coda_agent = CognitiveCodaAgent(enable_mathematical_model=True)
    coda_result = await coda_agent.generate_coda(
        episode_summary=episode_summary,
        topic="Ethics Under Uncertainty",
        exchanges=enhanced_turns
    )
    
    print(f"  Step 4 - Enhanced Coda: Generated with sub-scores")
    
    # 7. Verify end-to-end results
    assert agency_result['A'] >= 0.45, f"End-to-end agency too low: {agency_result['A']:.3f}"
    assert 'mathematical_model' in coda_result, "Mathematical model missing from coda"
    assert rules_injected > 0, "No decision rules injected in pipeline"
    
    # Verify CT blocks are cleaned
    ct_lines = [l for l in cleaned_transcript.split('\n') if l.startswith('Consequence Test:')]
    assert all(len(line) < 300 for line in ct_lines), "CT blocks not properly cleaned"
    
    print(f"  ✅ End-to-end pipeline test passed")
    print(f"    - CT blocks: cleaned to one-liners")
    print(f"    - Decision rules: {rules_injected} injected")
    print(f"    - Agency: {agency_result['A']:.3f} (≥0.45)")
    print(f"    - Coda: enhanced with sub-scores")
    
    return {
        'cleaned_transcript': cleaned_transcript,
        'enhanced_turns': enhanced_turns,
        'agency_result': agency_result,
        'coda_result': coda_result
    }


async def run_phase_6a_tests():
    """Run all Phase 6A integration tests"""
    print("🧪 Starting Phase 6A Integration Test Suite")
    print("=" * 60)
    
    try:
        # Test individual components
        test_ct_cleanup_integration()
        test_decision_rule_injection()
        test_enhanced_agency_extraction()
        await test_enhanced_coda_integration()
        
        # Test complete pipeline
        await test_end_to_end_pipeline()
        
        print("\n" + "=" * 60)
        print("🎉 ALL PHASE 6A INTEGRATION TESTS PASSED!")
        print("✅ CT Cleanup: Verbose blocks → one-line templates")
        print("✅ Decision Rules: Agent-specific injection working")
        print("✅ Agency Extraction: Enhanced with windowing & sub-signals")
        print("✅ Coda Display: Mathematical model with sub-scores")
        print("✅ End-to-End: Complete pipeline integration")
        print("\n🚀 Phase 6A implementation ready for production!")
        return True
        
    except Exception as e:
        print(f"\n❌ Phase 6A integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_phase_6a_tests())
    sys.exit(0 if success else 1)