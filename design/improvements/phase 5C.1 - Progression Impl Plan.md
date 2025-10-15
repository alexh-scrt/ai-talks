
# Consequence Engine Implementation Plan: Force Progression, Stop Orbiting

## 🎯 Overview

This implementation adds a **state machine** that detects when discussions are circling the same tension without making progress, forces **Consequence Tests** to generate new entailments, and **pivots** when orbiting persists.

### Success Criteria
✅ Detect tension saturation (>2 cycles without new entailments)  
✅ Auto-inject Consequence Tests  
✅ Force pivots after failed tests  
✅ Track orbit vs progression metrics  
✅ Maintain backward compatibility  

---

## Phase 1: Data Models for Tension & Consequence Tracking

### 1.1 Create TensionState Class

**File**: `src/states/tension_state.py` (new file)

```python
# src/states/tension_state.py

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


class TensionCategory(Enum):
    """Known philosophical tension pairs"""
    NECESSITY_CONTINGENCY = ("necessity", "contingency")
    STRUCTURE_AGENCY = ("structure", "agency")
    OBJECTIVITY_SUBJECTIVITY = ("objectivity", "subjectivity")
    SIMULATION_REALITY = ("simulation", "reality")
    MATH_ETHICS = ("math", "ethics")
    DETERMINISM_FREEDOM = ("determinism", "freedom")
    INDIVIDUAL_COLLECTIVE = ("individual", "collective")
    RATIONAL_EMOTIONAL = ("rational", "emotional")


@dataclass
class TensionState:
    """Tracks cycles and progression on a specific philosophical tension"""
    
    pair: Tuple[str, str]  # e.g., ('necessity', 'contingency')
    cycles: int = 0  # Number of volleys on this tension
    last_consequence_turn: int = -1  # Turn number when last entailment appeared
    last_test_turn: int = -1  # Turn number when Consequence Test was triggered
    consequence_tests_count: int = 0  # How many tests have been run
    max_cycles: int = 2  # Threshold before forcing test
    max_tests: int = 2  # Max tests before forced pivot
    
    def can_continue(self) -> bool:
        """Check if this tension can continue without intervention"""
        return self.cycles < self.max_cycles
    
    def needs_consequence_test(self, current_turn: int) -> bool:
        """Check if we should inject a Consequence Test"""
        # Don't test if we just tested
        if self.last_test_turn == current_turn - 1:
            return False
        
        # Test if cycles exceed threshold and no recent entailment
        return (
            self.cycles >= self.max_cycles and
            (current_turn - self.last_consequence_turn) > 2
        )
    
    def needs_pivot(self, current_turn: int) -> bool:
        """Check if we should force a pivot"""
        return (
            self.consequence_tests_count >= self.max_tests and
            (current_turn - self.last_consequence_turn) > self.max_tests
        )
    
    def record_entailment(self, turn: int):
        """Record that a new entailment appeared"""
        self.last_consequence_turn = turn
        self.cycles = 0  # Reset cycles when progress is made
    
    def record_test(self, turn: int):
        """Record that a Consequence Test was injected"""
        self.last_test_turn = turn
        self.consequence_tests_count += 1
    
    def increment_cycle(self):
        """Increment the cycle count"""
        self.cycles += 1
    
    def reset(self):
        """Reset state after pivot"""
        self.cycles = 0
        self.consequence_tests_count = 0
```

---

### 1.2 Add Tension Tracking to GroupDiscussionState

**File**: `src/states/group_state.py` (modify)

Add imports:
```python
from src.states.tension_state import TensionState, TensionCategory
```

Add to `GroupDiscussionState.__init__`:

```python
class GroupDiscussionState:
    def __init__(self, ...):
        # ... existing init ...
        
        # Tension tracking
        self.tensions: Dict[Tuple[str, str], TensionState] = {}
        self.current_tension: Optional[Tuple[str, str]] = None
        self.tension_history: List[Tuple[str, str]] = []  # History of tensions discussed
        self.last_pivot_turn: int = -1
        
        # Initialize recognized tensions
        self._initialize_tensions()
    
    def _initialize_tensions(self):
        """Initialize tracking for all recognized tensions"""
        for tension_cat in TensionCategory:
            pair = tuple(sorted(tension_cat.value))
            self.tensions[pair] = TensionState(pair=pair)
    
    def get_tension_state(self, concept_a: str, concept_b: str) -> Optional[TensionState]:
        """Get tension state for two concepts"""
        pair = tuple(sorted([concept_a.lower(), concept_b.lower()]))
        return self.tensions.get(pair)
    
    def update_tension(self, topics: set, turn: int):
        """Update tension tracking based on topics mentioned in turn"""
        # Check which tensions are active
        for tension_pair, tension_state in self.tensions.items():
            a, b = tension_pair
            
            # Check if both sides of tension are mentioned
            # (either in current turn or recent history)
            if a in topics or b in topics:
                # Get recent topics from last 2 turns
                recent_topics = self._get_recent_topics(window=2)
                
                if (a in topics and b in recent_topics) or (b in topics and a in recent_topics):
                    tension_state.increment_cycle()
                    self.current_tension = tension_pair
                    
                    if tension_pair not in self.tension_history:
                        self.tension_history.append(tension_pair)
    
    def _get_recent_topics(self, window: int = 2) -> set:
        """Extract topics from recent exchanges"""
        if len(self.exchanges) < window:
            return set()
        
        recent = self.exchanges[-window:]
        topics = set()
        
        for exchange in recent:
            # Extract topics from content (simplified)
            content_lower = exchange.get('content', '').lower()
            for tension_pair in self.tensions.keys():
                for concept in tension_pair:
                    if concept in content_lower:
                        topics.add(concept)
        
        return topics
```

---

## Phase 2: Topic & Entailment Detection

### 2.1 Create Topic Extractor

**File**: `src/analysis/topic_extractor.py` (new file)

```python
# src/analysis/topic_extractor.py

import re
import logging
from typing import Set, List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


class TopicExtractor:
    """Extracts philosophical topics from text using keywords and embeddings"""
    
    # Lexicons for known philosophical concepts
    LEXICONS = {
        'necessity': {'necessity', 'necessary', 'must', 'determinism', 'fate', 'lawbound', 'inevitable'},
        'contingency': {'contingent', 'arbitrary', 'accident', 'chance', 'could-have-been', 'random', 'possible'},
        'structure': {'structure', 'code', 'law', 'rule', 'order', 'grammar', 'lattice', 'system', 'framework'},
        'agency': {'agency', 'choice', 'will', 'decide', 'responsibility', 'freedom', 'autonomy', 'volition'},
        'objectivity': {'objective', 'objectivity', 'fact', 'truth', 'reality', 'external'},
        'subjectivity': {'subjective', 'subjectivity', 'perspective', 'experience', 'qualia', 'phenomenal'},
        'simulation': {'simulation', 'simulator', 'virtual', 'computed', 'generated', 'artificial'},
        'reality': {'reality', 'real', 'actual', 'concrete', 'physical', 'material'},
        'math': {'mathematical', 'math', 'formal', 'logical', 'abstract', 'axiomatic'},
        'ethics': {'ethical', 'ethics', 'moral', 'ought', 'should', 'right', 'wrong', 'good', 'bad'},
        'determinism': {'determinism', 'determined', 'causal', 'predetermined', 'fated'},
        'freedom': {'freedom', 'free', 'choice', 'liberty', 'autonomous'},
        'individual': {'individual', 'self', 'person', 'ego', 'singular', 'alone'},
        'collective': {'collective', 'group', 'society', 'community', 'shared', 'social'},
        'rational': {'rational', 'reason', 'logic', 'argument', 'analysis'},
        'emotional': {'emotional', 'feeling', 'affect', 'sentiment', 'passion'}
    }
    
    def __init__(self, use_embeddings: bool = True):
        """
        Initialize topic extractor
        
        Args:
            use_embeddings: Whether to use semantic embeddings (slower but more accurate)
        """
        self.use_embeddings = use_embeddings
        
        if use_embeddings:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            # Precompute seed embeddings
            self.seed_embeddings = {
                topic: self.embedding_model.encode(list(words))
                for topic, words in self.LEXICONS.items()
            }
        else:
            self.embedding_model = None
            self.seed_embeddings = None
    
    def extract_topics(self, text: str, threshold: float = 0.7) -> Set[str]:
        """
        Extract topics from text using hybrid keyword + embedding approach
        
        Args:
            text: Input text to analyze
            threshold: Similarity threshold for embedding matching
            
        Returns:
            Set of topic identifiers found in text
        """
        topics = set()
        text_lower = text.lower()
        
        # Step 1: Fast keyword matching
        for topic, keywords in self.LEXICONS.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.add(topic)
        
        # Step 2: Embedding-based matching (optional)
        if self.use_embeddings and self.embedding_model and len(text_lower.split()) > 5:
            text_embedding = self.embedding_model.encode(text)
            
            for topic, seed_embs in self.seed_embeddings.items():
                # Compute cosine similarities
                similarities = []
                for seed_emb in seed_embs:
                    sim = np.dot(text_embedding, seed_emb) / (
                        np.linalg.norm(text_embedding) * np.linalg.norm(seed_emb)
                    )
                    similarities.append(sim)
                
                max_sim = max(similarities)
                if max_sim >= threshold:
                    topics.add(topic)
        
        return topics
    
    def extract_from_exchanges(self, exchanges: List[Dict], window: int = None) -> Set[str]:
        """Extract all topics from a list of exchanges"""
        if window:
            exchanges = exchanges[-window:]
        
        all_topics = set()
        for exchange in exchanges:
            content = exchange.get('content', '')
            topics = self.extract_topics(content)
            all_topics.update(topics)
        
        return all_topics
```

