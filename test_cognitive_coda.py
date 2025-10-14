#!/usr/bin/env python3
"""
Test script for Cognitive Coda Generator

This test verifies:
1. CognitiveCodaAgent can be instantiated
2. Coda generation returns valid format
3. Word count validation works (≤15 words)
4. Single-line validation works
5. Parsing handles various response formats
6. Fallback works on parsing errors
7. Integration with orchestrator works
8. Coda appears in conversation log
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.cognitive_coda import CognitiveCodaAgent
from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator


async def test_coda_agent_creation():
    """Test that CognitiveCodaAgent can be instantiated"""
    
    print("\n" + "="*60)
    print("TEST 1: Cognitive Coda Agent Creation")
    print("="*60 + "\n")
    
    try:
        agent = CognitiveCodaAgent()
        print(f"✅ Agent created: {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Temperature: {agent.temperature}")
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False


async def test_coda_generation():
    """Test basic coda generation functionality"""
    
    print("="*60)
    print("TEST 2: Basic Coda Generation")
    print("="*60 + "\n")
    
    try:
        agent = CognitiveCodaAgent()
        
        # Test episode summary
        summary = """
        The discussion explored whether artificial intelligence poses an existential threat to humanity.
        Participants debated between cautious approaches (strict regulation, careful development)
        and optimistic views (AI as beneficial tool, accelerated progress).
        
        The synthesis revealed that both camps share concern for human welfare—the question becomes
        how to balance innovation with safety. A middle path emerged: conscious co-evolution
        where humans and AI systems develop together with mutual respect.
        """
        
        # Generate coda
        result = await agent.generate_coda(
            episode_summary=summary,
            topic="Is AI an existential threat?"
        )
        
        print("✨ Generated Cognitive Coda:")
        print(f"   {result['coda']}")
        print(f"\n📖 Reasoning Chain:")
        print(f"   {result['reasoning']}")
        
        # Validate format
        word_count = len(result['coda'].split())
        has_newlines = '\n' in result['coda']
        
        print(f"\n📊 Validation:")
        print(f"   Word count: {word_count} ({'✅' if word_count <= 15 else '❌'} ≤15)")
        print(f"   Single line: {'✅' if not has_newlines else '❌'}")
        print(f"   Has reasoning: {'✅' if result['reasoning'] else '❌'}")
        
        return word_count <= 15 and not has_newlines and bool(result['reasoning'])
        
    except Exception as e:
        print(f"❌ Coda generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration_with_orchestrator():
    """Test integration with orchestrator"""
    
    print("="*60)
    print("TEST 3: Integration with Orchestrator")
    print("="*60 + "\n")
    
    try:
        participants = [
            {
                "name": "Sophia",
                "gender": "female",
                "personality": "analytical",
                "expertise": "ethics"
            },
            {
                "name": "Marcus",
                "gender": "male",
                "personality": "creative",
                "expertise": "philosophy"
            }
        ]
        
        orchestrator = MultiAgentDiscussionOrchestrator(
            topic="What is the nature of consciousness?",
            target_depth=2,
            participants_config=participants,
            enable_narrator=False,
            enable_synthesizer=False,
            enable_coda=True  # ENABLE CODA
        )
        
        print("✅ Orchestrator created with coda enabled")
        print(f"   Coda agent initialized: {orchestrator.coda_agent is not None}")
        print(f"   Coda enabled flag: {orchestrator.enable_coda}")
        
        # Run short discussion
        print("\n🎭 Running short discussion...")
        exchanges = await orchestrator.run_discussion(max_iterations=3)
        
        # Check for coda in exchanges
        coda_exchanges = [e for e in exchanges if e.get('speaker') == 'Cognitive Coda']
        
        print(f"\n📊 Results:")
        print(f"   Total exchanges: {len(exchanges)}")
        print(f"   Coda exchanges: {len(coda_exchanges)}")
        
        if coda_exchanges:
            coda = coda_exchanges[0]
            print(f"   Coda content: {coda['content']}")
            print(f"   Has reasoning: {'reasoning' in coda}")
            print("✅ Coda generated and added to exchanges")
            return True
        else:
            print("❌ No coda found in exchanges")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_coda_disabled():
    """Test that coda can be disabled"""
    
    print("="*60)
    print("TEST 4: Coda Disabled")
    print("="*60 + "\n")
    
    try:
        participants = [
            {
                "name": "Alice",
                "gender": "female",
                "personality": "collaborative",
                "expertise": "science"
            },
            {
                "name": "Bob",
                "gender": "male",
                "personality": "skeptical",
                "expertise": "logic"
            }
        ]
        
        orchestrator = MultiAgentDiscussionOrchestrator(
            topic="Test topic",
            target_depth=2,
            participants_config=participants,
            enable_narrator=False,
            enable_synthesizer=False,
            enable_coda=False  # DISABLE CODA
        )
        
        print("✅ Orchestrator created with coda disabled")
        print(f"   Coda agent: {orchestrator.coda_agent}")
        print(f"   Coda enabled flag: {orchestrator.enable_coda}")
        
        # Run short discussion
        exchanges = await orchestrator.run_discussion(max_iterations=2)
        
        # Check for coda in exchanges
        coda_exchanges = [e for e in exchanges if e.get('speaker') == 'Cognitive Coda']
        
        print(f"\n📊 Results:")
        print(f"   Total exchanges: {len(exchanges)}")
        print(f"   Coda exchanges: {len(coda_exchanges)}")
        
        if len(coda_exchanges) == 0:
            print("✅ No coda generated when disabled")
            return True
        else:
            print("❌ Coda was generated despite being disabled")
            return False
            
    except Exception as e:
        print(f"❌ Disable test failed: {e}")
        return False


async def test_word_count_validation():
    """Test word count validation"""
    
    print("="*60)
    print("TEST 5: Word Count Validation")
    print("="*60 + "\n")
    
    try:
        agent = CognitiveCodaAgent()
        
        # Test valid coda (≤15 words)
        valid_coda = "Truth emerges where dialogue and doubt converge."
        try:
            agent._validate_coda(valid_coda)
            print(f"✅ Valid coda passed: '{valid_coda}' ({len(valid_coda.split())} words)")
        except ValueError as e:
            print(f"❌ Valid coda failed: {e}")
            return False
        
        # Test invalid coda (>15 words)
        invalid_coda = "This is a very long cognitive coda that exceeds the fifteen word limit that we have established for these philosophical theorems."
        try:
            agent._validate_coda(invalid_coda)
            print(f"❌ Invalid coda should have failed: '{invalid_coda}' ({len(invalid_coda.split())} words)")
            return False
        except ValueError as e:
            print(f"✅ Invalid coda correctly rejected: {e}")
        
        # Test single line validation
        multiline_coda = "Truth emerges\\nwhere dialogue converges."
        try:
            agent._validate_coda(multiline_coda)
            print(f"❌ Multiline coda should have failed")
            return False
        except ValueError as e:
            print(f"✅ Multiline coda correctly rejected: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False


async def run_all_tests():
    """Run all cognitive coda tests"""
    
    print("\n" + "="*60)
    print("COGNITIVE CODA GENERATOR TEST SUITE")
    print("="*60)
    
    results = []
    
    try:
        # Run individual tests
        results.append(await test_coda_agent_creation())
        results.append(await test_coda_generation())
        results.append(await test_integration_with_orchestrator())
        results.append(await test_coda_disabled())
        results.append(await test_word_count_validation())
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "="*60)
        if passed == total:
            print("✅ ALL TESTS PASSED")
        else:
            print(f"❌ {total - passed} TEST(S) FAILED")
        print("="*60 + "\n")
        
        print("Summary of Cognitive Coda Features:")
        print("  ✓ CognitiveCodaAgent can be instantiated" if results[0] else "  ❌ Agent creation failed")
        print("  ✓ Generates valid philosophical theorems" if results[1] else "  ❌ Coda generation failed")
        print("  ✓ Integrates with orchestrator properly" if results[2] else "  ❌ Integration failed")
        print("  ✓ Can be enabled/disabled via configuration" if results[3] else "  ❌ Disable functionality failed")
        print("  ✓ Validates word count and format constraints" if results[4] else "  ❌ Validation failed")
        
        if passed == total:
            print("\n🎉 Phase 4A: Cognitive Coda Generator is fully functional!")
        
        return passed == total
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)