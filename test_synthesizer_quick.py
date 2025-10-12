#!/usr/bin/env python3
"""
Quick test to verify synthesizer is properly integrated
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import DialecticalSynthesizerAgent
from src.config import TalksConfig


async def test_synthesizer_import():
    """Test that synthesizer can be imported and initialized"""
    
    print("\n" + "="*60)
    print("QUICK SYNTHESIZER VERIFICATION")
    print("="*60 + "\n")
    
    # Test 1: Import works
    try:
        synthesizer = DialecticalSynthesizerAgent(
            name="Test Synthesizer",
            synthesis_style="hegelian"
        )
        print("✅ DialecticalSynthesizerAgent imported and initialized")
    except Exception as e:
        print(f"❌ Failed to initialize synthesizer: {e}")
        return False
    
    # Test 2: Config loads correctly
    try:
        config = TalksConfig()
        enabled = config.get('synthesizer.enabled', True)
        style = config.get('synthesizer.style', 'hegelian')
        freq = config.get('synthesizer.frequency', 8)
        print(f"✅ Synthesizer config loaded: enabled={enabled}, style={style}, freq={freq}")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    # Test 3: Test synthesize_segment with minimal data
    try:
        test_exchanges = [
            {
                "turn": 0,
                "speaker": "Alice",
                "speaker_id": "alice",
                "content": "Free will is an illusion created by deterministic processes.",
                "move": "DEEPEN",
                "target": None,
                "personality": "analytical"
            },
            {
                "turn": 1,
                "speaker": "Bob",
                "speaker_id": "bob", 
                "content": "But quantum mechanics introduces fundamental randomness that breaks determinism.",
                "move": "CHALLENGE",
                "target": "alice",
                "personality": "creative"
            },
            {
                "turn": 2,
                "speaker": "Alice",
                "speaker_id": "alice",
                "content": "Random events don't grant free will - they just replace determinism with chaos.",
                "move": "CHALLENGE",
                "target": "bob",
                "personality": "analytical"
            }
        ]
        
        result = await synthesizer.synthesize_segment(
            exchanges=test_exchanges,
            turn_window=3,
            topic="Is free will an illusion?"
        )
        
        if result:
            print(f"✅ Synthesizer generated output: {result[:100]}...")
        else:
            print("⚠️ Synthesizer returned None (might need more exchanges)")
            
    except Exception as e:
        print(f"❌ Synthesis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✅ ALL QUICK TESTS PASSED")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_synthesizer_import())
    sys.exit(0 if success else 1)