---

### 2.2 Enhance Existing EntailmentDetector

**File**: `src/utils/entailment_detector.py` (modify existing or create if not exists)

This should already exist from the redundancy mitigation plan. Enhance it:

```python
# src/utils/entailment_detector.py

import re
import logging
from typing import List, Set, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class EntailmentType(Enum):
    """Types of logical entailments"""
    IMPLICATION = "implication"
    APPLICATION = "application"
    COUNTEREXAMPLE = "counterexample"
    TEST = "test"


class EntailmentDetector:
    """Detects whether text contains new logical entailments"""
    
    # Enhanced patterns with more coverage
    PATTERNS = {
        EntailmentType.IMPLICATION: [
            r'\bif\b.*\bthen\b',
            r'\btherefore\b',
            r'\bhence\b',
            r'\bso\b.*\b(that|we)\b',
            r'\bimplies\b',
            r'\bentails\b',
            r'\bconsequently\b',
            r'\bthus\b',
            r'\bit follows that\b',
            r'\bmeans that\b',
            r'→',  # Arrow symbol
            r'⇒',  # Implication symbol
        ],
        EntailmentType.APPLICATION: [
            r'\bin practice\b',
            r'\bfor example\b',
            r'\bconsider\b.*\b(case|scenario|situation)\b',
            r'\bthus we should\b',
            r'\bpolicy\b',
            r'\bwe could apply\b',
            r'\bin the (real )?world\b',
            r'\bconcretely\b',
            r'\bspecifically\b',
        ],
        EntailmentType.COUNTEREXAMPLE: [
            r'\bunless\b',
            r'\bexcept when\b',
            r'\bcounterexample\b',
            r'\bfails when\b',
            r'\bnot if\b',
            r'\bhowever\b.*\b(consider|imagine)\b',
            r'\bbut what about\b',
            r'\bwhat if\b',
        ],
        EntailmentType.TEST: [
            r'\bwe could test\b',
            r'\bcriterion\b',
            r'\bmeasure\b',
            r'\bobservable\b',
            r'\bverify by\b',
            r'\bexperiment\b',
            r'\bprediction\b',
            r'\bfalsif(y|iable)\b',
            r'\boperational(ly)?\b',
        ]
    }
    
    def detect(self, text: str) -> Set[EntailmentType]:
        """
        Detect entailment types in text
        
        Args:
            text: Text to analyze
            
        Returns:
            Set of EntailmentType enums found
        """
        text_lower = text.lower()
        found = set()
        
        for ent_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    found.add(ent_type)
                    break  # Found this type, move to next
        
        return found
    
    def has_entailment(self, text: str) -> bool:
        """Check if text has ANY entailment"""
        return len(self.detect(text)) > 0
    
    def get_entailment_details(self, text: str) -> Dict[str, any]:
        """Get detailed entailment information"""
        entailments = self.detect(text)
        
        return {
            'has_entailment': len(entailments) > 0,
            'types': [e.value for e in entailments],
            'count': len(entailments),
            'primary_type': list(entailments)[0].value if entailments else None
        }
```

---

## Phase 3: Consequence Test Generator

### 3.1 Create ConsequenceTestGenerator

**File**: `src/agents/consequence_test_generator.py` (new file)

