"""Quote retrieval system using hybrid keyword + semantic search"""

import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import numpy as np

logger = logging.getLogger(__name__)

# Check for sentence transformers availability
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available - falling back to keyword-only search")
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class QuoteRetriever:
    """
    Retrieves philosophically relevant quotes using hybrid keyword + semantic search
    """
    
    def __init__(self, corpus_path: str = "data/philosophical_quotes.jsonl"):
        """
        Initialize quote retriever
        
        Args:
            corpus_path: Path to JSONL corpus file
        """
        self.corpus_path = Path(corpus_path)
        self.quotes: List[Dict] = []
        self.quote_index: Dict[str, Dict] = {}  # id -> quote
        
        # Semantic search model (optional)
        self.embedding_model = None
        self.quote_embeddings: Optional[np.ndarray] = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("📊 Semantic search enabled with sentence transformers")
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}")
                self.embedding_model = None
        
        # Usage tracking
        self.used_quotes: Set[str] = set()
        self.last_authors: List[str] = []  # Track last N authors
        self.author_usage: Dict[str, int] = {}
        
        # Load corpus
        self._load_corpus()
        logger.info(f"📚 QuoteRetriever initialized with {len(self.quotes)} quotes")
    
    def _load_corpus(self):
        """Load quotes from JSONL file"""
        if not self.corpus_path.exists():
            logger.warning(f"Quote corpus not found: {self.corpus_path}")
            return
        
        with open(self.corpus_path, 'r') as f:
            for line in f:
                if line.strip():
                    quote = json.loads(line.strip())
                    self.quotes.append(quote)
                    self.quote_index[quote['id']] = quote
        
        # Precompute embeddings for all quotes if model available
        if self.quotes and self.embedding_model:
            try:
                quote_texts = [q['quote'] for q in self.quotes]
                self.quote_embeddings = self.embedding_model.encode(quote_texts)
                logger.info(f"📊 Precomputed embeddings for {len(quote_texts)} quotes")
            except Exception as e:
                logger.warning(f"Failed to compute embeddings: {e}")
                self.quote_embeddings = None
    
    def retrieve(
        self,
        topics: List[str],
        current_tension: Optional[Tuple[str, str]] = None,
        exclude_authors: Optional[List[str]] = None,
        top_k: int = 3,
        diversity_weight: float = 0.3,
        relevance_threshold: float = 0.65
    ) -> List[Dict]:
        """
        Retrieve relevant quotes using hybrid search
        
        Args:
            topics: List of topic keywords from current discussion
            current_tension: Optional tension pair for targeted retrieval
            exclude_authors: Authors to exclude (avoid repetition)
            top_k: Number of quotes to return
            diversity_weight: Weight for diversity vs pure relevance (0-1)
            relevance_threshold: Minimum semantic similarity score
            
        Returns:
            List of quote dictionaries with relevance scores
        """
        if not self.quotes:
            logger.warning("No quotes available in corpus")
            return []
        
        # Build search query
        query = self._build_query(topics, current_tension)
        logger.debug(f"Quote search query: {query}")
        
        # Step 1: Keyword filtering
        keyword_candidates = self._keyword_filter(topics, current_tension)
        
        # Step 2: Semantic ranking (if available) or fallback to keyword scoring
        if self.embedding_model and self.quote_embeddings is not None:
            ranked_quotes = self._semantic_rank(query, keyword_candidates, relevance_threshold)
        else:
            ranked_quotes = self._keyword_rank(keyword_candidates, topics, current_tension)
        
        # Step 3: Diversity filtering
        diverse_quotes = self._apply_diversity(
            ranked_quotes,
            exclude_authors or self.last_authors[-3:],
            diversity_weight
        )
        
        # Return top K
        selected = diverse_quotes[:top_k]
        
        # Track usage
        for quote in selected:
            self.used_quotes.add(quote['id'])
            author = quote['author']
            self.last_authors.append(author)
            self.author_usage[author] = self.author_usage.get(author, 0) + 1
        
        # Trim last_authors to keep only recent
        if len(self.last_authors) > 10:
            self.last_authors = self.last_authors[-10:]
        
        logger.info(f"📖 Retrieved {len(selected)} quotes")
        return selected
    
    def _build_query(self, topics: List[str], tension: Optional[Tuple[str, str]] = None) -> str:
        """Build search query from topics and tension"""
        query_parts = topics.copy()
        
        if tension:
            query_parts.extend(tension)
        
        return " ".join(query_parts)
    
    def _keyword_filter(
        self,
        topics: List[str],
        tension: Optional[Tuple[str, str]] = None
    ) -> List[Dict]:
        """Filter quotes by keyword match in topics"""
        candidates = []
        search_terms = set(t.lower() for t in topics)
        
        if tension:
            search_terms.update(t.lower() for t in tension)
        
        for quote in self.quotes:
            # Check if any search term matches quote topics
            quote_topics = set(t.lower() for t in quote['topics'])
            
            # Exact match or partial match
            if search_terms & quote_topics:  # Intersection
                candidates.append(quote)
            else:
                # Also check for partial matches in quote text or topics
                quote_text_lower = quote['quote'].lower()
                if any(term in quote_text_lower for term in search_terms):
                    candidates.append(quote)
        
        # If too few, return all quotes
        if len(candidates) < 5:
            logger.debug(f"Only {len(candidates)} keyword matches, using full corpus")
            return self.quotes
        
        logger.debug(f"Keyword filter: {len(candidates)} candidates")
        return candidates
    
    def _semantic_rank(
        self,
        query: str,
        candidates: List[Dict],
        threshold: float
    ) -> List[Dict]:
        """Rank candidates by semantic similarity"""
        if not candidates:
            return []
        
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Get candidate indices
            candidate_indices = [self.quotes.index(c) for c in candidates]
            candidate_embeddings = self.quote_embeddings[candidate_indices]
            
            # Compute cosine similarities
            similarities = np.dot(candidate_embeddings, query_embedding) / (
                np.linalg.norm(candidate_embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Attach scores and filter by threshold
            ranked = []
            for idx, sim in enumerate(similarities):
                if sim >= threshold:
                    quote = candidates[idx].copy()
                    quote['relevance_score'] = float(sim)
                    ranked.append(quote)
            
            # Sort by relevance
            ranked.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.debug(f"Semantic ranking: {len(ranked)} quotes above threshold")
            return ranked
            
        except Exception as e:
            logger.warning(f"Semantic ranking failed: {e}, falling back to keyword ranking")
            return self._keyword_rank(candidates, [], None)
    
    def _keyword_rank(
        self,
        candidates: List[Dict],
        topics: List[str],
        tension: Optional[Tuple[str, str]] = None
    ) -> List[Dict]:
        """Fallback keyword-based ranking when semantic search unavailable"""
        search_terms = set(t.lower() for t in topics)
        if tension:
            search_terms.update(t.lower() for t in tension)
        
        ranked = []
        for quote in candidates:
            # Score based on topic overlap
            quote_topics = set(t.lower() for t in quote['topics'])
            overlap = len(search_terms & quote_topics)
            
            # Bonus for exact matches in quote text
            quote_text_lower = quote['quote'].lower()
            text_matches = sum(1 for term in search_terms if term in quote_text_lower)
            
            # Simple relevance score
            relevance_score = (overlap * 0.7 + text_matches * 0.3) / max(len(search_terms), 1)
            
            # Only include if some relevance
            if relevance_score > 0:
                quote_copy = quote.copy()
                quote_copy['relevance_score'] = relevance_score
                ranked.append(quote_copy)
        
        # Sort by relevance
        ranked.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.debug(f"Keyword ranking: {len(ranked)} quotes with relevance")
        return ranked
    
    def _apply_diversity(
        self,
        quotes: List[Dict],
        exclude_authors: List[str],
        diversity_weight: float
    ) -> List[Dict]:
        """Apply diversity constraints to quote selection"""
        if not quotes:
            return []
        
        # Filter out recently used authors
        filtered = [
            q for q in quotes
            if q['author'] not in exclude_authors
        ]
        
        # If too few remain, allow some repetition
        if len(filtered) < 3 and len(quotes) > 3:
            logger.debug("Relaxing author diversity constraint")
            filtered = quotes
        
        # Boost quotes from underused authors
        for quote in filtered:
            author = quote['author']
            usage_count = self.author_usage.get(author, 0)
            
            # Diversity bonus (inverse of usage frequency)
            diversity_bonus = 1.0 / (1.0 + usage_count)
            
            # Combine relevance and diversity
            relevance = quote.get('relevance_score', 0.5)
            quote['final_score'] = (
                relevance * (1 - diversity_weight) +
                diversity_bonus * diversity_weight
            )
        
        # Re-sort by final score
        filtered.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return filtered
    
    def get_quote_by_id(self, quote_id: str) -> Optional[Dict]:
        """Get a specific quote by ID"""
        return self.quote_index.get(quote_id)
    
    def get_quotes_by_author(self, author: str) -> List[Dict]:
        """Get all quotes by a specific author"""
        return [q for q in self.quotes if q['author'] == author]
    
    def get_quotes_by_era(self, era: str) -> List[Dict]:
        """Get all quotes from a specific era"""
        return [q for q in self.quotes if q['era'] == era]
    
    def get_statistics(self) -> Dict:
        """Get usage statistics"""
        era_distribution = {}
        tradition_distribution = {}
        
        for quote in self.quotes:
            era = quote['era']
            tradition = quote['tradition']
            era_distribution[era] = era_distribution.get(era, 0) + 1
            tradition_distribution[tradition] = tradition_distribution.get(tradition, 0) + 1
        
        return {
            'total_quotes': len(self.quotes),
            'quotes_used': len(self.used_quotes),
            'unique_authors': len(set(q['author'] for q in self.quotes)),
            'era_distribution': era_distribution,
            'tradition_distribution': tradition_distribution,
            'author_usage': self.author_usage.copy(),
            'recent_authors': self.last_authors[-5:],
            'semantic_search_enabled': self.embedding_model is not None
        }
    
    def reset_session(self):
        """Reset tracking for new discussion session"""
        self.used_quotes.clear()
        self.last_authors.clear()
        self.author_usage.clear()
        logger.info("📚 Quote retriever session reset")