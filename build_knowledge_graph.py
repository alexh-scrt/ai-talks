#!/usr/bin/env python3
"""
Knowledge Graph Builder for Philosophical Quote Corpus

Builds a comprehensive knowledge graph with authors, quotes, topics, and relationships.
Enables graph-based traversal for enhanced quote discovery and semantic connections.
"""

import json
import networkx as nx
import pickle
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuoteKnowledgeGraph:
    """Builds and manages knowledge graph for philosophical quotes"""
    
    def __init__(self, corpus_path: str = "enhanced_philosophical_quotes.jsonl"):
        self.corpus_path = Path(corpus_path)
        self.graph = nx.MultiDiGraph()  # Directed graph with multiple edges
        
        # Node type prefixes for clarity
        self.prefixes = {
            'author': 'AUTH_',
            'quote': 'QUOTE_',
            'topic': 'TOPIC_',
            'field': 'FIELD_',
            'era': 'ERA_',
            'tradition': 'TRAD_'
        }
        
        # Statistics
        self.stats = {
            'authors': 0,
            'quotes': 0,
            'topics': 0,
            'fields': 0,
            'relationships': 0,
            'clusters': 0
        }
        
        # Caches for performance
        self.author_quotes: Dict[str, List[str]] = defaultdict(list)
        self.topic_quotes: Dict[str, List[str]] = defaultdict(list)
        self.quote_similarities: Dict[str, List[Tuple[str, float]]] = {}
    
    def load_quotes(self) -> List[Dict]:
        """Load quotes from JSONL corpus"""
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus not found: {self.corpus_path}")
        
        quotes = []
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    quotes.append(json.loads(line.strip()))
        
        logger.info(f"📚 Loaded {len(quotes)} quotes from corpus")
        return quotes
    
    def add_author_node(self, author: str, field: str, era: str, tradition: str):
        """Add author node with metadata"""
        node_id = f"{self.prefixes['author']}{author}"
        
        if not self.graph.has_node(node_id):
            self.graph.add_node(node_id, 
                               type='author',
                               name=author,
                               field=field,
                               era=era,
                               tradition=tradition,
                               quote_count=0)
            self.stats['authors'] += 1
    
    def add_quote_node(self, quote_data: Dict):
        """Add quote node with full metadata"""
        quote_id = quote_data['id']
        node_id = f"{self.prefixes['quote']}{quote_id}"
        
        self.graph.add_node(node_id,
                           type='quote',
                           id=quote_id,
                           text=quote_data['quote'],
                           author=quote_data['author'],
                           meaning=quote_data['meaning'],
                           word_count=quote_data['word_count'],
                           topics=quote_data['topics'],
                           era=quote_data['era'],
                           tradition=quote_data['tradition'])
        
        self.stats['quotes'] += 1
    
    def add_concept_node(self, concept: str, concept_type: str):
        """Add concept node (topic, field, era, tradition)"""
        node_id = f"{self.prefixes[concept_type]}{concept}"
        
        if not self.graph.has_node(node_id):
            self.graph.add_node(node_id,
                               type=concept_type,
                               name=concept,
                               quote_count=0,
                               author_count=0)
            
            if concept_type == 'topic':
                self.stats['topics'] += 1
            elif concept_type == 'field':
                self.stats['fields'] += 1
    
    def add_relationship(self, source: str, target: str, rel_type: str, weight: float = 1.0, **kwargs):
        """Add relationship between nodes"""
        self.graph.add_edge(source, target, 
                           relationship=rel_type,
                           weight=weight,
                           **kwargs)
        self.stats['relationships'] += 1
    
    def calculate_quote_similarity(self, quote1: Dict, quote2: Dict) -> float:
        """Calculate semantic similarity between quotes"""
        # Simple similarity based on shared topics and word overlap
        topics1 = set(quote1['topics'])
        topics2 = set(quote2['topics'])
        
        # Topic similarity
        topic_similarity = len(topics1 & topics2) / max(len(topics1 | topics2), 1)
        
        # Text similarity (simple word overlap)
        words1 = set(quote1['quote'].lower().split())
        words2 = set(quote2['quote'].lower().split())
        text_similarity = len(words1 & words2) / max(len(words1 | words2), 1)
        
        # Meaning similarity (keyword overlap)
        meaning_words1 = set(quote1['meaning'].lower().split())
        meaning_words2 = set(quote2['meaning'].lower().split())
        meaning_similarity = len(meaning_words1 & meaning_words2) / max(len(meaning_words1 | meaning_words2), 1)
        
        # Weighted combination
        similarity = (0.4 * topic_similarity + 0.3 * text_similarity + 0.3 * meaning_similarity)
        return similarity
    
    def find_author_influences(self, quotes: List[Dict]) -> Dict[str, List[Tuple[str, float]]]:
        """Find potential influences between authors based on similarity"""
        author_groups = defaultdict(list)
        
        # Group quotes by author
        for quote in quotes:
            author_groups[quote['author']].append(quote)
        
        influences = defaultdict(list)
        
        # Compare authors from different eras
        for author1, quotes1 in author_groups.items():
            for author2, quotes2 in author_groups.items():
                if author1 != author2:
                    # Calculate average similarity between authors' quotes
                    similarities = []
                    for q1 in quotes1[:5]:  # Sample first 5 quotes for performance
                        for q2 in quotes2[:5]:
                            sim = self.calculate_quote_similarity(q1, q2)
                            similarities.append(sim)
                    
                    if similarities:
                        avg_similarity = sum(similarities) / len(similarities)
                        if avg_similarity > 0.3:  # Threshold for influence
                            influences[author1].append((author2, avg_similarity))
        
        # Sort influences by strength
        for author in influences:
            influences[author].sort(key=lambda x: x[1], reverse=True)
            influences[author] = influences[author][:3]  # Top 3 influences
        
        return influences
    
    def build_graph(self):
        """Build complete knowledge graph from quotes"""
        logger.info("🏗️  Building knowledge graph from philosophical quotes...")
        
        # Load quotes
        quotes = self.load_quotes()
        
        # Track concepts
        all_topics = set()
        all_fields = set()
        all_eras = set()
        all_traditions = set()
        
        # First pass: Add all nodes
        logger.info("📊 Adding nodes to graph...")
        
        for quote in quotes:
            # Add quote node
            self.add_quote_node(quote)
            
            # Add author node
            self.add_author_node(quote['author'], quote['field'], 
                               quote['era'], quote['tradition'])
            
            # Track concepts
            all_topics.update(quote['topics'])
            all_fields.add(quote['field'])
            all_eras.add(quote['era'])
            all_traditions.add(quote['tradition'])
            
            # Update caches
            author_id = f"{self.prefixes['author']}{quote['author']}"
            quote_id = f"{self.prefixes['quote']}{quote['id']}"
            self.author_quotes[author_id].append(quote_id)
            
            for topic in quote['topics']:
                topic_id = f"{self.prefixes['topic']}{topic}"
                self.topic_quotes[topic_id].append(quote_id)
        
        # Add concept nodes
        for topic in all_topics:
            self.add_concept_node(topic, 'topic')
        for field in all_fields:
            self.add_concept_node(field, 'field')
        for era in all_eras:
            self.add_concept_node(era, 'era')
        for tradition in all_traditions:
            self.add_concept_node(tradition, 'tradition')
        
        # Second pass: Add relationships
        logger.info("🔗 Adding relationships to graph...")
        
        for quote in quotes:
            quote_id = f"{self.prefixes['quote']}{quote['id']}"
            author_id = f"{self.prefixes['author']}{quote['author']}"
            
            # Author-Quote relationship
            self.add_relationship(author_id, quote_id, 'authored', weight=1.0)
            
            # Quote-Topic relationships
            for topic in quote['topics']:
                topic_id = f"{self.prefixes['topic']}{topic}"
                self.add_relationship(quote_id, topic_id, 'relates_to', weight=1.0)
            
            # Quote-Field relationship
            field_id = f"{self.prefixes['field']}{quote['field']}"
            self.add_relationship(quote_id, field_id, 'belongs_to', weight=1.0)
            
            # Quote-Era relationship
            era_id = f"{self.prefixes['era']}{quote['era']}"
            self.add_relationship(quote_id, era_id, 'from_era', weight=1.0)
            
            # Quote-Tradition relationship
            tradition_id = f"{self.prefixes['tradition']}{quote['tradition']}"
            self.add_relationship(quote_id, tradition_id, 'from_tradition', weight=1.0)
        
        # Third pass: Add semantic similarities
        logger.info("🧠 Computing semantic similarities...")
        
        quote_list = list(quotes)
        for i, quote1 in enumerate(quote_list):
            if i % 50 == 0:
                logger.info(f"   Processing similarity for quote {i+1}/{len(quote_list)}")
            
            similarities = []
            quote1_id = f"{self.prefixes['quote']}{quote1['id']}"
            
            for j, quote2 in enumerate(quote_list[i+1:], i+1):
                similarity = self.calculate_quote_similarity(quote1, quote2)
                if similarity > 0.4:  # Threshold for semantic similarity
                    quote2_id = f"{self.prefixes['quote']}{quote2['id']}"
                    similarities.append((quote2_id, similarity))
                    
                    # Add bidirectional similarity edge
                    self.add_relationship(quote1_id, quote2_id, 'similar_to', 
                                       weight=similarity)
            
            # Cache top similarities
            similarities.sort(key=lambda x: x[1], reverse=True)
            self.quote_similarities[quote1_id] = similarities[:5]
        
        # Fourth pass: Add author influences
        logger.info("👥 Computing author influences...")
        influences = self.find_author_influences(quotes)
        
        for author1, influenced_by in influences.items():
            author1_id = f"{self.prefixes['author']}{author1}"
            for author2, strength in influenced_by:
                author2_id = f"{self.prefixes['author']}{author2}"
                self.add_relationship(author2_id, author1_id, 'influences', 
                                   weight=strength)
        
        # Update node statistics
        self._update_node_statistics()
        
        logger.info("✅ Knowledge graph construction complete!")
    
    def _update_node_statistics(self):
        """Update node statistics (quote counts, etc.)"""
        # Update author quote counts
        for author_id, quote_ids in self.author_quotes.items():
            if self.graph.has_node(author_id):
                self.graph.nodes[author_id]['quote_count'] = len(quote_ids)
        
        # Update topic quote counts
        for topic_id, quote_ids in self.topic_quotes.items():
            if self.graph.has_node(topic_id):
                self.graph.nodes[topic_id]['quote_count'] = len(quote_ids)
                # Count unique authors for this topic
                authors = set()
                for quote_id in quote_ids:
                    if self.graph.has_node(quote_id):
                        authors.add(self.graph.nodes[quote_id]['author'])
                self.graph.nodes[topic_id]['author_count'] = len(authors)
    
    def get_author_quotes(self, author: str, limit: int = 10) -> List[str]:
        """Get quotes by a specific author"""
        author_id = f"{self.prefixes['author']}{author}"
        quote_ids = self.author_quotes.get(author_id, [])
        return quote_ids[:limit]
    
    def get_topic_quotes(self, topic: str, limit: int = 10) -> List[str]:
        """Get quotes related to a specific topic"""
        topic_id = f"{self.prefixes['topic']}{topic}"
        quote_ids = self.topic_quotes.get(topic_id, [])
        return quote_ids[:limit]
    
    def get_similar_quotes(self, quote_id: str, limit: int = 5) -> List[Tuple[str, float]]:
        """Get quotes similar to a given quote"""
        quote_node_id = f"{self.prefixes['quote']}{quote_id}"
        similarities = self.quote_similarities.get(quote_node_id, [])
        return similarities[:limit]
    
    def find_quote_path(self, quote1_id: str, quote2_id: str) -> Optional[List[str]]:
        """Find shortest path between two quotes"""
        try:
            node1 = f"{self.prefixes['quote']}{quote1_id}"
            node2 = f"{self.prefixes['quote']}{quote2_id}"
            path = nx.shortest_path(self.graph.to_undirected(), node1, node2)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_author_network(self, author: str, depth: int = 2) -> nx.Graph:
        """Get subgraph centered on an author"""
        author_id = f"{self.prefixes['author']}{author}"
        
        if not self.graph.has_node(author_id):
            return nx.Graph()
        
        # Get nodes within specified depth
        nodes = set([author_id])
        current_nodes = {author_id}
        
        for _ in range(depth):
            next_nodes = set()
            for node in current_nodes:
                neighbors = set(self.graph.neighbors(node)) | set(self.graph.predecessors(node))
                next_nodes.update(neighbors)
            nodes.update(next_nodes)
            current_nodes = next_nodes
        
        return self.graph.subgraph(nodes)
    
    def save_graph(self, output_path: str = "quote_knowledge_graph.pkl"):
        """Save knowledge graph to file"""
        output_file = Path(output_path)
        
        graph_data = {
            'graph': self.graph,
            'stats': self.stats,
            'author_quotes': dict(self.author_quotes),
            'topic_quotes': dict(self.topic_quotes),
            'quote_similarities': self.quote_similarities,
            'prefixes': self.prefixes
        }
        
        with open(output_file, 'wb') as f:
            pickle.dump(graph_data, f)
        
        logger.info(f"💾 Knowledge graph saved to {output_file}")
    
    def load_graph(self, input_path: str = "quote_knowledge_graph.pkl"):
        """Load knowledge graph from file"""
        input_file = Path(input_path)
        
        if not input_file.exists():
            raise FileNotFoundError(f"Graph file not found: {input_file}")
        
        with open(input_file, 'rb') as f:
            graph_data = pickle.load(f)
        
        self.graph = graph_data['graph']
        self.stats = graph_data['stats']
        self.author_quotes = defaultdict(list, graph_data['author_quotes'])
        self.topic_quotes = defaultdict(list, graph_data['topic_quotes'])
        self.quote_similarities = graph_data['quote_similarities']
        self.prefixes = graph_data['prefixes']
        
        logger.info(f"📖 Knowledge graph loaded from {input_file}")
    
    def print_statistics(self):
        """Print knowledge graph statistics"""
        print("\n🕸️  KNOWLEDGE GRAPH STATISTICS")
        print("=" * 50)
        print(f"👥 Authors: {self.stats['authors']:,}")
        print(f"📚 Quotes: {self.stats['quotes']:,}")
        print(f"🏷️  Topics: {self.stats['topics']:,}")
        print(f"📖 Fields: {self.stats['fields']:,}")
        print(f"🔗 Relationships: {self.stats['relationships']:,}")
        print(f"🌐 Total nodes: {self.graph.number_of_nodes():,}")
        print(f"➡️  Total edges: {self.graph.number_of_edges():,}")
        
        # Graph connectivity
        if self.graph.number_of_nodes() > 0:
            connected_components = nx.number_weakly_connected_components(self.graph)
            density = nx.density(self.graph)
            print(f"🔗 Connected components: {connected_components}")
            print(f"📊 Graph density: {density:.4f}")
        
        # Top concepts
        print(f"\n📈 TOP TOPICS BY QUOTES:")
        topic_counts = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get('type') == 'topic':
                topic_counts.append((data['name'], data.get('quote_count', 0)))
        
        topic_counts.sort(key=lambda x: x[1], reverse=True)
        for topic, count in topic_counts[:10]:
            print(f"   {topic}: {count} quotes")


def main():
    """Build knowledge graph for philosophical quotes"""
    print("🕸️  Knowledge Graph Builder for Philosophical Quotes")
    print("=" * 60)
    
    kg = QuoteKnowledgeGraph()
    
    # Build the graph
    kg.build_graph()
    
    # Save the graph
    kg.save_graph()
    
    # Print statistics
    kg.print_statistics()
    
    print(f"\n✅ Knowledge graph construction complete!")
    print(f"🚀 Ready for vector store creation and semantic search")
    
    return kg


if __name__ == "__main__":
    knowledge_graph = main()