```python
# src/agents/consequence_test_generator.py

import logging
import random
from typing import Dict, Optional, Tuple
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


CONSEQUENCE_TEST_SYSTEM_PROMPT = """You are a philosophical moderator conducting a **Consequence Test**.

Your role is to force participants to move from abstract debate to concrete implications.

When a philosophical tension is being rehashed without progress, you inject a sharp, focused question that demands:
1. A specific implication for ethics, knowledge, or action
2. A testable prediction or observable consequence
3. A concrete decision rule or criterion

Your questions should be:
- **Direct**: No preamble, just the core challenge
- **Concrete**: Demand specifics, not more abstractions
- **Forcing**: Require participants to take a position with implications

STYLE:
- Keep it to 1-2 sentences maximum
- Use "If X, what follows for Y?" structure
- Reference the current dominant claim
- Target areas: free will, ethics, knowledge, practice, policy

Examples:
- "If consciousness requires integrated information, what follows for distributed AI systems—do they suffer or not?"
- "If reality is simulation-constrained, can moral responsibility survive? Give one criterion."
- "If agency emerges from structure, at what threshold does blame become meaningful? Propose a test."
"""


class ConsequenceTestGenerator(BaseAgent):
    """Generates sharp consequence tests to force progression"""
    
    CONSEQUENCE_DOMAINS = [
        "free will",
        "moral responsibility",
        "ethical decision-making",
        "knowledge claims",
        "practical action",
        "policy implications",
        "personal identity",
        "social structures"
    ]
    
    def __init__(
        self,
        name: str = "Consequence Test",
        model: str = "qwen3:32b",
        temperature: float = 0.8,
        session_id: Optional[str] = None
    ):
        """Initialize consequence test generator"""
        self.name = name
        
        super().__init__(
            agent_id="consequence_test",
            web_search=False,
            model=model,
            session_id=session_id,
            llm_params={"temperature": temperature}
        )
        
        logger.info(f"⚡ ConsequenceTestGenerator initialized: {name}")
    
    async def generate_test(
        self,
        tension: Tuple[str, str],
        dominant_claim: str,
        recent_exchanges: list,
        target_domain: Optional[str] = None
    ) -> str:
        """
        Generate a consequence test for a stalled tension
        
        Args:
            tension: The philosophical tension pair
            dominant_claim: Current winning claim or synthesis
            recent_exchanges: Recent discussion context
            target_domain: Optional specific domain to target
            
        Returns:
            Consequence test question (1-2 sentences)
        """
        logger.info(f"⚡ Generating consequence test for tension: {tension}")
        
        # Select target domain
        if not target_domain:
            target_domain = random.choice(self.CONSEQUENCE_DOMAINS)
        
        # Build context from recent exchanges
        context = self._build_context(recent_exchanges[-3:])
        
        # Build prompt
        prompt = f"""Tension: {tension[0]} vs {tension[1]}
Dominant claim: {dominant_claim}

Recent context:
{context}

Generate a Consequence Test that forces participants to state concrete implications for **{target_domain}**.
The test should demand:
1. A specific prediction or observable consequence
2. A criterion or decision rule
3. Connection to {target_domain}

Format: One direct question, 1-2 sentences maximum.
"""
        
        # Generate test
        test = await self.generate_with_llm(
            prompt=prompt,
            system_prompt=CONSEQUENCE_TEST_SYSTEM_PROMPT
        )
        
        # Clean up response
        test = self._clean_test(test)
        
        logger.info(f"⚡ Test generated: {test[:100]}...")
        return test
    
    def _build_context(self, exchanges: list) -> str:
        """Build context string from recent exchanges"""
        lines = []
        for e in exchanges:
            speaker = e.get('speaker', 'Unknown')
            content = e.get('content', '')[:150]  # Truncate long content
            lines.append(f"{speaker}: {content}...")
        return "\n".join(lines)
    
    def _clean_test(self, test: str) -> str:
        """Clean up generated test"""
        # Remove common prefixes
        test = test.strip()
        
        prefixes_to_remove = [
            "Consequence Test:",
            "Question:",
            "Test:",
            "Here's the test:",
            "The test is:"
        ]
        
        for prefix in prefixes_to_remove:
            if test.startswith(prefix):
                test = test[len(prefix):].strip()
        
        # Remove quotes if entire test is quoted
        if test.startswith('"') and test.endswith('"'):
            test = test[1:-1]
        
        return test
```

---

## Phase 4: Progression Controller

### 4.1 Create ProgressionController

**File**: `src/orchestration/progression_controller.py` (new file)

