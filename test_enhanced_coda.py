#!/usr/bin/env python3
"""Test enhanced cognitive coda with sub-scores display"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.cognitive_coda import CognitiveCodaAgent


async def test_enhanced_coda_display():
    """Test enhanced coda generation with agency sub-scores"""
    print("Testing enhanced coda display...")
    
    # Create test exchanges with agency patterns
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
    
    # Test episode summary
    episode_summary = """
    In this philosophical dialogue, the participants explored the relationship between ethical action and epistemic uncertainty. The discussion centered on whether we should suspend judgment when evidence is incomplete, or whether we have obligations to act despite uncertainty.

    Simone argued for authentic commitment even under ambiguity, drawing on existentialist themes of choosing meaning in an absurd universe. Aristotle emphasized practical wisdom and the cultivation of virtue as guides for action when theoretical knowledge fails. The conversation revealed a tension between the desire for certainty and the practical necessity of choice.

    Key themes included: the ethics of belief, decision-making under uncertainty, authentic action, and the role of practical wisdom in moral reasoning.
    """
    
    # Initialize enhanced coda agent
    coda_agent = CognitiveCodaAgent(
        name="Enhanced Coda Test",
        model="qwen3:32b",
        temperature=0.7,
        enable_mathematical_model=True
    )
    
    # Generate enhanced coda
    result = await coda_agent.generate_coda(
        episode_summary=episode_summary,
        topic="Ethics and Uncertainty",
        exchanges=test_exchanges,
        window_size=8
    )
    
    print(f"\n{'='*60}")
    print("ENHANCED CODA RESULT")
    print(f"{'='*60}")
    
    print(f"Coda: {result['coda']}")
    print(f"\nReasoning: {result['reasoning']}")
    
    # Test the process method to see the formatted output
    formatted_output = await coda_agent.process(
        episode_summary=episode_summary,
        topic="Ethics and Uncertainty", 
        exchanges=test_exchanges
    )
    
    print(f"\n{'='*60}")
    print("FORMATTED OUTPUT WITH SUB-SCORES")
    print(f"{'='*60}")
    print(formatted_output)
    
    # Verify that sub-scores are included
    if 'mathematical_model' in result:
        math_model = result['mathematical_model']
        components = math_model.get('components', {})
        
        print(f"\n{'='*60}")
        print("VERIFICATION - SUB-SCORES DETECTED")
        print(f"{'='*60}")
        
        print(f"Agency sub-components:")
        for key in ['A_ought', 'A_decis', 'A_conseq', 'A_stance']:
            if key in components:
                print(f"  {key}: {components[key]:.3f}")
        
        # Check that agency is in target range
        A = math_model['signals']['A']
        print(f"\nOverall Agency: {A:.3f}")
        assert A >= 0.45, f"Agency too low: {A:.3f}"
        print("✅ Agency in target range (≥0.45)")
        
        # Check that sub-scores are displayed in output
        assert 'A_ought:' in formatted_output, "A_ought sub-score not displayed"
        assert 'A_decis:' in formatted_output, "A_decis sub-score not displayed"
        assert 'A_conseq:' in formatted_output, "A_conseq sub-score not displayed"
        assert 'A_stance:' in formatted_output, "A_stance sub-score not displayed"
        print("✅ All agency sub-scores displayed in output")
        
        # Check for Next Action or Status message
        has_next_action = ('**Next:**' in formatted_output or '**Status:**' in formatted_output)
        assert has_next_action, "Missing Next Action or Status message"
        print("✅ Next Action/Status message displayed")
        
    else:
        print("❌ Mathematical model not generated")
        return False
    
    print(f"\n🎉 Enhanced coda display test passed!")
    return True


async def main():
    """Run enhanced coda test"""
    try:
        success = await test_enhanced_coda_display()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())