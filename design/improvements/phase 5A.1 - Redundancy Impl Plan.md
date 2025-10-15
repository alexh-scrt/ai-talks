
## Implementation Steps to Mitigate Redundancy & Low Information Yield

### **Phase 1: Add Turn Budget & Dyad Management**

#### 1.1 Create DyadState Tracker
**File**: `src/states/dyad_state.py` (new file)

```python
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class DyadState:
    """Tracks conversation volleys between two agents"""
    pair: Tuple[str, str]
    volleys_used: int = 0
    max_volleys: int = 2
    
    def can_continue(self) -> bool:
        return self.volleys_used < self.max_volleys
    
    def increment(self):
        self.volleys_used += 1
    
    def reset(self):
        self.volleys_used = 0
```

#### 1.2 Add Dyad Tracking to GroupDiscussionState
**File**: `src/states/group_state.py` (modify)

```python
from src.states.dyad_state import DyadState

class GroupDiscussionState:
    def __init__(self, ...):
        # ... existing init ...
        self.dyads: Dict[Tuple[str, str], DyadState] = {}
        self.last_speaker_id: Optional[str] = None
    
    def get_dyad_state(self, speaker_a: str, speaker_b: str) -> DyadState:
        """Get or create dyad state for two speakers"""
        pair = tuple(sorted([speaker_a, speaker_b]))
        if pair not in self.dyads:
            self.dyads[pair] = DyadState(pair=pair, max_volleys=2)
        return self.dyads[pair]
    
    def update_dyad(self, current_speaker: str):
        """Update dyad tracking after a turn"""
        if self.last_speaker_id and self.last_speaker_id != current_speaker:
            dyad = self.get_dyad_state(self.last_speaker_id, current_speaker)
            dyad.increment()
        self.last_speaker_id = current_speaker
```

---

### **Phase 2: Implement Entailment Detection**

#### 2.1 Create Entailment Detector
**File**: `src/utils/entailment_detector.py` (new file)

```python
import re
from typing import List, Set
from enum import Enum

class EntailmentType(Enum):
    IMPLICATION = "implication"
    APPLICATION = "application"
    COUNTEREXAMPLE = "counterexample"
    TEST = "test"

class EntailmentDetector:
    """Detects whether a text contains new entailments"""
    
    PATTERNS = {
        EntailmentType.IMPLICATION: [
            r'\bif\b.*\bthen\b',
            r'\btherefore\b',
            r'\bso that\b',
            r'\bentails\b',
            r'\bmeans that\b',
            r'\bimplies\b',
            r'\bconsequently\b'
        ],
        EntailmentType.APPLICATION: [
            r'\bin practice\b',
            r'\bfor example\b',
            r'\bconsider\b.*\bcase\b',
            r'\btherefore we should\b',
            r'\bwe could apply\b',
            r'\bin the scenario\b'
        ],
        EntailmentType.COUNTEREXAMPLE: [
            r'\bunless\b',
            r'\bexcept when\b',
            r'\bcounterexample\b',
            r'\bnot if\b',
            r'\bhowever\b',
            r'\bbut consider\b'
        ],
        EntailmentType.TEST: [
            r'\bwe could test\b',
            r'\bcriterion\b',
            r'\bmeasure\b',
            r'\bobservable\b',
            r'\beverify by\b',
            r'\bexperiment\b'
        ]
    }
    
    def detect(self, text: str) -> Set[EntailmentType]:
        """Detect entailment types in text"""
        text_lower = text.lower()
        found = set()
        
        for ent_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    found.add(ent_type)
                    break
        
        return found
    
    def has_entailment(self, text: str) -> bool:
        """Check if text has any entailment"""
        return len(self.detect(text)) > 0
```

---

### **Phase 3: Add Semantic Similarity Guard**

#### 3.1 Create Redundancy Checker
**File**: `src/utils/redundancy_checker.py` (new file)