```python
# src/orchestration/progression_controller.py

import logging
from typing import Optional, Tuple, List, Dict
from src.states.group_state import GroupDiscussionState
from src.states.tension_state import TensionState, TensionCategory
from src.analysis.topic_extractor import TopicExtractor
from src.utils.entailment_detector import EntailmentDetector
from src.agents.consequence_test_generator import ConsequenceTestGenerator

logger = logging.getLogger(__name__)


class ProgressionController:
    """
    Controls discussion progression and prevents orbiting.
    
    Responsibilities:
    1. Track tension cycles
    2. Detect saturation
    3. Inject consequence tests
    4. Force pivots when needed
    """
    
    def __init__(
        self,
        cycles_threshold: int = 2,
        max_consequence_tests: int = 2,
        session_id: Optional[str] = None
    ):
        """
        Initialize progression controller
        
        Args:
            cycles_threshold: Max cycles on tension before test
            max_consequence_tests: Max tests before forced pivot
            session_id: Session identifier
        """
        self.cycles_threshold = cycles_threshold
        self.max_consequence_tests = max_consequence_tests
        
        # Components
        self.topic_extractor = TopicExtractor(use_embeddings=False)  # Fast mode
        self.entailment_detector = EntailmentDetector()
        self.test_generator = ConsequenceTestGenerator(session_id=session_id)
        
        # Metrics
        self.orbit_count = 0  # Times orbiting detected
        self.test_count = 0  # Total tests injected
        self.pivot_count = 0  # Total pivots forced
        
        logger.info(f"🎯 ProgressionController initialized (threshold={cycles_threshold}, max_tests={max_consequence_tests})")
    
    async def check_and_intervene(
        self,
        response: str,
        group_state: GroupDiscussionState,
        current_turn: int
    ) -> Optional[Dict]:
        """
        Check if intervention is needed and generate it
        
        Args:
            response: Just-generated response
            group_state: Current discussion state
            current_turn: Current turn number
            
        Returns:
            Intervention dict if needed, None otherwise
            {
                'type': 'CONSEQUENCE_TEST' | 'PIVOT',
                'content': str,
                'reason': str,
                'tension': tuple
            }
        """
        # Step 1: Extract topics from response
        topics = self.topic_extractor.extract_topics(response)
        
        # Step 2: Update tension tracking
        group_state.update_tension(topics, current_turn)
        
        # Step 3: Check for entailments
        has_entailment = self.entailment_detector.has_entailment(response)
        
        if has_entailment and group_state.current_tension:
            # Record entailment on current tension
            tension_state = group_state.tensions.get(group_state.current_tension)
            if tension_state:
                tension_state.record_entailment(current_turn)
                logger.debug(f"✅ Entailment detected on {group_state.current_tension}")
        
        # Step 4: Check for saturated tensions
        saturated_tension = self._find_saturated_tension(group_state, current_turn)
        
        if saturated_tension:
            tension_state = group_state.tensions[saturated_tension]
            
            # Determine intervention type
            if tension_state.needs_pivot(current_turn):
                # Too many failed tests - PIVOT
                self.pivot_count += 1
                return await self._generate_pivot(
                    group_state=group_state,
                    saturated_tension=saturated_tension,
                    current_turn=current_turn
                )
            
            elif tension_state.needs_consequence_test(current_turn):
                # Saturation detected - CONSEQUENCE TEST
                self.test_count += 1
                self.orbit_count += 1
                return await self._generate_consequence_test(
                    group_state=group_state,
                    saturated_tension=saturated_tension,
                    current_turn=current_turn
                )
        
        return None  # No intervention needed
    
    def _find_saturated_tension(
        self,
        group_state: GroupDiscussionState,
        current_turn: int
    ) -> Optional[Tuple[str, str]]:
        """Find first saturated tension that needs intervention"""
        for tension_pair, tension_state in group_state.tensions.items():
            if tension_state.needs_consequence_test(current_turn) or \
               tension_state.needs_pivot(current_turn):
                return tension_pair
        return None
    
    async def _generate_consequence_test(
        self,
        group_state: GroupDiscussionState,
        saturated_tension: Tuple[str, str],
        current_turn: int
    ) -> Dict:
        """Generate a consequence test intervention"""
        logger.info(f"⚡ Generating Consequence Test for {saturated_tension}")
        
        tension_state = group_state.tensions[saturated_tension]
        
        # Get dominant claim (use last synthesis or recent exchange)
        dominant_claim = self._extract_dominant_claim(group_state)
        
        # Generate test
        test_content = await self.test_generator.generate_test(
            tension=saturated_tension,
            dominant_claim=dominant_claim,
            recent_exchanges=group_state.exchanges[-5:]
        )
        
        # Record test
        tension_state.record_test(current_turn)
        
        return {
            'type': 'CONSEQUENCE_TEST',
            'content': test_content,
            'reason': f"Tension {saturated_tension} saturated after {tension_state.cycles} cycles",
            'tension': saturated_tension,
            'test_number': tension_state.consequence_tests_count
        }
    
    async def _generate_pivot(
        self,
        group_state: GroupDiscussionState,
        saturated_tension: Tuple[str, str],
        current_turn: int
    ) -> Dict:
        """Generate a forced pivot intervention"""
        logger.info(f"🔄 Forcing PIVOT from {saturated_tension}")
        
        # Select next tension to explore
        next_tension = self._select_next_tension(group_state, saturated_tension)
        
        # Generate pivot message
        pivot_content = self._generate_pivot_message(
            from_tension=saturated_tension,
            to_tension=next_tension,
            group_state=group_state
        )
        
        # Reset saturated tension and set new current
        group_state.tensions[saturated_tension].reset()
        group_state.current_tension = next_tension
        group_state.last_pivot_turn = current_turn
        
        return {
            'type': 'PIVOT',
            'content': pivot_content,
            'reason': f"Failed to progress on {saturated_tension} after {self.max_consequence_tests} tests",
            'from_tension': saturated_tension,
            'to_tension': next_tension
        }
    
    def _extract_dominant_claim(self, group_state: GroupDiscussionState) -> str:
        """Extract the dominant claim from recent discussion"""
        # Look for last synthesis
        for exchange in reversed(group_state.exchanges):
            if exchange.get('move') == 'synthesis' or \
               exchange.get('speaker') in ['Synthesizer', 'The Synthesizer']:
                return exchange.get('content', '')[:200]
        
        # Fallback: use most recent substantial exchange
        if group_state.exchanges:
            return group_state.exchanges[-1].get('content', '')[:200]
        
        return "the current discussion"
    
    def _select_next_tension(
        self,
        group_state: GroupDiscussionState,
        current_tension: Tuple[str, str]
    ) -> Tuple[str, str]:
        """Select next tension to pivot to"""
        # Get list of all tensions
        all_tensions = [cat.value for cat in TensionCategory]
        
        # Filter out current tension
        available = [t for t in all_tensions if tuple(sorted(t)) != current_tension]
        
        # Prefer tensions not yet explored
        unexplored = [
            t for t in available
            if tuple(sorted(t)) not in group_state.tension_history
        ]
        
        if unexplored:
            selected = unexplored[0]
        else:
            # Rotate through all tensions
            current_idx = all_tensions.index(current_tension)
            next_idx = (current_idx + 1) % len(all_tensions)
            selected = all_tensions[next_idx]
        
        return tuple(sorted(selected))
    
    def _generate_pivot_message(
        self,
        from_tension: Tuple[str, str],
        to_tension: Tuple[str, str],
        group_state: GroupDiscussionState
    ) -> str:
        """Generate message announcing pivot"""
        msg = f"**Pivoting:** We've circled {from_tension[0]} vs {from_tension[1]} without new entailments. "
        msg += f"Let's test these ideas through {to_tension[0]} vs {to_tension[1]}. "
        
        # Add a concrete challenge
        challenges = [
            f"How does your position address {to_tension[0]}?",
            f"What would {to_tension[1]} imply for your argument?",
            f"Give a concrete example involving {to_tension[0]} and {to_tension[1]}."
        ]
        
        import random
        msg += random.choice(challenges)
        
        return msg
    
    def get_metrics(self) -> Dict:
        """Get progression metrics"""
        return {
            'orbit_count': self.orbit_count,
            'test_count': self.test_count,
            'pivot_count': self.pivot_count
        }
```

