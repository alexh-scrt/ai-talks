#!/usr/bin/env python3
"""
Enhanced Quote Retrieval System

Integrates knowledge graph, vector store, and semantic search for 
advanced philosophical quote discovery and recommendation.
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from build_knowledge_graph import QuoteKnowledgeGraph
    from build_vector_store import QuoteVectorStore
except ImportError:
    logger.warning("Could not import custom modules - ensure they're in the same directory")


class EnhancedQuoteRetriever:
    """
    Advanced quote retrieval system combining knowledge graph traversal
    and vector similarity search for optimal quote discovery.
    """
    
    def __init__(self,
                 knowledge_graph_path: str = "quote_knowledge_graph.pkl",
                 vector_store_path: str = "quote_vector_store.pkl"):
        """
        Initialize enhanced quote retriever
        
        Args:
            knowledge_graph_path: Path to saved knowledge graph
            vector_store_path: Path to saved vector store
        """
        self.kg_path = Path(knowledge_graph_path)
        self.vs_path = Path(vector_store_path)
        
        # Core components
        self.knowledge_graph: Optional[QuoteKnowledgeGraph] = None
        self.vector_store: Optional[QuoteVectorStore] = None
        
        # Retrieval history and diversity tracking
        self.used_quotes: set = set()
        self.used_authors: List[str] = []
        self.search_history: List[Dict] = []
        
        # Configuration
        self.config = {
            'diversity_weight': 0.3,
            'knowledge_graph_weight': 0.4,
            'semantic_weight': 0.6,
            'author_penalty': 0.1,  # Penalty for recently used authors
            'max_same_author': 2,   # Max quotes from same author in results
            'min_similarity': 0.3   # Minimum semantic similarity threshold
        }
        
        # Load components
        self._load_components()
    
    def _load_components(self):
        """Load knowledge graph and vector store"""
        try:
            # Load knowledge graph
            if self.kg_path.exists():
                self.knowledge_graph = QuoteKnowledgeGraph()
                self.knowledge_graph.load_graph(str(self.kg_path))
                logger.info("📊 Knowledge graph loaded successfully")
            else:
                logger.warning(f"Knowledge graph not found: {self.kg_path}")
            
            # Load vector store
            if self.vs_path.exists():
                self.vector_store = QuoteVectorStore()
                self.vector_store.load_vector_store(str(self.vs_path))
                logger.info("🧠 Vector store loaded successfully")
            else:
                logger.warning(f"Vector store not found: {self.vs_path}")
                
        except Exception as e:
            logger.error(f"Error loading components: {e}")
    
    def search_quotes(self, 
                     query: str,
                     search_mode: str = "hybrid",
                     limit: int = 10,
                     author: Optional[str] = None,
                     topic: Optional[str] = None,
                     era: Optional[str] = None,
                     tradition: Optional[str] = None) -> List[Dict]:
        """
        Enhanced quote search with multiple modes
        
        Args:
            query: Search query text
            search_mode: "semantic", "graph", "hybrid", "author", "topic"
            limit: Maximum number of results
            author: Filter by specific author
            topic: Filter by specific topic
            era: Filter by era (ancient, modern, contemporary)
            tradition: Filter by tradition (western, eastern, other)
            
        Returns:
            List of quote dictionaries with enhanced metadata
        """
        logger.info(f"🔍 Searching quotes: '{query}' (mode: {search_mode})")
        
        if search_mode == "semantic":
            results = self._semantic_search(query, limit)
        elif search_mode == "graph":
            results = self._graph_search(query, limit)
        elif search_mode == "hybrid":
            results = self._hybrid_search(query, limit)
        elif search_mode == "author":
            results = self._author_search(author or query, limit)
        elif search_mode == "topic":
            results = self._topic_search(topic or query, limit)
        else:
            results = self._hybrid_search(query, limit)
        
        # Apply filters
        filtered_results = self._apply_filters(results, author, topic, era, tradition)
        
        # Apply diversity and scoring
        final_results = self._apply_diversity_scoring(filtered_results, limit)
        
        # Track search
        self._track_search(query, search_mode, final_results)
        
        return final_results[:limit]
    
    def _semantic_search(self, query: str, limit: int) -> List[Dict]:
        """Perform pure semantic vector search"""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.semantic_search(
                query, 
                search_type="both",
                top_k=limit * 2,
                min_similarity=self.config['min_similarity']
            )
            
            enhanced_results = []
            for quote, similarity in results:
                quote['retrieval_score'] = float(similarity)
                quote['retrieval_method'] = 'semantic'
                enhanced_results.append(quote)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []
    
    def _graph_search(self, query: str, limit: int) -> List[Dict]:
        """Perform knowledge graph-based search"""
        if not self.knowledge_graph or not self.vector_store:
            return []
        
        try:
            # Extract keywords from query for graph traversal
            keywords = query.lower().split()
            results = []
            
            # Search by topics mentioned in query
            topic_keywords = ['knowledge', 'truth', 'existence', 'consciousness', 
                            'virtue', 'freedom', 'time', 'change', 'meaning', 'justice']
            
            for keyword in keywords:
                for topic in topic_keywords:
                    if keyword in topic or topic in keyword:
                        topic_quotes = self.knowledge_graph.get_topic_quotes(topic, limit)
                        for quote_id in topic_quotes:
                            quote_node_id = f"QUOTE_{quote_id.split('::')[1]}"  # Extract quote ID
                            if self.knowledge_graph.graph.has_node(quote_node_id):
                                quote_data = self.knowledge_graph.graph.nodes[quote_node_id]
                                quote_dict = {
                                    'id': quote_data['id'],
                                    'quote': quote_data['text'],
                                    'author': quote_data['author'],
                                    'meaning': quote_data['meaning'],
                                    'topics': quote_data['topics'],
                                    'era': quote_data['era'],
                                    'tradition': quote_data['tradition'],
                                    'retrieval_score': 0.8,  # High score for graph matches
                                    'retrieval_method': 'graph'
                                }
                                results.append(quote_dict)
            
            return results[:limit * 2]
            
        except Exception as e:
            logger.error(f"Graph search error: {e}")
            return []
    
    def _hybrid_search(self, query: str, limit: int) -> List[Dict]:
        """Combine semantic and graph search results"""
        semantic_results = self._semantic_search(query, limit)
        graph_results = self._graph_search(query, limit)
        
        # Combine and weight results
        combined_results = []
        seen_ids = set()
        
        # Add semantic results with weighted scores
        for quote in semantic_results:
            if quote['id'] not in seen_ids:
                quote['retrieval_score'] = (
                    quote['retrieval_score'] * self.config['semantic_weight']
                )
                combined_results.append(quote)
                seen_ids.add(quote['id'])
        
        # Add graph results with weighted scores
        for quote in graph_results:
            if quote['id'] not in seen_ids:
                quote['retrieval_score'] = (
                    quote['retrieval_score'] * self.config['knowledge_graph_weight']
                )
                combined_results.append(quote)
                seen_ids.add(quote['id'])
            else:
                # Boost score if found in both methods
                for existing_quote in combined_results:
                    if existing_quote['id'] == quote['id']:
                        existing_quote['retrieval_score'] += (
                            quote['retrieval_score'] * self.config['knowledge_graph_weight'] * 0.5
                        )
                        existing_quote['retrieval_method'] = 'hybrid'
                        break
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x['retrieval_score'], reverse=True)
        return combined_results
    
    def _author_search(self, author: str, limit: int) -> List[Dict]:
        """Search quotes by specific author"""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.search_by_author(author, "", limit)
            enhanced_results = []
            
            for quote, score in results:
                quote['retrieval_score'] = float(score)
                quote['retrieval_method'] = 'author'
                enhanced_results.append(quote)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Author search error: {e}")
            return []
    
    def _topic_search(self, topic: str, limit: int) -> List[Dict]:
        """Search quotes by specific topic"""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.search_by_topic(topic, "", limit)
            enhanced_results = []
            
            for quote, score in results:
                quote['retrieval_score'] = float(score)
                quote['retrieval_method'] = 'topic'
                enhanced_results.append(quote)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Topic search error: {e}")
            return []
    
    def _apply_filters(self, 
                      results: List[Dict],
                      author: Optional[str] = None,
                      topic: Optional[str] = None,
                      era: Optional[str] = None,
                      tradition: Optional[str] = None) -> List[Dict]:
        """Apply metadata filters to results"""
        filtered = results
        
        if author:
            filtered = [r for r in filtered if author.lower() in r.get('author', '').lower()]
        
        if topic:
            filtered = [r for r in filtered if topic in r.get('topics', [])]
        
        if era:
            filtered = [r for r in filtered if r.get('era') == era]
        
        if tradition:
            filtered = [r for r in filtered if r.get('tradition') == tradition]
        
        return filtered
    
    def _apply_diversity_scoring(self, results: List[Dict], limit: int) -> List[Dict]:
        """Apply diversity penalties and boost scores"""
        if not results:
            return []
        
        # Track author counts in current results
        author_counts = {}
        final_results = []
        
        for quote in results:
            author = quote.get('author', 'Unknown')
            
            # Author diversity penalty
            author_penalty = 0
            if author in author_counts:
                author_penalty = self.config['author_penalty'] * author_counts[author]
            
            # Penalty for recently used authors
            if author in self.used_authors[-5:]:  # Last 5 authors
                author_penalty += self.config['author_penalty']
            
            # Penalty for previously used quotes
            quote_penalty = 0
            if quote['id'] in self.used_quotes:
                quote_penalty = 0.3
            
            # Calculate final score
            final_score = quote['retrieval_score'] - author_penalty - quote_penalty
            quote['final_score'] = max(final_score, 0.0)
            
            # Add to results if author limit not exceeded
            current_author_count = author_counts.get(author, 0)
            if current_author_count < self.config['max_same_author']:
                final_results.append(quote)
                author_counts[author] = current_author_count + 1
        
        # Sort by final score
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        return final_results
    
    def find_similar_quotes(self, quote_id: str, limit: int = 5) -> List[Dict]:
        """Find quotes similar to a given quote"""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.find_similar_quotes(quote_id, limit)
            enhanced_results = []
            
            for quote, similarity in results:
                quote['retrieval_score'] = float(similarity)
                quote['retrieval_method'] = 'similarity'
                enhanced_results.append(quote)
            
            return self._apply_diversity_scoring(enhanced_results, limit)
            
        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            return []
    
    def get_author_network(self, author: str, max_quotes: int = 10) -> Dict:
        """Get author's quote network with related authors and topics"""
        if not self.knowledge_graph or not self.vector_store:
            return {}
        
        try:
            # Get author's quotes
            author_quotes = self.vector_store.search_by_author(author, "", max_quotes)
            
            # Get knowledge graph network
            network = self.knowledge_graph.get_author_network(author, depth=2)
            
            # Extract related authors and topics
            related_authors = set()
            related_topics = set()
            
            for node_id, data in network.nodes(data=True):
                if data.get('type') == 'author' and data['name'] != author:
                    related_authors.add(data['name'])
                elif data.get('type') == 'topic':
                    related_topics.add(data['name'])
            
            return {
                'author': author,
                'quotes': [q[0] for q in author_quotes],
                'related_authors': list(related_authors)[:5],
                'related_topics': list(related_topics)[:5],
                'network_size': network.number_of_nodes()
            }
            
        except Exception as e:
            logger.error(f"Author network error: {e}")
            return {}
    
    def _track_search(self, query: str, mode: str, results: List[Dict]):
        """Track search for session management"""
        # Track used quotes and authors
        for quote in results:
            self.used_quotes.add(quote['id'])
            author = quote.get('author', 'Unknown')
            if author not in self.used_authors:
                self.used_authors.append(author)
        
        # Limit history size
        if len(self.used_authors) > 20:
            self.used_authors = self.used_authors[-20:]
        
        # Track search history
        search_record = {
            'query': query,
            'mode': mode,
            'result_count': len(results),
            'top_scores': [r.get('final_score', 0) for r in results[:3]]
        }
        self.search_history.append(search_record)
        
        if len(self.search_history) > 50:
            self.search_history = self.search_history[-50:]
    
    def get_recommendations(self, limit: int = 5) -> List[Dict]:
        """Get personalized recommendations based on search history"""
        if not self.search_history or not self.vector_store:
            return []
        
        # Extract topics from search history
        historical_topics = []
        for search in self.search_history[-10:]:  # Last 10 searches
            query = search['query'].lower()
            # Simple topic extraction
            topic_keywords = ['knowledge', 'truth', 'existence', 'consciousness', 
                            'virtue', 'freedom', 'time', 'change', 'meaning', 'justice']
            for topic in topic_keywords:
                if topic in query:
                    historical_topics.append(topic)
        
        if not historical_topics:
            return []
        
        # Get quotes from most frequent topics
        from collections import Counter
        top_topics = Counter(historical_topics).most_common(3)
        
        recommendations = []
        for topic, _ in top_topics:
            topic_quotes = self.vector_store.search_by_topic(topic, "", limit)
            for quote, score in topic_quotes:
                if quote['id'] not in self.used_quotes:
                    quote['retrieval_score'] = float(score)
                    quote['retrieval_method'] = 'recommendation'
                    recommendations.append(quote)
        
        return self._apply_diversity_scoring(recommendations, limit)
    
    def reset_session(self):
        """Reset session tracking"""
        self.used_quotes.clear()
        self.used_authors.clear()
        self.search_history.clear()
        logger.info("🔄 Session reset")
    
    def get_statistics(self) -> Dict:
        """Get retrieval system statistics"""
        stats = {
            'session_searches': len(self.search_history),
            'unique_quotes_seen': len(self.used_quotes),
            'unique_authors_seen': len(set(self.used_authors)),
            'available_components': []
        }
        
        if self.knowledge_graph:
            kg_stats = self.knowledge_graph.stats
            stats['knowledge_graph'] = kg_stats
            stats['available_components'].append('knowledge_graph')
        
        if self.vector_store:
            vs_stats = self.vector_store.stats
            stats['vector_store'] = vs_stats
            stats['available_components'].append('vector_store')
        
        return stats


