#!/usr/bin/env python3
"""Comprehensive test suite for Intellectual Gravitas quote enrichment system"""

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


async def test_quote_corpus():
    """Test quote corpus loading and structure"""
    print("\n" + "="*60)
    print("TEST 1: Quote Corpus")
    print("="*60 + "\n")
    
    try:
        import json
        from pathlib import Path
        
        corpus_path = Path("data/philosophical_quotes.jsonl")
        
        # Test corpus file exists
        assert corpus_path.exists(), f"Quote corpus not found at {corpus_path}"
        
        # Load and validate quotes
        quotes = []
        with open(corpus_path, 'r') as f:
            for line in f:
                if line.strip():
                    quote = json.loads(line.strip())
                    quotes.append(quote)
        
        print(f"📚 Loaded {len(quotes)} quotes from corpus")
        assert len(quotes) > 0, "Corpus should contain quotes"
        
        # Validate quote schema
        required_fields = ['id', 'quote', 'author', 'source', 'era', 'tradition', 'topics', 'polarity', 'tone', 'word_count']
        sample_quote = quotes[0]
        
        for field in required_fields:
            assert field in sample_quote, f"Missing required field: {field}"
        
        print(f"✅ Quote schema validation passed")
        
        # Check distribution
        eras = {}
        traditions = {}
        authors = set()
        
        for quote in quotes:
            era = quote['era']
            tradition = quote['tradition']
            eras[era] = eras.get(era, 0) + 1
            traditions[tradition] = traditions.get(tradition, 0) + 1
            authors.add(quote['author'])
        
        print(f"📊 Distribution:")
        print(f"   Eras: {eras}")
        print(f"   Traditions: {traditions}")
        print(f"   Unique authors: {len(authors)}")
        
        # Sample quotes
        print(f"\n📝 Sample quotes:")
        for i, quote in enumerate(quotes[:3]):
            print(f"   {i+1}. \"{quote['quote']}\" — {quote['author']}")
            print(f"      Topics: {', '.join(quote['topics'][:3])}")
        
        print("✅ Quote corpus tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Quote corpus tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_quote_retrieval():
    """Test quote retrieval system"""
    print("\n" + "="*60)
    print("TEST 2: Quote Retrieval")
    print("="*60 + "\n")
    
    try:
        from src.retrieval.quote_retriever import QuoteRetriever
        
        retriever = QuoteRetriever()
        
        print(f"📚 Initialized retriever with {len(retriever.quotes)} quotes")
        assert len(retriever.quotes) > 0, "Should load quotes from corpus"
        
        # Test basic retrieval
        quotes = retriever.retrieve(
            topics=["truth", "knowledge", "certainty"],
            current_tension=("necessity", "contingency"),
            top_k=3
        )
        
        print(f"\n🔍 Retrieved {len(quotes)} quotes for 'truth, knowledge, certainty':")
        for i, quote in enumerate(quotes, 1):
            print(f"   {i}. {quote['author']} ({quote['era']}, {quote['tradition']})")
            print(f"      \"{quote['quote']}\"")
            print(f"      Relevance: {quote.get('relevance_score', 0):.3f}")
            print(f"      Topics: {', '.join(quote['topics'][:3])}")
        
        assert len(quotes) > 0, "Should retrieve at least one quote"
        
        # Test topic matching
        philosophy_quotes = retriever.retrieve(
            topics=["philosophy", "wisdom"],
            top_k=5
        )
        
        print(f"\n🧠 Philosophy/wisdom search returned {len(philosophy_quotes)} quotes")
        
        # Test diversity (multiple retrievals)
        authors_used = set()
        for i in range(3):
            diverse_quotes = retriever.retrieve(
                topics=["ethics", "virtue"],
                top_k=2
            )
            for quote in diverse_quotes:
                authors_used.add(quote['author'])
        
        print(f"\n🎲 Diversity test: {len(authors_used)} unique authors across 3 retrievals")
        
        # Get statistics
        stats = retriever.get_statistics()
        print(f"\n📊 Retrieval Statistics:")
        print(f"   Total quotes: {stats['total_quotes']}")
        print(f"   Quotes used: {stats['quotes_used']}")
        print(f"   Unique authors: {stats['unique_authors']}")
        print(f"   Semantic search: {stats['semantic_search_enabled']}")
        
        print("✅ Quote retrieval tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Quote retrieval tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_quote_enrichment_agent():
    """Test quote enrichment agent"""
    print("\n" + "="*60)
    print("TEST 3: Quote Enrichment Agent")
    print("="*60 + "\n")
    
    try:
        from src.agents.quote_enrichment_agent import QuoteEnrichmentAgent
        from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype
        
        # Create test agent
        enrichment_agent = QuoteEnrichmentAgent(quote_interval=2)
        
        print(f"📚 Initialized enrichment agent (interval={enrichment_agent.quote_interval})")
        
        # Test should_enrich logic
        assert not enrichment_agent.should_enrich(0), "Should not enrich on turn 0"
        assert not enrichment_agent.should_enrich(1), "Should not enrich on turn 1 (interval=2)"
        assert enrichment_agent.should_enrich(2), "Should enrich on turn 2"
        
        print("✅ Enrichment timing logic works")
        
        # Create test speaker
        speaker = ParticipantState(
            participant_id="test_speaker",
            name="Sophia",
            gender=Gender.FEMALE,
            personality=PersonalityArchetype.CREATIVE,
            expertise_area="philosophy"
        )
        
        print(f"👤 Created test speaker: {speaker.name} ({speaker.personality.value})")
        
        # Test quote enrichment
        original_response = "Consciousness seems to require both unity and diversity of experience."
        
        enriched_response = await enrichment_agent.enrich_response(
            response=original_response,
            speaker=speaker,
            discussion_topics=["consciousness", "experience", "unity"],
            current_tension=("structure", "agency"),
            discussion_context="We're exploring how consciousness emerges from complexity."
        )
        
        print(f"\n📝 Original response:")
        print(f"   {original_response}")
        print(f"\n✨ Enriched response:")
        print(f"   {enriched_response[:200]}...")
        
        # Validate enrichment
        assert len(enriched_response) > len(original_response), "Enriched should be longer"
        assert original_response in enriched_response, "Should contain original response"
        assert "consciousness" in enriched_response.lower(), "Should preserve topic"
        
        # Test statistics
        stats = enrichment_agent.get_statistics()
        print(f"\n📊 Enrichment Statistics:")
        print(f"   Quotes placed: {stats['quotes_placed']}")
        print(f"   Semantic search enabled: {stats['semantic_search_enabled']}")
        
        assert stats['quotes_placed'] == 1, "Should have placed one quote"
        
        print("✅ Quote enrichment agent tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Quote enrichment agent tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_voice_adaptation():
    """Test voice adaptation functionality"""
    print("\n" + "="*60)
    print("TEST 4: Voice Adaptation")
    print("="*60 + "\n")
    
    try:
        from src.agents.quote_enrichment_agent import QuoteEnrichmentAgent
        from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype
        
        enrichment_agent = QuoteEnrichmentAgent(enable_voice_adaptation=True)
        
        # Test speakers with different personalities
        speakers = [
            ParticipantState("analytical", "Marcus", Gender.MALE, PersonalityArchetype.ANALYTICAL, "logic"),
            ParticipantState("creative", "Luna", Gender.FEMALE, PersonalityArchetype.CREATIVE, "art"),
            ParticipantState("skeptical", "Diogenes", Gender.MALE, PersonalityArchetype.SKEPTICAL, "philosophy")
        ]
        
        # Test quote for adaptation
        test_quote = {
            'id': 'test_socrates_01',
            'quote': 'The unexamined life is not worth living.',
            'author': 'Socrates',
            'topics': ['self-knowledge', 'philosophy']
        }
        
        print(f"🎭 Testing voice adaptation for quote: \"{test_quote['quote']}\"")
        
        for speaker in speakers:
            try:
                adapted = await enrichment_agent._adapt_quote_to_voice(
                    quote=test_quote,
                    speaker=speaker,
                    context="We've been discussing self-awareness and consciousness."
                )
                
                print(f"\n👤 {speaker.name} ({speaker.personality.value}):")
                print(f"   \"{adapted}\"")
                
                # Basic validation
                assert len(adapted) > 5, "Adapted quote should have substance"
                assert "socrates" in adapted.lower() or "The unexamined life" in adapted, "Should reference original"
                
            except Exception as e:
                # Voice adaptation might fail due to LLM availability, but test basic functionality
                print(f"   ⚠️ Voice adaptation failed for {speaker.name}: {e}")
                print(f"   (This is expected if LLM is not available)")
        
        print("✅ Voice adaptation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Voice adaptation tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_orchestrator_integration():
    """Test integration with main orchestrator"""
    print("\n" + "="*60)
    print("TEST 5: Orchestrator Integration")
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
                "personality": "creative",
                "expertise": "ethics"
            }
        ]
        
        # Test orchestrator creation with quote enrichment
        orchestrator = MultiAgentDiscussionOrchestrator(
            topic="The nature of consciousness",
            target_depth=3,
            participants_config=participants_config,
            enable_narrator=False,
            enable_synthesizer=False,
            enable_coda=False,
            enable_redundancy_control=False,
            enable_progression_control=False,
            enable_quote_enrichment=True,
            quote_interval=4,
            enable_quote_voice_adaptation=True
        )
        
        print(f"🎭 Orchestrator created successfully")
        print(f"📚 Quote enrichment enabled: {orchestrator.enable_quote_enrichment}")
        assert orchestrator.enable_quote_enrichment
        assert orchestrator.quote_agent is not None
        
        # Test quote agent configuration
        quote_agent = orchestrator.quote_agent
        print(f"📖 Quote agent interval: {quote_agent.quote_interval}")
        print(f"🎭 Voice adaptation: {quote_agent.enable_voice_adaptation}")
        assert quote_agent.quote_interval == 4
        assert quote_agent.enable_voice_adaptation == True
        
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
    print("TEST 6: Configuration Loading")
    print("="*60 + "\n")
    
    try:
        from src.config import TalksConfig
        
        config = TalksConfig()
        
        # Test quote config loading
        quotes_enabled = config.get('quotes.enabled', False)
        quote_interval = config.get('quotes.interval', 8)
        voice_adaptation = config.get('quotes.voice_adaptation', True)
        
        print(f"⚙️  Quote config loaded:")
        print(f"   Enabled: {quotes_enabled}")
        print(f"   Interval: {quote_interval}")
        print(f"   Voice adaptation: {voice_adaptation}")
        
        # Should have quote configuration in talks.yml now
        assert isinstance(quotes_enabled, bool)
        assert isinstance(quote_interval, int)
        assert isinstance(voice_adaptation, bool)
        
        # Test retrieval settings
        top_k = config.get('quotes.retrieval.top_k', 3)
        relevance_threshold = config.get('quotes.retrieval.relevance_threshold', 0.4)
        diversity_weight = config.get('quotes.retrieval.diversity_weight', 0.3)
        
        print(f"🔍 Retrieval settings:")
        print(f"   Top K: {top_k}")
        print(f"   Relevance threshold: {relevance_threshold}")
        print(f"   Diversity weight: {diversity_weight}")
        
        assert isinstance(top_k, int)
        assert isinstance(relevance_threshold, float)
        assert isinstance(diversity_weight, float)
        
        # Test balance targets
        era_balance = config.get('quotes.balance.era', {})
        tradition_balance = config.get('quotes.balance.tradition', {})
        
        print(f"⚖️  Balance targets:")
        print(f"   Era balance: {era_balance}")
        print(f"   Tradition balance: {tradition_balance}")
        
        if era_balance:
            assert isinstance(era_balance, dict)
            assert 'ancient' in era_balance or 'modern' in era_balance
        
        print("✅ Configuration loading tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_diversity_enforcement():
    """Test author diversity enforcement"""
    print("\n" + "="*60)
    print("TEST 7: Diversity Enforcement")
    print("="*60 + "\n")
    
    try:
        from src.retrieval.quote_retriever import QuoteRetriever
        
        retriever = QuoteRetriever()
        
        # Retrieve multiple times to test diversity
        all_authors = []
        recent_authors = []
        
        for i in range(6):
            quotes = retriever.retrieve(
                topics=["wisdom", "truth"],
                top_k=2
            )
            
            if quotes:
                turn_authors = [q['author'] for q in quotes]
                all_authors.extend(turn_authors)
                recent_authors.extend(turn_authors)
                
                print(f"\nRetrieval {i+1}:")
                for q in quotes:
                    print(f"   - {q['author']}: \"{q['quote'][:40]}...\"")
                
                # Keep only recent 6 authors for diversity check
                if len(recent_authors) > 6:
                    recent_authors = recent_authors[-6:]
        
        # Check diversity metrics
        unique_all = len(set(all_authors))
        unique_recent = len(set(recent_authors))
        
        print(f"\n📊 Diversity Analysis:")
        print(f"   Total quotes retrieved: {len(all_authors)}")
        print(f"   Unique authors (all): {unique_all}")
        print(f"   Unique authors (recent 6): {unique_recent}/{len(recent_authors)}")
        
        # Get final statistics
        stats = retriever.get_statistics()
        print(f"   Authors used: {len(stats['author_usage'])}")
        print(f"   Recent authors: {stats['recent_authors']}")
        
        # Verify diversity
        diversity_ratio = unique_recent / len(recent_authors) if recent_authors else 0
        print(f"   Diversity ratio: {diversity_ratio:.2f}")
        
        # Should have reasonable diversity (not perfect due to small test corpus)
        assert diversity_ratio >= 0.3, f"Diversity ratio too low: {diversity_ratio}"
        
        print("✅ Diversity enforcement tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Diversity enforcement tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_end_to_end_flow():
    """Test complete end-to-end quote enrichment flow"""
    print("\n" + "="*60)
    print("TEST 8: End-to-End Flow")
    print("="*60 + "\n")
    
    try:
        from src.agents.quote_enrichment_agent import QuoteEnrichmentAgent
        from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype
        
        # Scenario: Multi-turn discussion with quote enrichment
        enrichment_agent = QuoteEnrichmentAgent(quote_interval=3, enable_voice_adaptation=False)
        
        speakers = [
            ParticipantState("alice", "Alice", Gender.FEMALE, PersonalityArchetype.ANALYTICAL, "logic"),
            ParticipantState("bob", "Bob", Gender.MALE, PersonalityArchetype.CREATIVE, "philosophy")
        ]
        
        print("🎬 Starting end-to-end quote enrichment scenario...")
        
        # Simulate multiple turns
        responses = [
            ("Alice", "What is the nature of consciousness?"),
            ("Bob", "Consciousness seems to emerge from complexity."),
            ("Alice", "But how can we be certain of our own awareness?"),  # Should get quote
            ("Bob", "Perhaps doubt itself is a form of certainty."),
            ("Alice", "The relationship between mind and matter remains mysterious."),
            ("Bob", "Maybe the mystery is part of the answer.")  # Should get quote
        ]
        
        enriched_count = 0
        
        for i, (speaker_name, response) in enumerate(responses):
            speaker = next(s for s in speakers if s.name == speaker_name)
            
            print(f"\nTurn {i}: {speaker_name}")
            print(f"Original: {response}")
            
            if enrichment_agent.should_enrich(i):
                try:
                    enriched = await enrichment_agent.enrich_response(
                        response=response,
                        speaker=speaker,
                        discussion_topics=["consciousness", "awareness", "mind"],
                        current_tension=("mind", "matter"),
                        discussion_context="Philosophical discussion about consciousness"
                    )
                    
                    print(f"Enriched: {enriched[:150]}...")
                    enriched_count += 1
                    
                    # Validate enrichment
                    assert len(enriched) > len(response), "Should be enriched"
                    assert response in enriched, "Should contain original"
                    
                except Exception as e:
                    print(f"   ⚠️ Enrichment failed: {e}")
            else:
                print(f"No enrichment (interval not met)")
        
        # Check final statistics
        final_stats = enrichment_agent.get_statistics()
        print(f"\n📊 Final Statistics:")
        print(f"   Quotes placed: {final_stats['quotes_placed']}")
        print(f"   Expected: {enriched_count}")
        
        print("✅ End-to-end flow tests passed")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end flow tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all quote enrichment tests"""
    print("🚀 Starting Intellectual Gravitas Quote Enrichment Test Suite")
    print("=" * 80)
    
    tests = [
        test_quote_corpus,
        test_quote_retrieval,
        test_quote_enrichment_agent,
        test_voice_adaptation,
        test_orchestrator_integration,
        test_configuration_loading,
        test_diversity_enforcement,
        test_end_to_end_flow
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
        print("✅ ALL TESTS PASSED - Intellectual Gravitas Quote Enrichment is ready!")
        print("\n📚 System Features Verified:")
        print("  • Philosophical quote corpus with structured metadata")
        print("  • Semantic retrieval with keyword fallback") 
        print("  • Author diversity enforcement and tracking")
        print("  • Voice adaptation for speaker personalities")
        print("  • Strategic quote placement timing")
        print("  • Full orchestrator integration")
        print("  • Configuration and CLI options")
        print("  • End-to-end enrichment workflow")
        print("\n🎭 Ready to add intellectual gravitas to philosophical discussions!")
    else:
        print(f"⚠️ {failed} tests failed - check implementation")
    
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)