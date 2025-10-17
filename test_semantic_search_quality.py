#!/usr/bin/env python3
"""
Semantic Search Quality Testing - Phase 7A-4

Tests the quality and effectiveness of semantic search on the enhanced philosophical quotes corpus.
Validates search relevance, diversity, coverage, and production readiness.

Features:
- Search relevance evaluation with philosophical concepts
- Diversity analysis across search results  
- Coverage testing for major philosophical domains
- Performance benchmarking for production use
- Quality metrics and scoring
"""

import json
import time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set
import sys
import os

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from retrieval.quote_retriever import QuoteRetriever
    from utils.llm_client import LLMClient
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Running without semantic search - using basic text matching")

class SemanticSearchQualityTester:
    """Tests semantic search quality on philosophical quotes corpus"""
    
    def __init__(self):
        self.test_queries = {
            # Metaphysical concepts
            'existence': [
                "What is the nature of being and existence?",
                "How do we understand reality and what exists?",
                "What does it mean to be authentic?",
                "The relationship between essence and existence"
            ],
            
            # Epistemological queries
            'knowledge': [
                "How do we acquire true knowledge?",
                "What is the difference between belief and knowledge?",
                "Can we know absolute truth?",
                "The limits of human understanding"
            ],
            
            # Ethical inquiries
            'ethics': [
                "What makes an action morally right?",
                "How should we live a good life?",
                "What is justice and fairness?",
                "The nature of virtue and character"
            ],
            
            # Political philosophy
            'politics': [
                "What is the ideal form of government?",
                "The balance between freedom and order",
                "Rights and responsibilities in society",
                "The nature of political authority"
            ],
            
            # Existential themes
            'meaning': [
                "What is the meaning of life?",
                "How do we find purpose in existence?",
                "Dealing with suffering and mortality",
                "The search for authentic living"
            ],
            
            # Eastern wisdom
            'eastern': [
                "The path to enlightenment and awakening",
                "Balance and harmony in life",
                "Non-attachment and letting go",
                "Mindfulness and present moment awareness"
            ],
            
            # Aesthetic philosophy
            'beauty': [
                "What is the nature of beauty?",
                "The relationship between art and truth",
                "Aesthetic experience and judgment",
                "Creativity and artistic expression"
            ],
            
            # Philosophy of mind
            'consciousness': [
                "The nature of consciousness and awareness",
                "The mind-body relationship",
                "Free will and determinism",
                "Personal identity over time"
            ]
        }
        
        self.quality_criteria = {
            'relevance': 0.25,    # How relevant are results to query
            'diversity': 0.25,    # Diversity of philosophical perspectives  
            'coverage': 0.20,     # Coverage of different traditions/eras
            'quality': 0.15,      # Overall quote quality scores
            'coherence': 0.15     # Thematic coherence of results
        }
        
        # Load corpus for analysis
        self.corpus = self._load_corpus()
        self.corpus_topics = self._extract_all_topics()
        
        # Initialize retriever if available
        try:
            self.retriever = QuoteRetriever()
            self.has_semantic_search = True
            print("✅ Semantic search enabled")
        except:
            self.retriever = None  
            self.has_semantic_search = False
            print("⚠️  Semantic search not available - using text matching")
    
    def _load_corpus(self) -> List[Dict]:
        """Load the enhanced philosophical quotes corpus"""
        corpus_path = Path("data/philosophical_quotes.jsonl")
        quotes = []
        
        if corpus_path.exists():
            with open(corpus_path, 'r', encoding='utf-8') as f:
                for line in f:
                    quotes.append(json.loads(line))
        
        return quotes
    
    def _extract_all_topics(self) -> Set[str]:
        """Extract all unique topics from corpus"""
        all_topics = set()
        for quote in self.corpus:
            all_topics.update(quote.get('topics', []))
        return all_topics
    
    def search_quotes(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for quotes using available method"""
        
        if self.has_semantic_search:
            try:
                # Use semantic search
                results = self.retriever.search_quotes(
                    query=query,
                    limit=limit,
                    diversity_threshold=0.7
                )
                return results
            except Exception as e:
                print(f"⚠️  Semantic search failed: {e}")
                return self._fallback_text_search(query, limit)
        else:
            return self._fallback_text_search(query, limit)
    
    def _fallback_text_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Fallback text-based search"""
        
        query_words = set(query.lower().split())
        scored_quotes = []
        
        for quote in self.corpus:
            # Simple text matching score
            quote_words = set(quote['quote'].lower().split())
            topic_words = set(word.lower() for word in quote.get('topics', []))
            
            # Calculate relevance score
            text_overlap = len(query_words.intersection(quote_words))
            topic_overlap = len(query_words.intersection(topic_words))
            
            score = text_overlap + (topic_overlap * 2)  # Weight topics higher
            
            if score > 0:
                scored_quotes.append((score, quote))
        
        # Sort by score and return top results
        scored_quotes.sort(reverse=True, key=lambda x: x[0])
        return [quote for _, quote in scored_quotes[:limit]]
    
    def evaluate_search_relevance(self, query: str, results: List[Dict]) -> float:
        """Evaluate how relevant search results are to the query"""
        
        if not results:
            return 0.0
        
        query_words = set(query.lower().split())
        relevance_scores = []
        
        for quote in results:
            # Check text relevance
            quote_words = set(quote['quote'].lower().split())
            text_relevance = len(query_words.intersection(quote_words)) / len(query_words)
            
            # Check topic relevance
            quote_topics = set(topic.lower() for topic in quote.get('topics', []))
            topic_relevance = len(query_words.intersection(quote_topics)) / len(query_words)
            
            # Combined relevance (weighted toward topics)
            combined_relevance = (text_relevance * 0.4) + (topic_relevance * 0.6)
            relevance_scores.append(combined_relevance)
        
        return sum(relevance_scores) / len(relevance_scores)
    
    def evaluate_result_diversity(self, results: List[Dict]) -> float:
        """Evaluate diversity of philosophical perspectives in results"""
        
        if not results:
            return 0.0
        
        # Check era diversity
        eras = [quote.get('era', 'unknown') for quote in results]
        era_diversity = len(set(eras)) / min(len(results), 4)  # Max 4 eras
        
        # Check tradition diversity  
        traditions = [quote.get('tradition', 'unknown') for quote in results]
        tradition_diversity = len(set(traditions)) / min(len(results), 3)  # Max 3 traditions
        
        # Check author diversity
        authors = [quote.get('author', 'unknown') for quote in results]
        author_diversity = len(set(authors)) / len(results)
        
        # Check topic diversity
        all_topics = [topic for quote in results for topic in quote.get('topics', [])]
        unique_topics = len(set(all_topics))
        topic_diversity = min(unique_topics / (len(results) * 2), 1.0)  # Expect ~2 topics per quote
        
        return (era_diversity + tradition_diversity + author_diversity + topic_diversity) / 4
    
    def evaluate_coverage(self, all_results: Dict[str, List[Dict]]) -> float:
        """Evaluate how well search covers different philosophical domains"""
        
        covered_topics = set()
        covered_eras = set()
        covered_traditions = set()
        
        for domain_results in all_results.values():
            for quote in domain_results:
                covered_topics.update(quote.get('topics', []))
                covered_eras.add(quote.get('era', 'unknown'))
                covered_traditions.add(quote.get('tradition', 'unknown'))
        
        # Calculate coverage ratios
        topic_coverage = len(covered_topics) / len(self.corpus_topics)
        era_coverage = len(covered_eras) / 4  # ancient, modern, contemporary, mixed
        tradition_coverage = len(covered_traditions) / 3  # western, eastern, other
        
        return (topic_coverage + era_coverage + tradition_coverage) / 3
    
    def evaluate_result_quality(self, results: List[Dict]) -> float:
        """Evaluate overall quality of search results"""
        
        if not results:
            return 0.0
        
        quality_scores = [quote.get('quality_score', 0.5) for quote in results]
        return sum(quality_scores) / len(quality_scores)
    
    def evaluate_thematic_coherence(self, results: List[Dict]) -> float:
        """Evaluate thematic coherence of search results"""
        
        if len(results) < 2:
            return 1.0
        
        # Collect all topics from results
        all_topics = [topic for quote in results for topic in quote.get('topics', [])]
        topic_counts = Counter(all_topics)
        
        # Calculate coherence based on topic overlap
        total_topics = len(all_topics)
        if total_topics == 0:
            return 0.0
        
        # Measure how much topics are shared across results
        shared_topic_ratio = sum(count for count in topic_counts.values() if count > 1) / total_topics
        
        return min(shared_topic_ratio * 2, 1.0)  # Scale up to make 50% sharing = perfect score
    
    def run_comprehensive_search_test(self) -> Dict:
        """Run comprehensive semantic search quality evaluation"""
        
        print("\n🔍 Running Comprehensive Search Quality Evaluation")
        print("Testing search relevance, diversity, coverage, and coherence")
        print("=" * 65)
        
        all_results = {}
        domain_scores = {}
        
        # Test each philosophical domain
        for domain, queries in self.test_queries.items():
            print(f"\n📚 Testing {domain.upper()} domain ({len(queries)} queries)...")
            
            domain_results = []
            domain_metrics = {
                'relevance': [],
                'diversity': [],
                'quality': [],
                'coherence': []
            }
            
            for i, query in enumerate(queries):
                print(f"   Query {i+1}: {query[:50]}...")
                
                # Perform search
                start_time = time.time()
                results = self.search_quotes(query, limit=8)
                search_time = time.time() - start_time
                
                if results:
                    # Evaluate this query's results
                    relevance = self.evaluate_search_relevance(query, results)
                    diversity = self.evaluate_result_diversity(results)
                    quality = self.evaluate_result_quality(results)
                    coherence = self.evaluate_thematic_coherence(results)
                    
                    domain_metrics['relevance'].append(relevance)
                    domain_metrics['diversity'].append(diversity)
                    domain_metrics['quality'].append(quality)
                    domain_metrics['coherence'].append(coherence)
                    
                    domain_results.extend(results)
                    
                    print(f"      Found {len(results)} quotes in {search_time:.3f}s")
                    print(f"      Relevance: {relevance:.3f}, Diversity: {diversity:.3f}")
                else:
                    print(f"      No results found")
            
            # Calculate domain averages
            if domain_metrics['relevance']:
                domain_score = {
                    'relevance': np.mean(domain_metrics['relevance']),
                    'diversity': np.mean(domain_metrics['diversity']),
                    'quality': np.mean(domain_metrics['quality']),
                    'coherence': np.mean(domain_metrics['coherence']),
                    'result_count': len(domain_results)
                }
                
                domain_scores[domain] = domain_score
                all_results[domain] = domain_results
                
                print(f"   Domain Score: {domain_score['relevance']:.3f} relevance, {domain_score['diversity']:.3f} diversity")
        
        # Calculate overall coverage
        coverage_score = self.evaluate_coverage(all_results)
        
        # Calculate weighted overall score
        overall_metrics = {
            'relevance': np.mean([score['relevance'] for score in domain_scores.values()]),
            'diversity': np.mean([score['diversity'] for score in domain_scores.values()]),
            'quality': np.mean([score['quality'] for score in domain_scores.values()]),
            'coherence': np.mean([score['coherence'] for score in domain_scores.values()]),
            'coverage': coverage_score
        }
        
        # Calculate final weighted score
        final_score = (
            overall_metrics['relevance'] * self.quality_criteria['relevance'] +
            overall_metrics['diversity'] * self.quality_criteria['diversity'] +
            overall_metrics['coverage'] * self.quality_criteria['coverage'] +
            overall_metrics['quality'] * self.quality_criteria['quality'] +
            overall_metrics['coherence'] * self.quality_criteria['coherence']
        )
        
        return {
            'overall_score': final_score,
            'overall_metrics': overall_metrics,
            'domain_scores': domain_scores,
            'total_queries': sum(len(queries) for queries in self.test_queries.values()),
            'successful_searches': len([d for d in domain_scores.values() if d['result_count'] > 0])
        }
    
    def run_performance_benchmark(self) -> Dict:
        """Run performance benchmarks for production readiness"""
        
        print("\n⚡ Running Performance Benchmarks")
        print("Testing search speed and scalability for production use")
        print("=" * 55)
        
        benchmark_queries = [
            "wisdom and truth",
            "meaning of life", 
            "ethical behavior",
            "nature of reality",
            "human consciousness"
        ]
        
        search_times = []
        
        for query in benchmark_queries:
            start_time = time.time()
            results = self.search_quotes(query, limit=10)
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            print(f"   '{query}': {len(results)} results in {search_time:.3f}s")
        
        avg_search_time = np.mean(search_times)
        max_search_time = max(search_times)
        
        # Performance thresholds for production
        performance_grade = 'A'
        if avg_search_time > 0.5:
            performance_grade = 'B'
        if avg_search_time > 1.0:
            performance_grade = 'C'
        if avg_search_time > 2.0:
            performance_grade = 'D'
        
        return {
            'average_search_time': avg_search_time,
            'max_search_time': max_search_time,
            'performance_grade': performance_grade,
            'searches_per_second': 1.0 / avg_search_time if avg_search_time > 0 else 0,
            'production_ready': avg_search_time < 1.0
        }

def main():
    """Phase 7A-4: Test semantic search quality with expanded corpus"""
    
    print("🧪 Phase 7A-4: Semantic Search Quality Testing")
    print("Evaluating search quality and production readiness of enhanced corpus")
    print("=" * 70)
    
    tester = SemanticSearchQualityTester()
    
    # Corpus overview
    print(f"📊 Testing corpus: {len(tester.corpus)} quotes")
    print(f"📚 Unique topics: {len(tester.corpus_topics)}")
    print(f"🔍 Search method: {'Semantic search' if tester.has_semantic_search else 'Text matching'}")
    
    # Run comprehensive quality tests
    quality_results = tester.run_comprehensive_search_test()
    
    # Run performance benchmarks
    performance_results = tester.run_performance_benchmark()
    
    # Report results
    print(f"\n📊 COMPREHENSIVE QUALITY RESULTS")
    print(f"=" * 45)
    print(f"🎯 Overall Score: {quality_results['overall_score']:.3f}/1.000")
    print(f"📈 Relevance: {quality_results['overall_metrics']['relevance']:.3f}")
    print(f"🌈 Diversity: {quality_results['overall_metrics']['diversity']:.3f}")
    print(f"📚 Coverage: {quality_results['overall_metrics']['coverage']:.3f}")
    print(f"⭐ Quality: {quality_results['overall_metrics']['quality']:.3f}")
    print(f"🔗 Coherence: {quality_results['overall_metrics']['coherence']:.3f}")
    
    print(f"\n⚡ PERFORMANCE RESULTS")
    print(f"=" * 25)
    print(f"🕒 Average search time: {performance_results['average_search_time']:.3f}s")
    print(f"🚀 Searches per second: {performance_results['searches_per_second']:.1f}")
    print(f"📊 Performance grade: {performance_results['performance_grade']}")
    print(f"🏭 Production ready: {'✅ Yes' if performance_results['production_ready'] else '❌ No'}")
    
    print(f"\n📋 DOMAIN PERFORMANCE")
    print(f"=" * 25)
    for domain, scores in quality_results['domain_scores'].items():
        print(f"{domain.capitalize():12}: {scores['relevance']:.3f} relevance, {scores['result_count']:3d} results")
    
    # Quality assessment
    overall_score = quality_results['overall_score']
    if overall_score >= 0.8:
        quality_grade = "Excellent"
        emoji = "🏆"
    elif overall_score >= 0.7:
        quality_grade = "Good"
        emoji = "✅"
    elif overall_score >= 0.6:
        quality_grade = "Acceptable"
        emoji = "👍"
    else:
        quality_grade = "Needs Improvement"
        emoji = "⚠️"
    
    print(f"\n{emoji} FINAL ASSESSMENT: {quality_grade}")
    print(f"📊 {quality_results['successful_searches']}/{quality_results['total_queries']} successful searches")
    
    if overall_score >= 0.7 and performance_results['production_ready']:
        print(f"🌟 CORPUS IS PRODUCTION-READY!")
        print(f"🚀 Ready for deployment in Intellectual Gravitas system")
        print(f"✅ Phase 7A-4 COMPLETE - Semantic search quality validated")
        print(f"📋 Next: Phase 8 - End-to-end integration validation")
    else:
        print(f"⚠️  Corpus needs further optimization before production deployment")
        recommendations = []
        if quality_results['overall_metrics']['relevance'] < 0.7:
            recommendations.append("Improve search relevance matching")
        if quality_results['overall_metrics']['diversity'] < 0.6:
            recommendations.append("Increase philosophical diversity")
        if not performance_results['production_ready']:
            recommendations.append("Optimize search performance")
        
        print(f"📋 Recommendations: {', '.join(recommendations)}")
    
    return quality_results, performance_results

if __name__ == "__main__":
    quality_results, performance_results = main()