```python
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

class RedundancyChecker:
    """Checks for semantic similarity to detect redundant content"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = similarity_threshold
    
    def is_redundant(self, candidate: str, recent_texts: List[str]) -> bool:
        """Check if candidate is too similar to recent texts"""
        if not recent_texts:
            return False
        
        # Encode all texts
        embeddings = self.model.encode([candidate] + recent_texts)
        candidate_emb = embeddings[0]
        recent_embs = embeddings[1:]
        
        # Compute cosine similarities
        similarities = np.dot(recent_embs, candidate_emb) / (
            np.linalg.norm(recent_embs, axis=1) * np.linalg.norm(candidate_emb)
        )
        
        max_similarity = np.max(similarities)
        return max_similarity >= self.threshold
    
    def get_max_similarity(self, candidate: str, recent_texts: List[str]) -> float:
        """Get maximum similarity score"""
        if not recent_texts:
            return 0.0
        
        embeddings = self.model.encode([candidate] + recent_texts)
        candidate_emb = embeddings[0]
        recent_embs = embeddings[1:]
        
        similarities = np.dot(recent_embs, candidate_emb) / (
            np.linalg.norm(recent_embs, axis=1) * np.linalg.norm(candidate_emb)
        )
        
        return float(np.max(similarities))
```

---

### **Phase 4: Implement Tension State Tracking**

#### 4.1 Create TensionState
**File**: `src/states/tension_state.py` (new file)

```python
from dataclasses import dataclass
from typing import Tuple

@dataclass
class TensionState:
    """Tracks cycles on a specific philosophical tension"""
    pair: Tuple[str, str]  # e.g., ('necessity', 'contingency')
    cycles: int = 0
    last_new_entailment_turn: int = -1
    max_cycles: int = 2
    
    def can_continue(self) -> bool:
        return self.cycles < self.max_cycles
    
    def increment_cycle(self):
        self.cycles += 1
    
    def reset(self):
        self.cycles = 0
    
    def record_entailment(self, turn: int):
        self.last_new_entailment_turn = turn
```

#### 4.2 Add Tension Tracking to GroupDiscussionState
**File**: `src/states/group_state.py` (modify)

```python
from src.states.tension_state import TensionState

class GroupDiscussionState:
    def __init__(self, ...):
        # ... existing init ...
        self.tensions: Dict[Tuple[str, str], TensionState] = {}
        self.current_tension: Optional[Tuple[str, str]] = None
    
    def get_tension_state(self, concept_a: str, concept_b: str) -> TensionState:
        """Get or create tension state"""
        pair = tuple(sorted([concept_a, concept_b]))
        if pair not in self.tensions:
            self.tensions[pair] = TensionState(pair=pair)
        return self.tensions[pair]
```

---

### **Phase 5: Modify Orchestrator to Enforce Policies**

#### 5.1 Add Control Loop in Orchestrator
**File**: `src/orchestration/orchestrator.py` (modify)

Add these methods to the orchestrator class:

```python
from src.utils.entailment_detector import EntailmentDetector, EntailmentType
from src.utils.redundancy_checker import RedundancyChecker

class MultiAgentDiscussionOrchestrator:
    def __init__(self, ...):
        # ... existing init ...
        self.entailment_detector = EntailmentDetector()
        self.redundancy_checker = RedundancyChecker(similarity_threshold=0.85)
        self.max_dyad_volleys = 2
        self.max_tension_cycles = 2
    
    async def _propose_and_refine_turn(
        self,
        speaker: ParticipantAgent,
        recommended_move: DialogueMove,
        context: Dict
    ) -> str:
        """Propose turn with refinement for redundancy and entailments"""
        
        # Get recent exchanges for context
        recent_texts = [
            e['content'] for e in self.group_state.exchanges[-3:]
        ]
        
        max_attempts = 3
        for attempt in range(max_attempts):
            # Generate response
            response = await speaker.generate_response(
                group_state=self.group_state,
                recommended_move=recommended_move,
                recent_exchanges=self.group_state.exchanges[-5:]
            )
            
            # Check 1: Redundancy
            if self.redundancy_checker.is_redundant(response, recent_texts):
                logger.warning(f"Attempt {attempt+1}: Response too similar to recent turns")
                if attempt < max_attempts - 1:
                    # Add instruction to revise
                    context['revision_instruction'] = "Avoid repetition. Add a new entailment or perspective."
                    continue
            
            # Check 2: Entailment requirement
            entailments = self.entailment_detector.detect(response)
            if not entailments:
                logger.warning(f"Attempt {attempt+1}: No new entailments detected")
                if attempt < max_attempts - 1:
                    context['revision_instruction'] = (
                        "Add at least one new entailment: "
                        "implication (if X then Y), application (in case Z), "
                        "counterexample, or test/criterion."
                    )
                    continue
            
            # Success - response passes checks
            logger.debug(f"Turn validated with entailments: {[e.value for e in entailments]}")
            return response
        
        # After max attempts, return best attempt
        logger.warning("Max refinement attempts reached, using last response")
        return response
    
    def _should_force_pivot(self) -> bool:
        """Check if we should force a topic/speaker pivot"""
        
        # Check dyad budget
        if self.group_state.last_speaker_id:
            current_speaker = self.group_state.turn_number
            if len(self.group_state.exchanges) >= 2:
                last_exchange = self.group_state.exchanges[-1]
                current_speaker_id = last_exchange['speaker_id']
                
                if self.group_state.last_speaker_id != current_speaker_id:
                    dyad = self.group_state.get_dyad_state(
                        self.group_state.last_speaker_id,
                        current_speaker_id
                    )
                    if not dyad.can_continue():
                        logger.info(f"🔄 Dyad budget exceeded: forcing pivot")
                        return True
        
        # Check tension cycles
        if self.group_state.current_tension:
            tension = self.group_state.get_tension_state(*self.group_state.current_tension)
            if not tension.can_continue():
                logger.info(f"🔄 Tension cycles exceeded: forcing pivot")
                return True
        
        return False
    
    async def _execute_forced_pivot(self):
        """Execute a forced pivot with new speaker or dilemma"""
        logger.info("Executing forced pivot...")
        
        # Option 1: Introduce a dilemma through the moderator
        if self.narrator and hasattr(self.narrator, 'inject_dilemma'):
            dilemma = await self.narrator.inject_dilemma(
                topic=self.topic,
                recent_exchanges=self.group_state.exchanges[-5:]
            )
            
            dilemma_exchange = {
                'turn': self.group_state.turn_number,
                'speaker': self.narrator.name,
                'content': dilemma,
                'move': 'PIVOT_DILEMMA',
                'addressed_to': None
            }
            self.group_state.add_exchange(dilemma_exchange)
            
            await self._queue_message(
                self.narrator.name,
                dilemma,
                "pivot"
            )
        
        # Reset dyad states
        for dyad in self.group_state.dyads.values():
            dyad.reset()
        
        # Reset current tension
        if self.group_state.current_tension:
            tension = self.group_state.get_tension_state(*self.group_state.current_tension)
            tension.reset()
```

#### 5.2 Integrate into Discussion Loop
**File**: `src/orchestration/orchestrator.py` (modify `run_discussion`)

```python
async def run_discussion(self, max_iterations: int = 48) -> List[Dict]:
    """Main discussion loop with redundancy control"""
    
    # ... existing setup ...
    
    while self.group_state.turn_number < max_iterations:
        
        # Check for forced pivot
        if self._should_force_pivot():
            await self._execute_forced_pivot()
            # Continue to next iteration with fresh state
            continue
        
        # Select next speaker (with dyad awareness)
        next_speaker_id = self.turn_selector.select_next_speaker(self.group_state)
        speaker = self.participants[next_speaker_id]
        
        # ... existing turn logic ...
        
        # Use refined turn generation
        response = await self._propose_and_refine_turn(
            speaker=speaker,
            recommended_move=recommended_move,
            context={}
        )
        
        # Record entailments found
        entailments = self.entailment_detector.detect(response)
        
        exchange = {
            "turn": self.group_state.turn_number,
            "speaker": speaker.state.name,
            "speaker_id": next_speaker_id,
            "content": response,
            "move": recommended_move.move_type,
            "target": recommended_move.target,
            "personality": speaker.state.personality.value,
            "entailments": [e.value for e in entailments]  # Track entailments
        }
        self.group_state.add_exchange(exchange)
        
        # Update dyad state
        self.group_state.update_dyad(next_speaker_id)
        
        # ... existing synthesis checkpoint (keep every 12 turns) ...
        
        # ... rest of existing logic ...
```