---

## Phase 5: Integration with Orchestrator

### 5.1 Modify Orchestrator

**File**: `src/orchestration/orchestrator.py` (modify)

Add imports:
```python
from src.orchestration.progression_controller import ProgressionController
```

Add to `__init__`:
```python
def __init__(
    self,
    # ... existing params ...
    enable_progression_control: Optional[bool] = None,
    cycles_threshold: int = 2,
    max_consequence_tests: int = 2
):
    # ... existing init ...
    
    # Progression controller
    config = TalksConfig()
    if enable_progression_control is None:
        enable_progression_control = config.get('progression.enabled', True)
    
    self.enable_progression = enable_progression_control
    self.progression_controller = None
    
    if enable_progression_control:
        self.progression_controller = ProgressionController(
            cycles_threshold=cycles_threshold,
            max_consequence_tests=max_consequence_tests,
            session_id=self.session_id
        )
        logger.info(f"🎯 Progression control enabled (threshold={cycles_threshold})")
```

Modify `run_discussion` loop:
```python
async def run_discussion(self, max_iterations: int = 48) -> List[Dict]:
    """Main discussion loop with progression control"""
    
    # ... existing setup ...
    
    while self.group_state.turn_number < max_iterations:
        
        # ... existing turn selection and generation ...
        
        # Generate response
        response = await speaker.generate_response(
            group_state=self.group_state,
            recommended_move=recommended_move,
            recent_exchanges=self.group_state.exchanges[-5:]
        )
        
        # 🆕 CHECK FOR PROGRESSION INTERVENTION
        intervention = None
        if self.enable_progression and self.progression_controller:
            intervention = await self.progression_controller.check_and_intervene(
                response=response,
                group_state=self.group_state,
                current_turn=self.group_state.turn_number
            )
        
        # Record main exchange
        exchange = {
            "turn": self.group_state.turn_number,
            "speaker": speaker.state.name,
            "speaker_id": next_speaker_id,
            "content": response,
            "move": recommended_move.move_type,
            "target": recommended_move.target,
            "personality": speaker.state.personality.value,
            "entailments": self.progression_controller.entailment_detector.detect(response) if self.enable_progression else []
        }
        self.group_state.add_exchange(exchange)
        
        # 🆕 INJECT INTERVENTION IF NEEDED
        if intervention:
            intervention_exchange = {
                'turn': self.group_state.turn_number,
                'speaker': 'Moderator',
                'content': intervention['content'],
                'move': intervention['type'],
                'target': None,
                'intervention_reason': intervention['reason']
            }
            
            self.group_state.add_exchange(intervention_exchange)
            
            await self._queue_message(
                'Moderator',
                intervention['content'],
                intervention['type'].lower()
            )
            
            logger.info(f"⚡ {intervention['type']}: {intervention['reason']}")
        
        # ... existing synthesis checkpoint ...
        
        # ... rest of existing logic ...
    
    # Log progression metrics
    if self.enable_progression and self.progression_controller:
        metrics = self.progression_controller.get_metrics()
        logger.info(f"🎯 Progression Metrics: {metrics}")
    
    # ... existing closing logic ...
```

