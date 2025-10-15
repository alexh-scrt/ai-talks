import re
import logging
from typing import List, Dict, Optional
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)


class SignalExtractor:
    """Extracts S-A-D signals from discussion exchanges"""
    
    def __init__(self):
        """Initialize signal extractor with lazy-loaded sentence transformer"""
        self.embedding_model = None
        self._embedding_initialized = False
        
        # Regex patterns for feature detection
        self.logic_patterns = [
            r'\bif\b.*\bthen\b',
            r'\btherefore\b',
            r'\bso that\b',
            r'\bentails\b',
            r'\bimplies\b',
            r'\bconsequently\b',
            r'\bhence\b',
            r'\bthus\b',
            r'\bit follows that\b'
        ]
        
        self.agency_patterns = {
            'ought': [r'\bought\b', r'\bshould\b', r'\bmust\b', r'\bchoose\b'],
            'decis': [r'\bI (decide|will|choose|commit)\b', r'\bwe (should|must|will)\b', r'\bdecision\b'],
            'conse': [r'\bwould lead to\b', r'\bresults in\b', r'\bcauses\b', r'\bconsequence\b'],
            'stanc': [r'\bI (believe|assert|claim|hold)\b', r'\bclearly\b', r'\bobviously\b', r'\bcertainly\b']
        }
        
        self.dependence_patterns = {
            'simulator': [r'\bsimulator\b', r'\bdetermin(ed|ism)\b', r'\bfate\b', r'\bpredetermin\b', r'\binevitable\b'],
            'rules': [r'\bhost said\b', r'\bmoderator (required|mandated)\b', r'\bmust follow\b', r'\brequired to\b'],
        }
    
    def _initialize_embeddings(self):
        """Lazy initialization of sentence transformer model"""
        if self._embedding_initialized:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.debug("Sentence transformer model initialized for signal extraction")
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback focus calculation")
            self.embedding_model = None
        except Exception as e:
            logger.error(f"Failed to initialize sentence transformer: {e}")
            self.embedding_model = None
        
        self._embedding_initialized = True
    
    def extract_structure_signals(
        self,
        exchanges: List[Dict],
        window: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Extract Structure (S) signals: order/groundedness of discourse
        
        Returns: {S_cite, S_logic, S_consis, S_focus} normalized to [0,1]
        """
        if window:
            exchanges = exchanges[-window:]
        
        total_turns = len(exchanges)
        if total_turns == 0:
            return {'S_cite': 0.0, 'S_logic': 0.0, 'S_consis': 0.0, 'S_focus': 0.0}
        
        # S_cite: citation/anchor density
        citation_count = sum(
            1 for e in exchanges 
            if 'retrieved_anchors' in e or 'citations' in e or 'cite' in e.get('content', '').lower()
        )
        S_cite = min(citation_count / total_turns, 1.0)
        
        # S_logic: logical operators presence
        logic_count = 0
        for exchange in exchanges:
            text = exchange.get('content', '').lower()
            if any(re.search(pattern, text) for pattern in self.logic_patterns):
                logic_count += 1
        S_logic = logic_count / total_turns
        
        # S_consis: contradiction rate inverted (simplified)
        # Use entailment presence as proxy for consistency
        entailment_count = sum(
            1 for e in exchanges
            if e.get('entailments') and len(e['entailments']) > 0
        )
        S_consis = entailment_count / total_turns
        
        # S_focus: topical drift inverse using embeddings
        S_focus = self._compute_focus_signal(exchanges)
        
        return {
            'S_cite': float(S_cite),
            'S_logic': float(S_logic),
            'S_consis': float(S_consis),
            'S_focus': float(S_focus)
        }
    
    def _compute_focus_signal(self, exchanges: List[Dict]) -> float:
        """Compute topical focus using embeddings or fallback"""
        total_turns = len(exchanges)
        
        if total_turns < 3:
            return 0.5  # Default for short discussions
        
        self._initialize_embeddings()
        
        if self.embedding_model is not None:
            try:
                # Use embeddings for semantic similarity
                texts = [e.get('content', '')[:500] for e in exchanges]  # Truncate long texts
                embeddings = self.embedding_model.encode(texts)
                
                # Compute pairwise similarities
                similarities = []
                for i in range(len(embeddings) - 1):
                    sim = np.dot(embeddings[i], embeddings[i+1]) / (
                        np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i+1])
                    )
                    similarities.append(sim)
                
                return float(np.mean(similarities)) if similarities else 0.5
            except Exception as e:
                logger.warning(f"Embedding-based focus calculation failed: {e}")
        
        # Fallback: use word overlap as proxy for topical consistency
        return self._fallback_focus_calculation(exchanges)
    
    def _fallback_focus_calculation(self, exchanges: List[Dict]) -> float:
        """Fallback focus calculation using word overlap"""
        total_turns = len(exchanges)
        if total_turns < 2:
            return 0.5
        
        # Extract word sets from consecutive exchanges
        overlaps = []
        for i in range(total_turns - 1):
            words1 = set(exchanges[i].get('content', '').lower().split())
            words2 = set(exchanges[i+1].get('content', '').lower().split())
            
            if len(words1) > 0 and len(words2) > 0:
                overlap = len(words1 & words2) / len(words1 | words2)
                overlaps.append(overlap)
        
        return float(np.mean(overlaps)) if overlaps else 0.5
    
    def extract_agency_signals(
        self,
        exchanges: List[Dict],
        window: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Extract Agency (A) signals: choice/commitment appearance
        
        Returns: {A_ought, A_decis, A_conse, A_stanc} normalized to [0,1]
        """
        if window:
            exchanges = exchanges[-window:]
        
        total_turns = len(exchanges)
        if total_turns == 0:
            return {'A_ought': 0.0, 'A_decis': 0.0, 'A_conse': 0.0, 'A_stanc': 0.0}
        
        results = {}
        
        for key, patterns in self.agency_patterns.items():
            count = 0
            for exchange in exchanges:
                text = exchange.get('content', '').lower()
                if any(re.search(pattern, text) for pattern in patterns):
                    count += 1
            
            signal_name = f'A_{key}'
            results[signal_name] = min(count / total_turns, 1.0)
        
        return results
    
    def extract_dependence_signals(
        self,
        exchanges: List[Dict],
        window: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Extract Dependence (D) signals: external control/inevitability
        
        Returns: {D_sim, D_rules, D_nonvar} normalized to [0,1]
        """
        if window:
            exchanges = exchanges[-window:]
        
        total_turns = len(exchanges)
        if total_turns == 0:
            return {'D_sim': 0.0, 'D_rules': 0.0, 'D_nonvar': 0.0}
        
        # D_sim: simulator/determinism references
        sim_count = 0
        for exchange in exchanges:
            text = exchange.get('content', '').lower()
            if any(re.search(pattern, text) for pattern in self.dependence_patterns['simulator']):
                sim_count += 1
        D_sim = min(sim_count / total_turns, 1.0)
        
        # D_rules: moderator constraints
        rules_count = sum(
            1 for e in exchanges
            if e.get('move') in ['PIVOT_DILEMMA', 'COORDINATOR'] or 
               e.get('speaker') in ['Moderator', 'Host', 'Narrator']
        )
        D_rules = min(rules_count / total_turns, 1.0)
        
        # D_nonvar: variability inverse (predictability)
        D_nonvar = self._compute_predictability(exchanges)
        
        return {
            'D_sim': float(D_sim),
            'D_rules': float(D_rules),
            'D_nonvar': float(D_nonvar)
        }
    
    def _compute_predictability(self, exchanges: List[Dict]) -> float:
        """Compute predictability as inverse of variety"""
        total_turns = len(exchanges)
        
        if total_turns < 5:
            return 0.5
        
        # Use move type variety as proxy
        move_types = [e.get('move', 'UNKNOWN') for e in exchanges]
        move_counts = Counter(move_types)
        
        # Higher entropy = more variety = lower dependence
        probabilities = np.array(list(move_counts.values())) / total_turns
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        max_entropy = np.log2(len(move_counts))
        
        if max_entropy > 0:
            variety_score = entropy / max_entropy
            return 1.0 - variety_score  # Invert: low variety = high dependence
        else:
            return 0.5
    
    def compute_aggregate_signals(
        self,
        exchanges: List[Dict],
        window: Optional[int] = None,
        weights: Optional[Dict[str, Dict[str, float]]] = None
    ) -> Dict[str, any]:
        """
        Compute aggregate S, A, D signals
        
        Returns: {S, A, D, components} with S/A/D in [0,1]
        """
        # Default equal weights
        if weights is None:
            weights = {
                'S': {'S_cite': 0.25, 'S_logic': 0.25, 'S_consis': 0.25, 'S_focus': 0.25},
                'A': {'A_ought': 0.25, 'A_decis': 0.25, 'A_conse': 0.25, 'A_stanc': 0.25},
                'D': {'D_sim': 0.33, 'D_rules': 0.33, 'D_nonvar': 0.34}
            }
        
        # Extract component signals
        S_components = self.extract_structure_signals(exchanges, window)
        A_components = self.extract_agency_signals(exchanges, window)
        D_components = self.extract_dependence_signals(exchanges, window)
        
        # Aggregate with weights
        S = sum(S_components[k] * weights['S'].get(k, 0.25) for k in S_components)
        A = sum(A_components[k] * weights['A'].get(k, 0.25) for k in A_components)
        D = sum(D_components[k] * weights['D'].get(k, 0.33) for k in D_components)
        
        return {
            'S': float(np.clip(S, 0, 1)),
            'A': float(np.clip(A, 0, 1)),
            'D': float(np.clip(D, 0, 1)),
            'components': {
                **S_components,
                **A_components,
                **D_components
            }
        }