---

### **Phase 6: Add Synthesis Cadence Enforcement**

#### 6.1 Modify Synthesis Logic
**File**: `src/orchestration/orchestrator.py` (modify)

```python
# Change synthesis frequency to exactly 12 turns
self.synthesis_frequency = 12  # Fixed per plan

# In the discussion loop, enforce synthesis
if (self.enable_synthesizer and 
    self.group_state.turn_number > 0 and
    self.group_state.turn_number % 12 == 0):  # Every 12 turns exactly
    
    logger.info(f"🔄 MANDATORY Synthesis checkpoint at turn {self.group_state.turn_number}")
    
    synthesis = await self.synthesizer.synthesize_segment(
        exchanges=self.group_state.exchanges,
        turn_window=12,
        topic=self.topic,
        require_next_step=True  # Add this parameter
    )
    
    # Synthesis must include next step
    # Format: "Summary (≤3 sentences). Next: [action]"
    
    # ... rest of synthesis handling ...
```

---

### **Phase 7: Update Configuration**

#### 7.1 Add Config Parameters
**File**: `talks.yml` (modify)

```yaml
# Redundancy Control
redundancy_control:
  enabled: true
  dyad_max_volleys: 2
  tension_max_cycles: 2
  similarity_threshold: 0.85
  require_entailment: true
  synthesis_interval: 12
  max_total_turns: 48

# Entailment Detection
entailment:
  enabled: true
  types:
    - implication
    - application
    - counterexample
    - test
```

---

### **Phase 8: Add CLI Options**

#### 8.1 Update CLI
**File**: `src/cli/client.py` (modify)

```python
@click.option("--max-turns", default=48, help="Maximum turns (default: 48)")
@click.option("--dyad-limit", default=2, help="Max volleys per dyad (default: 2)")
@click.option("--no-redundancy-check", is_flag=True, help="Disable redundancy checking")
def main(..., max_turns, dyad_limit, no_redundancy_check):
    # ... pass to orchestrator ...
```

---

### **Phase 9: Testing**

#### 9.1 Create Test Script
**File**: `test_redundancy_control.py` (new file)

```python
#!/usr/bin/env python3
"""Test redundancy control and information yield"""

import asyncio
from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator

async def test_redundancy_control():
    """Test that redundancy control works"""
    
    participants = [
        {"name": "Alice", "gender": "female", "personality": "analytical", "expertise": "logic"},
        {"name": "Bob", "gender": "male", "personality": "creative", "expertise": "ethics"}
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="The nature of truth",
        target_depth=3,
        participants_config=participants,
        enable_synthesizer=True
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=24)
    
    # Verify constraints
    print(f"Total turns: {len(exchanges)}")
    print(f"Dyad states: {orchestrator.group_state.dyads}")
    
    # Check entailments
    entailment_counts = sum(
        len(e.get('entailments', [])) for e in exchanges
    )
    print(f"Total entailments detected: {entailment_counts}")
    
    # Check synthesis frequency
    synthesis_count = sum(1 for e in exchanges if e['move'] == 'synthesis')
    print(f"Syntheses generated: {synthesis_count} (expected: {len(exchanges)//12})")

if __name__ == "__main__":
    asyncio.run(test_redundancy_control())
```

---

## Summary of Key Changes

| Component              | Action                       | Impact                          |
| ---------------------- | ---------------------------- | ------------------------------- |
| **DyadState**          | Track conversation pairs     | Caps A↔B volleys at 2           |
| **EntailmentDetector** | Validate new content         | Forces meaningful contributions |
| **RedundancyChecker**  | Semantic similarity          | Blocks repetitive turns         |
| **TensionState**       | Track philosophical tensions | Prevents circular arguments     |
| **Orchestrator**       | Enforce all policies         | Coordinates all controls        |
| **Synthesis**          | Fixed 12-turn interval       | Creates predictable structure   |
| **Max Turns**          | Cap at 48                    | Prevents excessive length       |

This implementation maintains your existing architecture while adding targeted controls at the orchestration layer. The key insight is to validate/refine turns **before** they're committed to the exchange log, rather than trying to fix redundancy after the fact.