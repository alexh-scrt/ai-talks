#!/usr/bin/env python3
"""
Vector Store Builder for Philosophical Quote Corpus

Creates semantic embeddings and vector store for advanced quote retrieval
using sentence transformers and FAISS for high-performance similarity search.
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for required libraries
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available - installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "sentence-transformers"])
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    logger.warning("faiss not available - installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "faiss-cpu"])
    import faiss
    FAISS_AVAILABLE = True


class QuoteVectorStore:
    """Advanced vector store for semantic quote retrieval"""
    
    def __init__(self, 
                 corpus_path: str = "enhanced_philosophical_quotes.jsonl",
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector store
        
        Args:
            corpus_path: Path to quote corpus JSONL file
            model_name: Sentence transformer model name
        """
        self.corpus_path = Path(corpus_path)
        self.model_name = model_name
        
        # Load sentence transformer model
        logger.info(f"🔄 Loading sentence transformer model: {model_name}")
        self.encoder = SentenceTransformer(model_name)
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
        
        # Storage
        self.quotes: List[Dict] = []
        self.quote_embeddings: Optional[np.ndarray] = None
        self.meaning_embeddings: Optional[np.ndarray] = None
        
        # FAISS indices
        self.quote_index: Optional[faiss.Index] = None
        self.meaning_index: Optional[faiss.Index] = None
        
        # Mappings
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        self.author_to_quotes: Dict[str, List[int]] = {}
        self.topic_to_quotes: Dict[str, List[int]] = {}
        
        # Statistics
        self.stats = {
            'total_quotes': 0,
            'embedding_dimension': self.embedding_dim,
            'unique_authors': 0,
            'unique_topics': 0,
            'avg_quote_length': 0,
            'model_name': model_name
        }
    
    def load_quotes(self) -> List[Dict]:
        """Load quotes from corpus"""
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus not found: {self.corpus_path}")
        
        quotes = []
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    quotes.append(json.loads(line.strip()))
        
        logger.info(f"📚 Loaded {len(quotes)} quotes from corpus")
        return quotes
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding"""
        # Basic preprocessing - keep it simple for philosophical content
        text = text.strip()
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        return text
    
    def create_embeddings(self):
        """Create embeddings for all quotes and meanings"""
        logger.info("🧠 Creating semantic embeddings...")
        
        # Load quotes
        self.quotes = self.load_quotes()
        
        # Create mappings
        for i, quote in enumerate(self.quotes):
            quote_id = quote['id']
            self.id_to_index[quote_id] = i
            self.index_to_id[i] = quote_id
            
            # Author mapping
            author = quote['author']
            if author not in self.author_to_quotes:
                self.author_to_quotes[author] = []
            self.author_to_quotes[author].append(i)
            
            # Topic mapping
            for topic in quote['topics']:
                if topic not in self.topic_to_quotes:
                    self.topic_to_quotes[topic] = []
                self.topic_to_quotes[topic].append(i)
        
        # Prepare texts for embedding
        quote_texts = [self.preprocess_text(q['quote']) for q in self.quotes]
        meaning_texts = [self.preprocess_text(q['meaning']) for q in self.quotes]
        
        # Create embeddings in batches for efficiency
        batch_size = 32
        logger.info(f"📊 Creating quote embeddings (batch size: {batch_size})...")
        
        quote_embeddings = []
        for i in range(0, len(quote_texts), batch_size):
            batch = quote_texts[i:i+batch_size]
            batch_embeddings = self.encoder.encode(batch, convert_to_numpy=True)
            quote_embeddings.append(batch_embeddings)
            
            if i % (batch_size * 10) == 0:
                logger.info(f"   Processed {i}/{len(quote_texts)} quotes")
        
        self.quote_embeddings = np.vstack(quote_embeddings)
        
        logger.info(f"📖 Creating meaning embeddings...")
        meaning_embeddings = []
        for i in range(0, len(meaning_texts), batch_size):
            batch = meaning_texts[i:i+batch_size]
            batch_embeddings = self.encoder.encode(batch, convert_to_numpy=True)
            meaning_embeddings.append(batch_embeddings)
            
            if i % (batch_size * 10) == 0:
                logger.info(f"   Processed {i}/{len(meaning_texts)} meanings")
        
        self.meaning_embeddings = np.vstack(meaning_embeddings)
        
        logger.info(f"✅ Created embeddings: {self.quote_embeddings.shape}")
    
    def build_faiss_indices(self):
        """Build FAISS indices for fast similarity search"""
        logger.info("🔍 Building FAISS indices for fast search...")
        
        if self.quote_embeddings is None or self.meaning_embeddings is None:
            raise ValueError("Embeddings must be created first")
        
        # Normalize embeddings for cosine similarity
        quote_embeddings_norm = self.quote_embeddings / np.linalg.norm(
            self.quote_embeddings, axis=1, keepdims=True)
        meaning_embeddings_norm = self.meaning_embeddings / np.linalg.norm(
            self.meaning_embeddings, axis=1, keepdims=True)
        
        # Create FAISS indices
        # Use IndexFlatIP for exact cosine similarity (inner product after normalization)
        self.quote_index = faiss.IndexFlatIP(self.embedding_dim)
        self.meaning_index = faiss.IndexFlatIP(self.embedding_dim)
        
        # Add embeddings to indices
        self.quote_index.add(quote_embeddings_norm.astype(np.float32))
        self.meaning_index.add(meaning_embeddings_norm.astype(np.float32))
        
        logger.info(f"📊 FAISS indices built: {self.quote_index.ntotal} quotes indexed")
    
    def semantic_search(self, 
                       query: str, 
                       search_type: str = "both",
                       top_k: int = 10,
                       min_similarity: float = 0.3) -> List[Tuple[Dict, float]]:
        """
        Perform semantic search on quotes
        
        Args:
            query: Search query text
            search_type: "quote", "meaning", or "both"
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (quote_dict, similarity_score) tuples
        """
        if self.quote_index is None or self.meaning_index is None:
            raise ValueError("FAISS indices must be built first")
        
        # Encode query
        query_preprocessed = self.preprocess_text(query)
        query_embedding = self.encoder.encode([query_preprocessed])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        results = []
        
        if search_type in ["quote", "both"]:
            # Search quote embeddings
            scores, indices = self.quote_index.search(
                query_embedding.astype(np.float32), top_k * 2)
            
            for score, idx in zip(scores[0], indices[0]):
                if score >= min_similarity and idx < len(self.quotes):
                    quote = self.quotes[idx].copy()
                    results.append((quote, float(score), "quote"))
        
        if search_type in ["meaning", "both"]:
            # Search meaning embeddings
            scores, indices = self.meaning_index.search(
                query_embedding.astype(np.float32), top_k * 2)
            
            for score, idx in zip(scores[0], indices[0]):
                if score >= min_similarity and idx < len(self.quotes):
                    quote = self.quotes[idx].copy()
                    results.append((quote, float(score), "meaning"))
        
        # Remove duplicates and sort by score
        seen_ids = set()
        unique_results = []
        
        for quote, score, search_mode in results:
            if quote['id'] not in seen_ids:
                seen_ids.add(quote['id'])
                quote['search_mode'] = search_mode
                unique_results.append((quote, score))
        
        unique_results.sort(key=lambda x: x[1], reverse=True)
        return unique_results[:top_k]
    
    def find_similar_quotes(self, quote_id: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Find quotes similar to a given quote"""
        if quote_id not in self.id_to_index:
            return []
        
        idx = self.id_to_index[quote_id]
        quote_embedding = self.quote_embeddings[idx:idx+1]
        quote_embedding = quote_embedding / np.linalg.norm(quote_embedding)
        
        scores, indices = self.quote_index.search(
            quote_embedding.astype(np.float32), top_k + 1)  # +1 to exclude self
        
        results = []
        for score, similar_idx in zip(scores[0], indices[0]):
            if similar_idx != idx and similar_idx < len(self.quotes):
                similar_quote = self.quotes[similar_idx]
                results.append((similar_quote, float(score)))
        
        return results[:top_k]
    
    def search_by_author(self, author: str, query: str = "", top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Search quotes by specific author with optional semantic filtering"""
        if author not in self.author_to_quotes:
            return []
        
        author_indices = self.author_to_quotes[author]
        
        if not query:
            # Return random sample of author's quotes
            import random
            sample_indices = random.sample(author_indices, min(top_k, len(author_indices)))
            return [(self.quotes[idx], 1.0) for idx in sample_indices]
        
        # Semantic search within author's quotes
        query_embedding = self.encoder.encode([self.preprocess_text(query)])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        results = []
        for idx in author_indices:
            quote_embedding = self.quote_embeddings[idx:idx+1]
            quote_embedding = quote_embedding / np.linalg.norm(quote_embedding)
            
            similarity = np.dot(query_embedding[0], quote_embedding[0])
            results.append((self.quotes[idx], float(similarity)))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def search_by_topic(self, topic: str, query: str = "", top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Search quotes by topic with optional semantic filtering"""
        if topic not in self.topic_to_quotes:
            return []
        
        topic_indices = self.topic_to_quotes[topic]
        
        if not query:
            # Return highest-rated quotes for topic
            return [(self.quotes[idx], 1.0) for idx in topic_indices[:top_k]]
        
        # Semantic search within topic
        query_embedding = self.encoder.encode([self.preprocess_text(query)])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        results = []
        for idx in topic_indices:
            quote_embedding = self.quote_embeddings[idx:idx+1]
            quote_embedding = quote_embedding / np.linalg.norm(quote_embedding)
            
            similarity = np.dot(query_embedding[0], quote_embedding[0])
            results.append((self.quotes[idx], float(similarity)))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def calculate_statistics(self):
        """Calculate vector store statistics"""
        if not self.quotes:
            return
        
        self.stats.update({
            'total_quotes': len(self.quotes),
            'unique_authors': len(self.author_to_quotes),
            'unique_topics': len(self.topic_to_quotes),
            'avg_quote_length': np.mean([len(q['quote'].split()) for q in self.quotes])
        })
    
    def save_vector_store(self, output_path: str = "quote_vector_store.pkl"):
        """Save vector store to file"""
        output_file = Path(output_path)
        
        vector_data = {
            'quotes': self.quotes,
            'quote_embeddings': self.quote_embeddings,
            'meaning_embeddings': self.meaning_embeddings,
            'id_to_index': self.id_to_index,
            'index_to_id': self.index_to_id,
            'author_to_quotes': self.author_to_quotes,
            'topic_to_quotes': self.topic_to_quotes,
            'stats': self.stats,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim
        }
        
        with open(output_file, 'wb') as f:
            pickle.dump(vector_data, f)
        
        # Save FAISS indices separately
        quote_index_path = output_file.with_suffix('.quote.index')
        meaning_index_path = output_file.with_suffix('.meaning.index')
        
        faiss.write_index(self.quote_index, str(quote_index_path))
        faiss.write_index(self.meaning_index, str(meaning_index_path))
        
        logger.info(f"💾 Vector store saved to {output_file}")
        logger.info(f"📊 FAISS indices saved to {quote_index_path} and {meaning_index_path}")
    
    def load_vector_store(self, input_path: str = "quote_vector_store.pkl"):
        """Load vector store from file"""
        input_file = Path(input_path)
        
        if not input_file.exists():
            raise FileNotFoundError(f"Vector store not found: {input_file}")
        
        with open(input_file, 'rb') as f:
            vector_data = pickle.load(f)
        
        self.quotes = vector_data['quotes']
        self.quote_embeddings = vector_data['quote_embeddings']
        self.meaning_embeddings = vector_data['meaning_embeddings']
        self.id_to_index = vector_data['id_to_index']
        self.index_to_id = vector_data['index_to_id']
        self.author_to_quotes = vector_data['author_to_quotes']
        self.topic_to_quotes = vector_data['topic_to_quotes']
        self.stats = vector_data['stats']
        self.model_name = vector_data['model_name']
        self.embedding_dim = vector_data['embedding_dim']
        
        # Load FAISS indices
        quote_index_path = input_file.with_suffix('.quote.index')
        meaning_index_path = input_file.with_suffix('.meaning.index')
        
        self.quote_index = faiss.read_index(str(quote_index_path))
        self.meaning_index = faiss.read_index(str(meaning_index_path))
        
        logger.info(f"📖 Vector store loaded from {input_file}")
    
    def print_statistics(self):
        """Print vector store statistics"""
        print("\n🧠 VECTOR STORE STATISTICS")
        print("=" * 50)
        print(f"📚 Total quotes: {self.stats['total_quotes']:,}")
        print(f"👥 Unique authors: {self.stats['unique_authors']:,}")
        print(f"🏷️  Unique topics: {self.stats['unique_topics']:,}")
        print(f"📊 Embedding dimension: {self.stats['embedding_dimension']}")
        print(f"📖 Average quote length: {self.stats['avg_quote_length']:.1f} words")
        print(f"🤖 Model: {self.stats['model_name']}")
        
        print(f"\n📈 TOP AUTHORS BY QUOTE COUNT:")
        author_counts = [(author, len(indices)) for author, indices in self.author_to_quotes.items()]
        author_counts.sort(key=lambda x: x[1], reverse=True)
        for author, count in author_counts[:10]:
            print(f"   {author}: {count} quotes")
        
        print(f"\n🏷️  TOP TOPICS BY QUOTE COUNT:")
        topic_counts = [(topic, len(indices)) for topic, indices in self.topic_to_quotes.items()]
        topic_counts.sort(key=lambda x: x[1], reverse=True)
        for topic, count in topic_counts[:10]:
            print(f"   {topic}: {count} quotes")


def main():
    """Build vector store for philosophical quotes"""
    print("🧠 Vector Store Builder for Philosophical Quotes")
    print("=" * 60)
    
    # Create vector store
    vector_store = QuoteVectorStore()
    
    # Create embeddings
    vector_store.create_embeddings()
    
    # Build FAISS indices
    vector_store.build_faiss_indices()
    
    # Calculate statistics
    vector_store.calculate_statistics()
    
    # Save vector store
    vector_store.save_vector_store()
    
    # Print statistics
    vector_store.print_statistics()
    
    print(f"\n✅ Vector store construction complete!")
    print(f"🚀 Ready for advanced semantic search and quote retrieval")
    
    # Demo search
    print(f"\n🔍 DEMO SEARCH RESULTS:")
    print("-" * 30)
    
    demo_queries = [
        "What is the meaning of life?",
        "How can we find truth and knowledge?",
        "What is consciousness and the mind?"
    ]
    
    for query in demo_queries:
        print(f"\nQuery: '{query}'")
        results = vector_store.semantic_search(query, top_k=3)
        for i, (quote, score) in enumerate(results, 1):
            print(f"  {i}. [{score:.3f}] {quote['author']}: \"{quote['quote'][:80]}...\"")
    
    return vector_store


if __name__ == "__main__":
    vector_store = main()