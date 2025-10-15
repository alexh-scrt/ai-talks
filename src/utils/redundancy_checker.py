from typing import List
import logging

logger = logging.getLogger(__name__)


class RedundancyChecker:
    """Checks for semantic similarity to detect redundant content"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.threshold = similarity_threshold
        self.model = None
        self._initialized = False
    
    def _initialize_model(self):
        """Lazy initialization of sentence transformer model"""
        if self._initialized:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.np = np
            self._initialized = True
            logger.debug("Sentence transformer model initialized successfully")
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback similarity check")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize sentence transformer: {e}")
            self._initialized = True
    
    def is_redundant(self, candidate: str, recent_texts: List[str]) -> bool:
        """Check if candidate is too similar to recent texts"""
        if not recent_texts:
            return False
        
        self._initialize_model()
        
        if self.model is None:
            return self._fallback_similarity_check(candidate, recent_texts)
        
        try:
            embeddings = self.model.encode([candidate] + recent_texts)
            candidate_emb = embeddings[0]
            recent_embs = embeddings[1:]
            
            similarities = self.np.dot(recent_embs, candidate_emb) / (
                self.np.linalg.norm(recent_embs, axis=1) * self.np.linalg.norm(candidate_emb)
            )
            
            max_similarity = self.np.max(similarities)
            return max_similarity >= self.threshold
        except Exception as e:
            logger.error(f"Error in semantic similarity check: {e}")
            return self._fallback_similarity_check(candidate, recent_texts)
    
    def get_max_similarity(self, candidate: str, recent_texts: List[str]) -> float:
        """Get maximum similarity score"""
        if not recent_texts:
            return 0.0
        
        self._initialize_model()
        
        if self.model is None:
            return self._fallback_max_similarity(candidate, recent_texts)
        
        try:
            embeddings = self.model.encode([candidate] + recent_texts)
            candidate_emb = embeddings[0]
            recent_embs = embeddings[1:]
            
            similarities = self.np.dot(recent_embs, candidate_emb) / (
                self.np.linalg.norm(recent_embs, axis=1) * self.np.linalg.norm(candidate_emb)
            )
            
            return float(self.np.max(similarities))
        except Exception as e:
            logger.error(f"Error in similarity calculation: {e}")
            return self._fallback_max_similarity(candidate, recent_texts)
    
    def _fallback_similarity_check(self, candidate: str, recent_texts: List[str]) -> bool:
        """Simple word overlap fallback when sentence transformers unavailable"""
        candidate_words = set(candidate.lower().split())
        
        for text in recent_texts:
            text_words = set(text.lower().split())
            if len(candidate_words) == 0 or len(text_words) == 0:
                continue
            
            overlap = len(candidate_words & text_words)
            union = len(candidate_words | text_words)
            jaccard_similarity = overlap / union if union > 0 else 0
            
            if jaccard_similarity >= (self.threshold * 0.7):  # Lower threshold for word overlap
                return True
        
        return False
    
    def _fallback_max_similarity(self, candidate: str, recent_texts: List[str]) -> float:
        """Simple word overlap fallback for max similarity"""
        candidate_words = set(candidate.lower().split())
        max_sim = 0.0
        
        for text in recent_texts:
            text_words = set(text.lower().split())
            if len(candidate_words) == 0 or len(text_words) == 0:
                continue
            
            overlap = len(candidate_words & text_words)
            union = len(candidate_words | text_words)
            jaccard_similarity = overlap / union if union > 0 else 0
            max_sim = max(max_sim, jaccard_similarity)
        
        return max_sim