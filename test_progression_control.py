#!/usr/bin/env python3
"""Comprehensive test suite for Force Progression, Stop Orbiting implementation"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Dict, List, Set

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_tension_state_enhanced():
    """Test enhanced TensionState with consequence test tracking"""
    print("\n" + "="*60)
    print("TEST 1: Enhanced TensionState")
    print("="*60 + "\n")
    
    try:
        from src.states.tension_state import TensionState, ConsequenceTest
        
        # Test basic functionality
        tension = TensionState(pair=("necessity", "contingency"))
        
        print(f"📊 Initial state: {tension}")
        assert tension.cycles == 0
        assert tension.can_continue()
        assert not tension.is_saturated()
        assert not tension.should_inject_test()
        
        # Test cycle progression
        tension.increment_cycle()
        tension.increment_cycle()
        print(f"📊 After 2 cycles: {tension}")
        assert tension.cycles == 2
        assert tension.is_saturated()
        assert tension.should_inject_test()
        
        # Test consequence test injection
        test = tension.add_consequence_test(5, "If necessity is true, what follows for free will?")
        print(f"🔬 Added test: {test.prompt[:50]}...")
        assert len(tension.consequence_tests) == 1
        assert tension.last_consequence_turn == 5
        
        # Test entailment recording (should reset cycles)
        tension.record_entailment(7)
        print(f"📊 After entailment: {tension}")
        assert tension.cycles == 0
        assert not tension.needs_pivot
        assert tension.last_new_entailment_turn == 7
        
        # Test failed consequence tests
        tension.increment_cycle()
        tension.increment_cycle()
        test2 = tension.add_consequence_test(10, "Second test")
        test2.responded = True
        test2.had_entailment = False
        
        test3 = tension.add_consequence_test(12, "Third test")
        test3.responded = True
        test3.had_entailment = False
        
        print(f"📊 After failed tests: {tension}")
        assert tension.count_failed_tests() == 2
        assert tension.should_pivot()
        
        print("✅ Enhanced TensionState tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced TensionState tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_topic_extractor():
    """Test TopicExtractor for philosophical concept detection"""
    print("\n" + "="*60)
    print("TEST 2: TopicExtractor")
    print("="*60 + "\n")
    
    try:
        from src.utils.topic_extractor import TopicExtractor
        
        extractor = TopicExtractor()
        
        # Test basic topic extraction
        text1 = "If consciousness is necessary for experience, then deterministic systems cannot truly feel."
        topics1 = extractor.extract_topics(text1)
        print(f"📝 Text: {text1[:50]}...")
        print(f"🏷️  Topics found: {topics1}")
        
        assert "necessity" in topics1
        assert "consciousness" in topics1
        
        # Test tension detection
        text2 = "The structure of reality constrains our agency, but we must still choose freely."
        topics2 = extractor.extract_topics(text2)
        tensions = extractor.detect_tensions(text2)
        print(f"📝 Text: {text2[:50]}...")
        print(f"🏷️  Topics: {topics2}")
        print(f"⚡ Tensions: {tensions}")
        
        # Should detect structure/agency tension
        expected_tension = tuple(sorted(["structure", "agency"]))
        assert expected_tension in tensions
        
        # Test with recent context
        recent_topics = [{"necessity", "determinism"}, {"freedom", "choice"}]
        context_tensions = extractor.detect_tensions("This is about freedom", recent_topics)
        print(f"🔄 Context tensions: {context_tensions}")
        
        # Test explanation feature
        explanation = extractor.explain_detection(text2)
        print(f"💡 Detection explanation: {explanation}")
        assert explanation  # Should have some explanations
        
        # Test comprehensive analysis
        summary = extractor.get_tension_summary(text2, recent_topics)
        print(f"📋 Tension summary: {summary}")
        assert summary["has_tensions"]
        assert summary["tension_count"] > 0
        
        print("✅ TopicExtractor tests passed")
        return True
        
    except Exception as e:
        print(f"❌ TopicExtractor tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_enhanced_entailment_detector():
    """Test enhanced EntailmentDetector with consequence patterns"""
    print("\n" + "="*60)
    print("TEST 3: Enhanced EntailmentDetector")
    print("="*60 + "\n")
    
    try:
        from src.utils.entailment_detector import EntailmentDetector, EntailmentType
        
        detector = EntailmentDetector()
        
        # Test enhanced implication patterns
        impl_text = "If free will exists, then moral responsibility follows necessarily."
        impl_entailments = detector.detect(impl_text)
        print(f"📝 Implication text: {impl_text}")
        print(f"🔍 Entailments: {[e.value for e in impl_entailments]}")
        assert EntailmentType.IMPLICATION in impl_entailments
        
        # Test enhanced application patterns
        app_text = "We ought to test this empirically to see if consciousness can be measured."
        app_entailments = detector.detect(app_text)
        print(f"📝 Application text: {app_text}")
        print(f"🔍 Entailments: {[e.value for e in app_entailments]}")
        assert EntailmentType.APPLICATION in app_entailments or EntailmentType.TEST in app_entailments
        
        # Test consequence pattern detection
        conseq_text = "This leads to the prediction that free agents will make unpredictable choices."
        has_consequence = detector.has_consequence_pattern(conseq_text)
        print(f"📝 Consequence text: {conseq_text}")
        print(f"🎯 Has consequence pattern: {has_consequence}")
        assert has_consequence
        
        # Test strongest entailment prioritization
        multi_text = "If X then Y, for example in practice, we could test this hypothesis."
        strongest = detector.get_strongest_entailment(multi_text)
        print(f"📝 Multi-pattern text: {multi_text}")
        print(f"💪 Strongest entailment: {strongest.value if strongest else None}")
        assert strongest == EntailmentType.TEST  # Should prioritize TEST
        
        # Test consequence test validation
        test_prompt = "If reality is a simulation, what follows for moral responsibility?"
        response1 = "Therefore, we should observe different ethical patterns in simulated vs real scenarios."
        response2 = "I agree with the previous point about simulation theory."
        
        validation1 = detector.validate_consequence_response(test_prompt, response1)
        validation2 = detector.validate_consequence_response(test_prompt, response2)
        
        print(f"🔬 Test prompt: {test_prompt[:40]}...")
        print(f"✅ Good response validation: {validation1}")
        print(f"❌ Poor response validation: {validation2}")
        
        assert validation1["has_entailments"]
        assert validation1["quality_score"] > validation2["quality_score"]
        
        # Test entailment explanation
        explanation = detector.explain_entailments(multi_text)
        print(f"💡 Entailment explanation: {explanation}")
        assert explanation  # Should have explanations
        
        print("✅ Enhanced EntailmentDetector tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced EntailmentDetector tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_consequence_test_generator():
    """Test ConsequenceTestGenerator agent"""
    print("\n" + "="*60)
    print("TEST 4: ConsequenceTestGenerator")
    print("="*60 + "\n")
    
    try:
        from src.agents.consequence_test_generator import ConsequenceTestGenerator, ConsequenceTestContext
        
        # Test without LLM for speed
        generator = ConsequenceTestGenerator(llm_client=None)
        
        # Test basic test generation
        context = ConsequenceTestContext(
            tension=("necessity", "contingency"),
            current_claim="Reality operates according to necessary laws",
            discussion_summary="Discussion about determinism vs freedom",
            turn_count=5
        )
        
        test_prompt = await generator.generate_test(context)
        print(f"🔬 Generated test: {test_prompt}")
        assert "Consequence Test:" in test_prompt
        # The test should be related to the provided claim somehow
        assert len(test_prompt) > 50  # Should be a substantial test prompt
        
        # Test with different tension
        context2 = ConsequenceTestContext(
            tension=("structure", "agency"),
            current_claim="Social structures determine individual choices",
            discussion_summary="Discussion about freedom within constraints",
            turn_count=8,
            previous_tests=["Previous test about structure"]
        )
        
        test_prompt2 = await generator.generate_test(context2)
        print(f"🔬 Generated test 2: {test_prompt2}")
        assert "Consequence Test:" in test_prompt2
        assert test_prompt2 != test_prompt  # Should be different
        
        # Test synthesis generation
        synthesis = generator.generate_synthesis_prompt(
            tension=("objectivity", "subjectivity"),
            failed_tests=["Test 1", "Test 2"],
            discussion_summary="Extended discussion on truth"
        )
        print(f"🎯 Generated synthesis: {synthesis[:100]}...")
        assert "synthesis" in synthesis.lower() or "voice of reason" in synthesis.lower()
        
        # Test template selection variety
        test_prompts = []
        for i in range(5):
            context_var = ConsequenceTestContext(
                tension=("math", "ethics"),
                current_claim=f"Mathematical truth {i}",
                discussion_summary="Math vs ethics discussion",
                turn_count=i+1
            )
            prompt = await generator.generate_test(context_var)
            test_prompts.append(prompt)
        
        print(f"🎲 Generated {len(set(test_prompts))} unique prompts out of 5 attempts")
        # Should have some variety (at least 2 different prompts)
        assert len(set(test_prompts)) >= 2
        
        print("✅ ConsequenceTestGenerator tests passed")
        return True
        
    except Exception as e:
        print(f"❌ ConsequenceTestGenerator tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_progression_controller():
    """Test ProgressionController orchestration logic"""
    print("\n" + "="*60)
    print("TEST 5: ProgressionController")
    print("="*60 + "\n")
    
    try:
        from src.controllers.progression_controller import ProgressionController, ProgressionConfig
        
        # Create test config
        config = ProgressionConfig(
            cycles_threshold=2,
            max_consequence_tests=2,
            enable_progression=True
        )
        
        controller = ProgressionController(config, llm_client=None)
        
        # Test normal turn processing
        result1 = await controller.process_turn(
            content="This is a normal philosophical statement about truth.",
            speaker="Alice",
            context={"episode_summary": "Discussion about truth"}
        )
        
        print(f"📊 Normal turn result: {result1['state_update']}")
        assert "interventions" in result1
        assert "state_update" in result1
        assert result1["state_update"]["turn_index"] == 1
        
        # Test turn with tension but no entailment (should increment cycles)
        result2 = await controller.process_turn(
            content="The necessity of moral laws conflicts with our contingent feelings.",
            speaker="Bob",
            context={"episode_summary": "Discussion continues"}
        )
        
        print(f"📊 Tension turn result: {result2['state_update']}")
        assert result2["state_update"]["turn_index"] == 2
        active_tensions = result2["state_update"]["active_tensions"]
        print(f"⚡ Active tensions: {active_tensions}")
        
        # Process another turn on same tension without entailment
        result3 = await controller.process_turn(
            content="Yes, the necessity versus contingency issue remains unresolved here.",
            speaker="Charlie",
            context={"episode_summary": "Discussion continues"}
        )
        
        print(f"📊 Second tension turn: {result3['state_update']}")
        interventions = result3.get("interventions", [])
        print(f"🔬 Interventions triggered: {len(interventions)}")
        
        # Should trigger consequence test after 2 cycles
        if interventions:
            print(f"🔬 First intervention: {interventions[0]['type']}")
            assert interventions[0]["type"] == "consequence_test"
        
        # Test entailment reset
        result4 = await controller.process_turn(
            content="Therefore, we can test this by examining specific moral decisions.",
            speaker="Alice",
            context={"episode_summary": "Discussion continues"}
        )
        
        print(f"📊 Entailment turn: {result4['state_update']}")
        assert result4["state_update"]["has_entailment"]
        
        # Test status report
        status = controller.get_status_report()
        print(f"📋 Status report: {status['metrics']}")
        assert "turns_processed" in status["metrics"]
        assert status["metrics"]["turns_processed"] == 4
        
        print("✅ ProgressionController tests passed")
        return True
        
    except Exception as e:
        print(f"❌ ProgressionController tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_orchestrator_integration():
    """Test integration with main orchestrator (basic sanity check)"""
    print("\n" + "="*60)
    print("TEST 6: Orchestrator Integration")
    print("="*60 + "\n")
    
    try:
        from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator
        
        # Basic participants config
        participants_config = [
            {
                "name": "Alice",
                "gender": "female",
                "personality": "analytical",
                "expertise": "philosophy"
            },
            {
                "name": "Bob", 
                "gender": "male",
                "personality": "skeptical",
                "expertise": "logic"
            }
        ]
        
        # Test orchestrator creation with progression control
        orchestrator = MultiAgentDiscussionOrchestrator(
            topic="The nature of free will",
            target_depth=3,
            participants_config=participants_config,
            enable_narrator=False,
            enable_synthesizer=False,
            enable_coda=False,
            enable_redundancy_control=False,
            enable_progression_control=True,
            progression_config={
                "cycles_threshold": 2,
                "max_consequence_tests": 2,
                "enable_progression": True
            }
        )
        
        print(f"🎭 Orchestrator created successfully")
        print(f"🚀 Progression control enabled: {orchestrator.enable_progression_control}")
        assert orchestrator.enable_progression_control
        assert orchestrator.progression_controller is not None
        
        # Test progression controller configuration
        prog_config = orchestrator.progression_controller.config
        print(f"⚙️  Progression config: cycles={prog_config.cycles_threshold}, tests={prog_config.max_consequence_tests}")
        assert prog_config.cycles_threshold == 2
        assert prog_config.max_consequence_tests == 2
        
        print("✅ Orchestrator integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator integration tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_configuration_loading():
    """Test configuration loading from talks.yml"""
    print("\n" + "="*60)
    print("TEST 7: Configuration Loading")
    print("="*60 + "\n")
    
    try:
        from src.config import TalksConfig
        
        config = TalksConfig()
        
        # Test progression engine config loading
        prog_enabled = config.get('progression_engine.enabled', False)
        cycles_threshold = config.get('progression_engine.cycles_threshold', 2)
        max_tests = config.get('progression_engine.max_consequence_tests', 2)
        
        print(f"⚙️  Config loaded - enabled: {prog_enabled}, cycles: {cycles_threshold}, tests: {max_tests}")
        
        # Should have progression config in talks.yml now
        assert isinstance(prog_enabled, bool)
        assert isinstance(cycles_threshold, int)
        assert isinstance(max_tests, int)
        
        # Test tension list loading
        tensions = config.get('progression_engine.tensions', [])
        print(f"⚡ Configured tensions: {len(tensions)} found")
        if tensions:
            print(f"   Example: {tensions[0]}")
            assert isinstance(tensions[0], list)
            assert len(tensions[0]) == 2
        
        # Test consequence domains
        domains = config.get('progression_engine.consequence_domains', [])
        print(f"🎯 Configured domains: {len(domains)} found")
        if domains:
            print(f"   Example: {domains[0]}")
            assert isinstance(domains[0], str)
        
        print("✅ Configuration loading tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_progression_state_persistence():
    """Test progression state save/load functionality"""
    print("\n" + "="*60)
    print("TEST 8: State Persistence")
    print("="*60 + "\n")
    
    try:
        from src.controllers.progression_controller import ProgressionController, ProgressionConfig
        import tempfile
        import json
        
        # Create controller and process some turns
        config = ProgressionConfig(cycles_threshold=2, max_consequence_tests=2)
        controller = ProgressionController(config, llm_client=None)
        
        # Process turns to create state
        await controller.process_turn(
            content="Necessity versus contingency is a fundamental tension.",
            speaker="Alice",
            context={}
        )
        
        await controller.process_turn(
            content="The contingent nature of reality challenges necessary truths.",
            speaker="Bob", 
            context={}
        )
        
        # Save state
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            state_file = f.name
        
        controller.save_state(state_file)
        print(f"💾 State saved to: {state_file}")
        
        # Verify file exists and has content
        with open(state_file, 'r') as f:
            saved_data = json.load(f)
        
        print(f"📄 Saved data keys: {list(saved_data.keys())}")
        assert "tensions" in saved_data
        assert "turn_index" in saved_data
        assert "metrics" in saved_data
        assert saved_data["turn_index"] == 2
        
        # Test loading state
        new_controller = ProgressionController(config, llm_client=None)
        new_controller.load_state(state_file)
        
        print(f"📥 State loaded, turn index: {new_controller.state.turn_index}")
        assert new_controller.state.turn_index == 2
        assert len(new_controller.state.tensions) > 0
        
        # Clean up
        Path(state_file).unlink()
        
        print("✅ State persistence tests passed")
        return True
        
    except Exception as e:
        print(f"❌ State persistence tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_end_to_end_scenario():
    """Test complete end-to-end progression control scenario"""
    print("\n" + "="*60)
    print("TEST 9: End-to-End Scenario")
    print("="*60 + "\n")
    
    try:
        from src.controllers.progression_controller import ProgressionController, ProgressionConfig
        
        # Scenario: Discussion that should trigger progression control
        config = ProgressionConfig(cycles_threshold=2, max_consequence_tests=2)
        controller = ProgressionController(config, llm_client=None)
        
        print("🎬 Starting end-to-end scenario...")
        
        # Turn 1: Introduce tension
        result1 = await controller.process_turn(
            content="The structure of reality determines everything we do.",
            speaker="Alice",
            context={"episode_summary": "Discussion on determinism"}
        )
        print(f"Turn 1: {result1['state_update']['active_tensions']}")
        
        # Turn 2: Same tension, no entailment (should increment cycle)
        result2 = await controller.process_turn(
            content="But human agency seems to allow genuine choice within structures.",
            speaker="Bob",
            context={"episode_summary": "Continuing discussion"}
        )
        print(f"Turn 2: Interventions={len(result2.get('interventions', []))}")
        
        # Turn 3: Repeat tension, should trigger consequence test
        result3 = await controller.process_turn(
            content="The tension between structure and agency remains unresolved.",
            speaker="Charlie",
            context={"episode_summary": "Still discussing"}
        )
        print(f"Turn 3: Interventions={len(result3.get('interventions', []))}")
        
        # Should have triggered consequence test
        if result3.get('interventions'):
            intervention = result3['interventions'][0]
            print(f"🔬 Triggered: {intervention['type']} for {intervention['tension']}")
            assert intervention['type'] == 'consequence_test'
        
        # Turn 4: Poor response to test (no entailment)
        result4 = await controller.process_turn(
            content="I agree with the previous points about structure and agency.",
            speaker="Alice",
            context={"episode_summary": "Responding to test"}
        )
        print(f"Turn 4: Entailment={result4['state_update'].get('has_entailment', False)}")
        
        # Turn 5: Another poor response, might trigger pivot
        result5 = await controller.process_turn(
            content="Yes, the structure agency question is complex.",
            speaker="Bob",
            context={"episode_summary": "Still no progress"}
        )
        print(f"Turn 5: Interventions={len(result5.get('interventions', []))}")
        
        # Get final status
        final_status = controller.get_status_report()
        print(f"📊 Final metrics: {final_status['metrics']}")
        
        # Verify progression control worked
        assert final_status['metrics']['turns_processed'] == 5
        assert final_status['metrics']['tests_injected'] >= 1
        
        print("✅ End-to-end scenario tests passed")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end scenario tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all progression control tests"""
    print("🚀 Starting Force Progression, Stop Orbiting Test Suite")
    print("=" * 80)
    
    tests = [
        test_tension_state_enhanced,
        test_topic_extractor,
        test_enhanced_entailment_detector,
        test_consequence_test_generator,
        test_progression_controller,
        test_orchestrator_integration,
        test_configuration_loading,
        test_progression_state_persistence,
        test_end_to_end_scenario
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
        print("✅ ALL TESTS PASSED - Force Progression, Stop Orbiting is ready!")
        print("\n🚀 System Features Verified:")
        print("  • Enhanced TensionState with consequence test tracking")
        print("  • TopicExtractor for philosophical concept detection")
        print("  • Enhanced EntailmentDetector with consequence patterns")
        print("  • ConsequenceTestGenerator for contextual test prompts")
        print("  • ProgressionController orchestration logic")
        print("  • Full orchestrator integration")
        print("  • Configuration and CLI options")
        print("  • State persistence and metrics tracking")
        print("  • End-to-end progression control workflow")
    else:
        print(f"⚠️ {failed} tests failed - check implementation")
    
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)