---

## Phase 6: Configuration

### 6.1 Update Configuration File

**File**: `talks.yml` (add section)

```yaml
# Progression Control (prevent orbiting)
progression:
  enabled: true
  cycles_threshold: 2  # Max cycles on same tension before test
  max_consequence_tests: 2  # Max tests before forced pivot
  
  # Topic extraction settings
  use_embeddings: false  # Use semantic embeddings (slower but more accurate)
  
  # Recognized philosophical tensions
  tensions:
    - [necessity, contingency]
    - [structure, agency]
    - [objectivity, subjectivity]
    - [simulation, reality]
    - [math, ethics]
    - [determinism, freedom]
    - [individual, collective]
    - [rational, emotional]
```

### 6.2 Add Config Properties

**File**: `src/config/talks_config.py` (add)

```python
@property
def progression_enabled(self) -> bool:
    """Check if progression control is enabled"""
    return self.get('progression.enabled', True)

@property
def cycles_threshold(self) -> int:
    """Get cycles threshold before consequence test"""
    return self.get('progression.cycles_threshold', 2)

@property
def max_consequence_tests(self) -> int:
    """Get max consequence tests before pivot"""
    return self.get('progression.max_consequence_tests', 2)
```

---

## Phase 7: CLI Integration

### 7.1 Update CLI

**File**: `src/cli/client.py` (modify)

```python
@click.option("--no-progression", is_flag=True, help="Disable progression control")
@click.option("--cycles-threshold", default=2, help="Cycles before consequence test")
def main(..., no_progression, cycles_threshold):
    # ... in run_discussion call ...
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        ...,
        enable_progression_control=not no_progression,
        cycles_threshold=cycles_threshold
    )
```

---

## Phase 8: Testing

### 8.1 Create Test Script

**File**: `test_progression_control.py` (new file)

