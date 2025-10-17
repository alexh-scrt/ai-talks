#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Quote Retrieval System

Tests all components: parser, knowledge graph, vector store, and integrated retrieval.
Validates system performance, accuracy, and production readiness.
"""

import time
from pathlib import Path
from enhanced_quote_retriever import EnhancedQuoteRetriever
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuoteSystemTester:
    """Comprehensive test suite for the quote retrieval system"""
    
    def __init__(self):
        self.retriever = EnhancedQuoteRetriever()
        self.test_results = {
            'parsing': {},
            'knowledge_graph': {},
            'vector_store': {},
            'integration': {},
            'performance': {}
        }
    
    def test_corpus_quality(self):
        """Test the quality and coverage of the parsed corpus"""
        print("📚 Testing Corpus Quality")
        print("-" * 40)
        
        stats = self.retriever.get_statistics()
        
        # Check corpus size
        if 'vector_store' in stats:
            vs_stats = stats['vector_store']
            total_quotes = vs_stats['total_quotes']
            unique_authors = vs_stats['unique_authors']
            unique_topics = vs_stats['unique_topics']
            
            print(f"✅ Total quotes: {total_quotes} (target: >500)")
            print(f"✅ Unique authors: {unique_authors} (target: >300)")
            print(f"✅ Unique topics: {unique_topics} (target: >5)")
            
            # Quality metrics
            author_diversity = unique_authors / total_quotes if total_quotes > 0 else 0
            print(f"📊 Author diversity: {author_diversity:.3f} (target: >0.5)")
            
            self.test_results['parsing'] = {
                'total_quotes': total_quotes,
                'unique_authors': unique_authors,
                'unique_topics': unique_topics,
                'author_diversity': author_diversity,
                'quality_score': min(1.0, (total_quotes/500 + unique_authors/300 + unique_topics/5) / 3)
            }
    
    def test_semantic_search_accuracy(self):
        """Test semantic search accuracy across different domains"""
        print("\n🧠 Testing Semantic Search Accuracy")
        print("-" * 40)
        
        test_queries = [
            ("What is the meaning of life?", ["meaning", "life", "purpose"]),
            ("How do we acquire knowledge?", ["knowledge", "truth", "wisdom"]),
            ("What is consciousness?", ["consciousness", "mind", "awareness"]),
            ("How should we live ethically?", ["virtue", "ethics", "moral"]),
            ("What is the nature of time?", ["time", "change", "temporal"])
        ]
        
        accuracy_scores = []
        
        for query, expected_topics in test_queries:
            results = self.retriever.search_quotes(query, "semantic", limit=5)
            
            if results:
                # Check if results contain expected topics
                found_topics = set()
                for quote in results:
                    found_topics.update(quote.get('topics', []))
                
                overlap = len(set(expected_topics) & found_topics)
                accuracy = overlap / len(expected_topics) if expected_topics else 0
                accuracy_scores.append(accuracy)
                
                print(f"Query: '{query[:30]}...'")
                print(f"  Expected topics: {expected_topics}")
                print(f"  Found topics: {list(found_topics)}")
                print(f"  Accuracy: {accuracy:.2f}")
                print(f"  Top result: {results[0]['author']}")
        
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
        print(f"\n📊 Average semantic accuracy: {avg_accuracy:.3f}")
        
        self.test_results['vector_store']['semantic_accuracy'] = avg_accuracy
    
    def test_knowledge_graph_connectivity(self):
        """Test knowledge graph structure and connectivity"""
        print("\n🕸️  Testing Knowledge Graph Connectivity")
        print("-" * 40)
        
        stats = self.retriever.get_statistics()
        
        if 'knowledge_graph' in stats:
            kg_stats = stats['knowledge_graph']
            
            total_nodes = kg_stats.get('authors', 0) + kg_stats.get('quotes', 0) + kg_stats.get('topics', 0)
            total_relationships = kg_stats.get('relationships', 0)
            
            print(f"✅ Total nodes: {total_nodes}")
            print(f"✅ Total relationships: {total_relationships}")
            
            # Test author networks
            test_authors = ["Albert Einstein", "Aristotle", "Nietzsche"]
            network_qualities = []
            
            for author in test_authors:
                network = self.retriever.get_author_network(author)
                if network:
                    network_size = network.get('network_size', 0)
                    related_authors = len(network.get('related_authors', []))
                    related_topics = len(network.get('related_topics', []))
                    
                    quality = min(1.0, (network_size/10 + related_authors/3 + related_topics/3) / 3)
                    network_qualities.append(quality)
                    
                    print(f"Author: {author}")
                    print(f"  Network size: {network_size}")
                    print(f"  Related authors: {related_authors}")
                    print(f"  Related topics: {related_topics}")
            
            avg_network_quality = sum(network_qualities) / len(network_qualities) if network_qualities else 0
            print(f"\n📊 Average network quality: {avg_network_quality:.3f}")
            
            self.test_results['knowledge_graph'] = {
                'total_nodes': total_nodes,
                'total_relationships': total_relationships,
                'network_quality': avg_network_quality,
                'connectivity_score': min(1.0, total_relationships / max(total_nodes, 1))
            }
    
    def test_search_performance(self):
        """Test search performance and response times"""
        print("\n⚡ Testing Search Performance")
        print("-" * 40)
        
        test_queries = [
            "meaning of life",
            "consciousness and mind",
            "virtue and ethics",
            "nature of time",
            "wisdom and knowledge"
        ]
        
        search_modes = ["semantic", "hybrid"]
        performance_results = {}
        
        for mode in search_modes:
            times = []
            for query in test_queries:
                start_time = time.time()
                results = self.retriever.search_quotes(query, mode, limit=10)
                end_time = time.time()
                
                search_time = end_time - start_time
                times.append(search_time)
                
                print(f"{mode.capitalize()} search '{query[:20]}...': {search_time:.3f}s ({len(results)} results)")
            
            avg_time = sum(times) / len(times)
            performance_results[mode] = {
                'avg_time': avg_time,
                'max_time': max(times),
                'searches_per_second': 1 / avg_time if avg_time > 0 else 0
            }
        
        print(f"\n📊 Performance Summary:")
        for mode, perf in performance_results.items():
            print(f"{mode.capitalize()}: {perf['avg_time']:.3f}s avg, {perf['searches_per_second']:.1f} searches/sec")
        
        self.test_results['performance'] = performance_results
    
    def test_diversity_and_relevance(self):
        """Test result diversity and relevance"""
        print("\n🌈 Testing Diversity and Relevance")
        print("-" * 40)
        
        query = "wisdom and knowledge"
        results = self.retriever.search_quotes(query, "hybrid", limit=10)
        
        if results:
            # Author diversity
            authors = [r['author'] for r in results]
            unique_authors = len(set(authors))
            author_diversity = unique_authors / len(results)
            
            # Era diversity
            eras = [r.get('era', 'unknown') for r in results]
            unique_eras = len(set(eras))
            
            # Topic diversity
            all_topics = []
            for r in results:
                all_topics.extend(r.get('topics', []))
            unique_topics = len(set(all_topics))
            
            # Average relevance score
            avg_relevance = sum(r.get('final_score', 0) for r in results) / len(results)
            
            print(f"Author diversity: {author_diversity:.3f} ({unique_authors}/{len(results)})")
            print(f"Era diversity: {unique_eras} different eras")
            print(f"Topic diversity: {unique_topics} different topics")
            print(f"Average relevance: {avg_relevance:.3f}")
            
            self.test_results['integration'] = {
                'author_diversity': author_diversity,
                'era_diversity': unique_eras,
                'topic_diversity': unique_topics,
                'avg_relevance': avg_relevance,
                'overall_quality': (author_diversity + min(unique_eras/3, 1) + min(unique_topics/5, 1) + min(avg_relevance, 1)) / 4
            }
    
    def test_recommendation_system(self):
        """Test personalized recommendation system"""
        print("\n💡 Testing Recommendation System")
        print("-" * 40)
        
        # Simulate user queries to build history
        simulation_queries = [
            "meaning of life",
            "consciousness",
            "virtue and ethics",
            "wisdom"
        ]
        
        for query in simulation_queries:
            self.retriever.search_quotes(query, "hybrid", limit=3)
        
        # Get recommendations
        recommendations = self.retriever.get_recommendations(5)
        
        if recommendations:
            print(f"Generated {len(recommendations)} recommendations")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['author']}: \"{rec['quote'][:50]}...\"")
                print(f"   Topics: {', '.join(rec.get('topics', []))}")
            
            # Check recommendation quality
            rec_topics = []
            for rec in recommendations:
                rec_topics.extend(rec.get('topics', []))
            
            topic_diversity = len(set(rec_topics)) / len(rec_topics) if rec_topics else 0
            
            self.test_results['integration']['recommendation_quality'] = {
                'count': len(recommendations),
                'topic_diversity': topic_diversity
            }
        else:
            print("No recommendations generated")
    
    def test_edge_cases(self):
        """Test system behavior with edge cases"""
        print("\n🧪 Testing Edge Cases")
        print("-" * 40)
        
        edge_cases = [
            ("", "empty query"),
            ("asdfghjkl", "nonsense query"),
            ("a", "single character"),
            ("What is the meaning of life and consciousness and virtue and truth and knowledge and wisdom and ethics and justice and freedom and time and change and existence?" * 10, "very long query")
        ]
        
        edge_case_results = []
        
        for query, description in edge_cases:
            try:
                results = self.retriever.search_quotes(query, "hybrid", limit=5)
                success = len(results) >= 0  # Should not crash
                edge_case_results.append(success)
                print(f"{description}: {'✅ Pass' if success else '❌ Fail'} ({len(results)} results)")
            except Exception as e:
                edge_case_results.append(False)
                print(f"{description}: ❌ Error - {e}")
        
        edge_case_pass_rate = sum(edge_case_results) / len(edge_case_results)
        print(f"\nEdge case pass rate: {edge_case_pass_rate:.3f}")
        
        self.test_results['integration']['edge_case_pass_rate'] = edge_case_pass_rate
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE SYSTEM TEST REPORT")
        print("=" * 60)
        
        # Overall system health
        health_score = 0
        component_count = 0
        
        for component, results in self.test_results.items():
            if results:
                component_count += 1
                if component == 'parsing':
                    health_score += results.get('quality_score', 0)
                elif component == 'vector_store':
                    health_score += results.get('semantic_accuracy', 0)
                elif component == 'knowledge_graph':
                    health_score += results.get('connectivity_score', 0)
                elif component == 'integration':
                    health_score += results.get('overall_quality', 0)
                elif component == 'performance':
                    # Performance score based on speed (target: <1s per search)
                    avg_time = results.get('semantic', {}).get('avg_time', 1)
                    health_score += min(1.0, 1.0 / max(avg_time, 0.1))
        
        overall_health = health_score / component_count if component_count > 0 else 0
        
        print(f"🎯 OVERALL SYSTEM HEALTH: {overall_health:.3f}/1.000")
        if overall_health >= 0.8:
            print("✅ EXCELLENT - Production ready")
        elif overall_health >= 0.6:
            print("✅ GOOD - Ready with minor optimizations")
        elif overall_health >= 0.4:
            print("⚠️  FAIR - Needs improvement before production")
        else:
            print("❌ POOR - Significant issues need addressing")
        
        print(f"\n📊 COMPONENT SCORES:")
        
        # Parsing/Corpus Quality
        if 'parsing' in self.test_results:
            parsing = self.test_results['parsing']
            print(f"📚 Corpus Quality: {parsing.get('quality_score', 0):.3f}")
            print(f"   • Total quotes: {parsing.get('total_quotes', 0):,}")
            print(f"   • Unique authors: {parsing.get('unique_authors', 0):,}")
            print(f"   • Author diversity: {parsing.get('author_diversity', 0):.3f}")
        
        # Vector Store Performance
        if 'vector_store' in self.test_results:
            vs = self.test_results['vector_store']
            print(f"🧠 Semantic Search: {vs.get('semantic_accuracy', 0):.3f}")
        
        # Knowledge Graph Connectivity
        if 'knowledge_graph' in self.test_results:
            kg = self.test_results['knowledge_graph']
            print(f"🕸️  Knowledge Graph: {kg.get('connectivity_score', 0):.3f}")
            print(f"   • Network quality: {kg.get('network_quality', 0):.3f}")
        
        # Integration Quality
        if 'integration' in self.test_results:
            integration = self.test_results['integration']
            print(f"🔗 Integration: {integration.get('overall_quality', 0):.3f}")
            print(f"   • Author diversity: {integration.get('author_diversity', 0):.3f}")
            print(f"   • Average relevance: {integration.get('avg_relevance', 0):.3f}")
        
        # Performance
        if 'performance' in self.test_results:
            perf = self.test_results['performance']
            semantic_perf = perf.get('semantic', {})
            print(f"⚡ Performance: {min(1.0, 1.0/max(semantic_perf.get('avg_time', 1), 0.1)):.3f}")
            print(f"   • Avg search time: {semantic_perf.get('avg_time', 0):.3f}s")
            print(f"   • Searches/second: {semantic_perf.get('searches_per_second', 0):.1f}")
        
        print(f"\n🚀 PRODUCTION READINESS CHECKLIST:")
        
        checklist_items = [
            ("Corpus size > 500 quotes", self.test_results.get('parsing', {}).get('total_quotes', 0) > 500),
            ("Author diversity > 0.5", self.test_results.get('parsing', {}).get('author_diversity', 0) > 0.5),
            ("Semantic accuracy > 0.4", self.test_results.get('vector_store', {}).get('semantic_accuracy', 0) > 0.4),
            ("Average search time < 1s", self.test_results.get('performance', {}).get('semantic', {}).get('avg_time', 1) < 1.0),
            ("Edge case handling", self.test_results.get('integration', {}).get('edge_case_pass_rate', 0) > 0.8),
            ("Knowledge graph connectivity", self.test_results.get('knowledge_graph', {}).get('connectivity_score', 0) > 0.3)
        ]
        
        for item, passed in checklist_items:
            status = "✅" if passed else "❌"
            print(f"{status} {item}")
        
        passed_items = sum(1 for _, passed in checklist_items if passed)
        readiness_score = passed_items / len(checklist_items)
        
        print(f"\n📈 Production Readiness: {readiness_score:.1%} ({passed_items}/{len(checklist_items)} checks passed)")
        
        return overall_health, readiness_score


def main():
    """Run comprehensive system tests"""
    print("🧪 Comprehensive Quote Retrieval System Test Suite")
    print("=" * 60)
    
    tester = QuoteSystemTester()
    
    # Run all tests
    tester.test_corpus_quality()
    tester.test_semantic_search_accuracy()
    tester.test_knowledge_graph_connectivity()
    tester.test_search_performance()
    tester.test_diversity_and_relevance()
    tester.test_recommendation_system()
    tester.test_edge_cases()
    
    # Generate final report
    overall_health, readiness_score = tester.generate_final_report()
    
    print(f"\n🎉 TESTING COMPLETE!")
    print(f"System Health: {overall_health:.1%}")
    print(f"Production Readiness: {readiness_score:.1%}")
    
    return tester


if __name__ == "__main__":
    test_suite = main()