def demo_enhanced_retrieval():
    """Demonstrate the enhanced quote retrieval system"""
    print("🚀 Enhanced Quote Retrieval System Demo")
    print("=" * 60)
    
    # Initialize retriever
    retriever = EnhancedQuoteRetriever()
    
    # Demo queries
    demo_queries = [
        ("What is the meaning of life?", "hybrid"),
        ("How do we find truth?", "semantic"),
        ("What is consciousness?", "graph"),
        ("wisdom", "topic")
    ]
    
    for query, mode in demo_queries:
        print(f"\n🔍 Query: '{query}' (mode: {mode})")
        print("-" * 40)
        
        results = retriever.search_quotes(query, mode, limit=3)
        
        for i, quote in enumerate(results, 1):
            score = quote.get('final_score', quote.get('retrieval_score', 0))
            method = quote.get('retrieval_method', 'unknown')
            print(f"{i}. [{score:.3f}|{method}] {quote['author']}")
            print(f"   \"{quote['quote'][:80]}...\"")
            print(f"   Topics: {', '.join(quote.get('topics', []))}")
    
    # Demo author network
    print(f"\n👥 Author Network: Albert Einstein")
    print("-" * 40)
    network = retriever.get_author_network("Albert Einstein")
    if network:
        print(f"Quotes: {len(network['quotes'])}")
        print(f"Related authors: {', '.join(network['related_authors'])}")
        print(f"Related topics: {', '.join(network['related_topics'])}")
    
    # Demo recommendations
    print(f"\n💡 Personalized Recommendations")
    print("-" * 40)
    recommendations = retriever.get_recommendations(3)
    for i, quote in enumerate(recommendations, 1):
        print(f"{i}. {quote['author']}: \"{quote['quote'][:60]}...\"")
    
    # Print statistics
    print(f"\n📊 System Statistics")
    print("-" * 40)
    stats = retriever.get_statistics()
    print(f"Session searches: {stats['session_searches']}")
    print(f"Unique quotes seen: {stats['unique_quotes_seen']}")
    print(f"Available components: {', '.join(stats['available_components'])}")
    
    return retriever


if __name__ == "__main__":
    demo_retriever = demo_enhanced_retrieval()