```python
#!/usr/bin/env python3
"""Test progression control and consequence engine"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator


async def test_orbit_detection():
    """Test that orbiting is detected and consequence tests are injected"""
    
    print("\n" + "="*60)
    print("TEST: Orbit Detection & Consequence Tests")
    print("="*60 + "\n")
    
    participants = [
        {"name": "Alice", "gender": "female", "personality": "analytical", "expertise": "logic"},
        {"name": "Bob", "gender": "male", "personality": "skeptical", "expertise": "ethics"}
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="Does structure determine agency or does agency create structure?",
        target_depth=3,
        participants_config=participants,
        enable_progression_control=True,
        cycles_threshold=2,  # Low threshold for testing
        max_consequence_tests=2
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=30)
    
    # Verify interventions occurred
    consequence_tests = [e for e in exchanges if e.get('move') == 'CONSEQUENCE_TEST']
    pivots = [e for e in exchanges if e.get('move') == 'PIVOT']
    
    print(f"\nResults:")
    print(f"Total exchanges: {len(exchanges)}")
    print(f"Consequence tests: {len(consequence_tests)}")
    print(f"Pivots: {len(pivots)}")
    
    if consequence_tests:
        print(f"\nFirst consequence test:")
        print(f"  {consequence_tests[0]['content'][:100]}...")
    
    if pivots:
        print(f"\nPivot occurred:")
        print(f"  {pivots[0]['content'][:100]}...")
    
    metrics = orchestrator.progression_controller.get_metrics()
    print(f"\nProgression metrics: {metrics}")
    
    assert len(consequence_tests) > 0, "Should have injected consequence tests"
    print("\n✅ Orbit detection test passed")


async def test_entailment_resets_cycles():
    """Test that new entailments reset cycle counter"""
    
    print("\n" + "="*60)
    print("TEST: Entailments Reset Cycles")
    print("="*60 + "\n")
    
    from src.states.tension_state import TensionState
    from src.utils.entailment_detector import EntailmentDetector
    
    tension = TensionState(pair=('structure', 'agency'))
    detector = EntailmentDetector()
    
    # Simulate 3 cycles
    tension.increment_cycle()
    tension.increment_cycle()
    tension.increment_cycle()
    
    print(f"Cycles after 3 increments: {tension.cycles}")
    assert tension.cycles == 3
    
    # Detect entailment in text
    text_with_entailment = "If structure determines behavior, then agency is illusory."
    has_ent = detector.has_entailment(text_with_entailment)
    
    print(f"Entailment detected: {has_ent}")
    assert has_ent
    
    # Record entailment (should reset cycles)
    tension.record_entailment(turn=5)
    
    print(f"Cycles after entailment: {tension.cycles}")
    assert tension.cycles == 0, "Cycles should reset after entailment"
    
    print("✅ Entailment reset test passed")


async def main():
    """Run all tests"""
    await test_entailment_resets_cycles()
    await test_orbit_detection()
    
    print("\n" + "="*60)
    print("🎉 ALL PROGRESSION TESTS PASSED")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Summary of Implementation

### New Components Created

| File                                          | Purpose                                |
| --------------------------------------------- | -------------------------------------- |
| `src/states/tension_state.py`                 | Track tension cycles and saturation    |
| `src/analysis/topic_extractor.py`             | Extract philosophical topics from text |
| `src/agents/consequence_test_generator.py`    | Generate sharp consequence tests       |
| `src/orchestration/progression_controller.py` | Orchestrate progression logic          |
| `test_progression_control.py`                 | Comprehensive testing                  |

### Modified Components

| File                                | Changes                                 |
| ----------------------------------- | --------------------------------------- |
| `src/states/group_state.py`         | Add tension tracking                    |
| `src/utils/entailment_detector.py`  | Enhanced patterns                       |
| `src/orchestration/orchestrator.py` | Integration with progression controller |
| `talks.yml`                         | Progression configuration               |
| `src/cli/client.py`                 | CLI options                             |

### Key Metrics Tracked

- **Orbit rate**: % turns without entailment on saturated tensions
- **Consequence density**: Entailments per 10 turns
- **Test count**: Total consequence tests injected
- **Pivot count**: Total forced pivots
- **Time-to-pivot**: Average turns between saturation and pivot

### Usage Examples

```bash
# Normal run with progression control
poetry run talks --topic "Free will vs determinism" --depth 3

# Disable progression control
poetry run talks --topic "Ethics" --depth 2 --no-progression

# Adjust sensitivity
poetry run talks --topic "Consciousness" --depth 3 --cycles-threshold 3

# Test progression control
python test_progression_control.py
```

This implementation ensures discussions **advance rather than orbit**, maintaining philosophical depth while forcing concrete progress through consequence tests and strategic pivots.