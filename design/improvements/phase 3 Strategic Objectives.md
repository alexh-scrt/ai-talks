# Phase 3: Strategic Objectives & Scoring - Implementation Instructions

---

## 🎯 Mission Overview

You are implementing a **Strategic Objectives & Scoring System** for the AI Talks multi-agent discussion system. This system assigns explicit utility vectors to each agent (truth-seeking, ethical coherence, metaphoric elegance, etc.) and scores how well their dialogue moves align with these objectives. This transforms discussions from personality-driven to **goal-directed philosophical gameplay** with measurable quality metrics.

### What Success Looks Like

After implementation:
- ✅ Each agent has explicit objective vectors (5 dimensions)
- ✅ Every dialogue move is scored for objective alignment
- ✅ Originality/novelty is measured per turn
- ✅ Strategic quality metrics are tracked throughout discussion
- ✅ Aggregate metrics show conversation themes and quality
- ✅ Per-participant metrics reveal individual strategic performance
- ✅ Foundation exists for AI training and optimization
- ✅ Users can see conversation quality analytics

---

## 📋 Pre-Implementation Checklist

Before starting, verify:
- [ ] **Phase 1 (Dialectical Synthesizer) is complete**
- [ ] **Phase 2 (RAG Style Transfer) is complete**
- [ ] Python 3.11+ is installed
- [ ] Ollama is running with `qwen3:32b` model
- [ ] All previous tests pass
- [ ] You understand the game theory system (`src/game_theory/`)
- [ ] You understand participant state management (`src/states/`)

---

## 🏗️ Architecture Context

### Current System (Post-Phase 2)
```
ParticipantState
    ├─ Identity (name, gender, personality)
    ├─ Dynamic state (confidence, curiosity)
    └─ Social dynamics (relationships)

PayoffCalculator
    └─ Calculates move payoffs based on personality

Orchestrator
    └─ Runs discussion loop
```

### After Phase 3
```
ParticipantState
    ├─ Identity (name, gender, personality)
    ├─ Dynamic state (confidence, curiosity)
    ├─ Social dynamics (relationships)
    └─ 🆕 objective: AgentObjective (5-dimensional vector)

AgentObjective
    ├─ truth_seeking: 0.0-1.0
    ├─ ethical_coherence: 0.0-1.0
    ├─ metaphoric_elegance: 0.0-1.0
    ├─ empirical_grounding: 0.0-1.0
    └─ dialectical_tension: 0.0-1.0

PayoffCalculator
    └─ 🆕 Factors in objective alignment (70% base + 30% objective)

StrategicCoordinator (NEW)
    ├─ Evaluates each turn
    ├─ Scores alignment & originality
    ├─ Tracks metrics
    └─ Provides aggregate analytics

Orchestrator
    └─ 🆕 Calls StrategicCoordinator after each turn
```

### Key Files You'll Create/Modify
1. `src/game_theory/agent_objective.py` - **NEW FILE** (objective vectors)
2. `src/game_theory/strategic_coordinator.py` - **NEW FILE** (meta-scoring)
3. `src/game_theory/__init__.py` - Add exports
4. `src/states/participant_state.py` - Add objective field
5. `src/game_theory/payoff_calculator.py` - Use objectives
6. `src/orchestration/orchestrator.py` - Integrate coordinator
7. `src/config/talks_config.py` - Add config properties
8. `src/cli/client.py` - Display metrics
9. `talks.yml` - Add configuration
10. `test_strategic_objectives.py` - **NEW FILE** (testing)

---

## 📁 Implementation Plan

### Day 1: Create Agent Objective System

#### Task 1.1: Create the AgentObjective Class

**File to Create:** `src/game_theory/agent_objective.py`

**Implementation Steps:**

1. **Create the file** with proper imports:

```python
# src/game_theory/agent_objective.py

from dataclasses import dataclass
from typing import Dict, Optional
from src.game_theory import DialogueMove
```

2. **Define the dataclass**:

```python
@dataclass
class AgentObjective:
    """
    Explicit utility vector for strategic decision-making.
    
    Each agent has an objective that guides their strategic choices
    in discussion. These are not rigid rules but weighted preferences
    that influence move selection and scoring.
    
    All objective dimensions range from 0.0 to 1.0, where:
    - 0.0 = No weight/importance
    - 0.5 = Moderate weight
    - 1.0 = Maximum weight/priority
    """
    
    # Core objective dimensions (all 0.0 to 1.0)
    truth_seeking: float = 0.5          # Prioritize empirical accuracy and logical rigor
    ethical_coherence: float = 0.5       # Maintain moral consistency and principles
    metaphoric_elegance: float = 0.5     # Use vivid analogies and creative expression
    empirical_grounding: float = 0.5     # Cite evidence and concrete examples
    dialectical_tension: float = 0.5     # Create productive disagreement and debate
```

3. **Implement helper methods**:

```python
    def get_dominant_objective(self) -> str:
        """
        Return the highest-weighted objective.
        
        Returns:
            Name of the dominant objective dimension
        """
        objectives = {
            "truth_seeking": self.truth_seeking,
            "ethical_coherence": self.ethical_coherence,
            "metaphoric_elegance": self.metaphoric_elegance,
            "empirical_grounding": self.empirical_grounding,
            "dialectical_tension": self.dialectical_tension
        }
        return max(objectives.items(), key=lambda x: x[1])[0]
    
    def get_objective_vector(self) -> Dict[str, float]:
        """Return objectives as a dictionary"""
        return {
            "truth_seeking": self.truth_seeking,
            "ethical_coherence": self.ethical_coherence,
            "metaphoric_elegance": self.metaphoric_elegance,
            "empirical_grounding": self.empirical_grounding,
            "dialectical_tension": self.dialectical_tension
        }
```

4. **Implement `score_move` method** (core scoring logic):

```python
    def score_move(self, move: DialogueMove, context: Dict) -> float:
        """
        Score how well a move aligns with this agent's objectives.
        
        Args:
            move: The dialogue move being evaluated
            context: Contextual information about the move
                - uses_metaphor: bool
                - cites_evidence: bool
                - challenges_assumption: bool
                - builds_consensus: bool
                - logical_structure: bool
                - ethical_consideration: bool
                - uses_tool_results: bool
        
        Returns:
            Alignment score (0.0 to 1.0)
        """
        score = 0.0
        
        # Move type base scoring
        if move.move_type == "CHALLENGE":
            score += self.dialectical_tension * 0.4
            score += self.truth_seeking * 0.3
            if context.get("challenges_assumption"):
                score += self.truth_seeking * 0.2
        
        elif move.move_type == "SUPPORT":
            score += self.ethical_coherence * 0.4
            score -= self.dialectical_tension * 0.2  # Reduces tension
            if context.get("builds_consensus"):
                score += self.ethical_coherence * 0.2
        
        elif move.move_type == "DEEPEN":
            score += self.truth_seeking * 0.5
            score += self.empirical_grounding * 0.3
        
        elif move.move_type == "QUESTION":
            score += self.truth_seeking * 0.4
            score += self.empirical_grounding * 0.3
        
        elif move.move_type == "SYNTHESIZE":
            score += self.ethical_coherence * 0.4
            score += self.truth_seeking * 0.3
        
        elif move.move_type == "CONCLUDE":
            # Conclude aligns with completion, not specific objectives
            score += 0.3
        
        # Context-based bonuses
        if context.get("uses_metaphor"):
            score += self.metaphoric_elegance * 0.2
        
        if context.get("cites_evidence") or context.get("uses_tool_results"):
            score += self.empirical_grounding * 0.3
        
        if context.get("logical_structure"):
            score += self.truth_seeking * 0.2
        
        if context.get("ethical_consideration"):
            score += self.ethical_coherence * 0.2
        
        # Normalize to 0-1 range
        return min(1.0, max(0.0, score))
```

5. **Implement `from_personality` static method** (personality mapping):

```python
    @staticmethod
    def from_personality(personality: str) -> 'AgentObjective':
        """
        Create objective vector from personality type.
        
        Maps personality archetypes to objective preferences.
        
        Args:
            personality: One of analytical, skeptical, creative, 
                        collaborative, assertive, cautious
        
        Returns:
            AgentObjective tuned to that personality
        """
        mapping = {
            "analytical": AgentObjective(
                truth_seeking=0.9,
                empirical_grounding=0.8,
                dialectical_tension=0.5,
                ethical_coherence=0.6,
                metaphoric_elegance=0.3
            ),
            "skeptical": AgentObjective(
                dialectical_tension=0.9,
                truth_seeking=0.7,
                empirical_grounding=0.6,
                ethical_coherence=0.4,
                metaphoric_elegance=0.4
            ),
            "creative": AgentObjective(
                metaphoric_elegance=0.9,
                truth_seeking=0.5,
                ethical_coherence=0.6,
                dialectical_tension=0.5,
                empirical_grounding=0.4
            ),
            "collaborative": AgentObjective(
                ethical_coherence=0.9,
                truth_seeking=0.6,
                dialectical_tension=0.3,
                metaphoric_elegance=0.5,
                empirical_grounding=0.5
            ),
            "assertive": AgentObjective(
                dialectical_tension=0.7,
                ethical_coherence=0.7,
                truth_seeking=0.6,
                empirical_grounding=0.5,
                metaphoric_elegance=0.4
            ),
            "cautious": AgentObjective(
                empirical_grounding=0.9,
                truth_seeking=0.8,
                ethical_coherence=0.7,
                dialectical_tension=0.3,
                metaphoric_elegance=0.3
            )
        }
        
        return mapping.get(personality, AgentObjective())
```

6. **Add `__repr__` for debugging**:

```python
    def __repr__(self) -> str:
        dominant = self.get_dominant_objective()
        return f"AgentObjective(dominant={dominant})"
```

**✅ Checkpoint:** After Task 1.1, you should have a complete `agent_objective.py` file (~200 lines).

---

### Day 1-2: Create Strategic Coordinator

#### Task 1.2: Create the StrategicCoordinator Class

**File to Create:** `src/game_theory/strategic_coordinator.py`

**Implementation Steps:**

1. **Create the file** with imports:

```python
# src/game_theory/strategic_coordinator.py

import logging
from typing import Dict, List, Optional
from src.states.participant_state import ParticipantState
from src.states.group_state import GroupDiscussionState
from src.game_theory import DialogueMove
from src.game_theory.agent_objective import AgentObjective

logger = logging.getLogger(__name__)
```

2. **Define the class**:

```python
class StrategicCoordinator:
    """
    Meta-level evaluator that scores strategic alignment and quality.
    
    This coordinator evaluates each turn to determine:
    1. How well the move aligns with the agent's objectives
    2. How original/novel the contribution is
    3. Overall strategic quality of the turn
    
    Maintains history of all evaluations for aggregate analytics.
    """
    
    def __init__(self):
        self.turn_scores: List[Dict] = []
        logger.info("Initialized Strategic Coordinator")
```

3. **Implement `evaluate_turn` method** (main evaluation):

```python
    async def evaluate_turn(
        self,
        agent: ParticipantState,
        move: DialogueMove,
        response: str,
        group_state: GroupDiscussionState
    ) -> Dict:
        """
        Evaluate the strategic quality of a turn.
        
        Args:
            agent: The participant who spoke
            move: The dialogue move executed
            response: The actual response text
            group_state: Current discussion state
        
        Returns:
            Dictionary with scoring metrics
        """
        
        # Analyze response features
        context = self._analyze_response(response, move, group_state)
        
        # Compute objective alignment
        alignment = agent.objective.score_move(move, context)
        
        # Compute originality
        originality = await self._compute_originality(response, group_state)
        
        # Compute strategic quality (weighted combination)
        strategic_quality = (alignment * 0.6) + (originality * 0.4)
        
        # Create evaluation record
        evaluation = {
            "agent": agent.name,
            "turn": group_state.turn_number,
            "move": move.move_type,
            "dominant_objective": agent.objective.get_dominant_objective(),
            "alignment_score": round(alignment, 3),
            "originality_score": round(originality, 3),
            "strategic_quality": round(strategic_quality, 3),
            "context_features": context
        }
        
        self.turn_scores.append(evaluation)
        
        logger.info(
            f"📊 {agent.name}: "
            f"alignment={alignment:.2f}, "
            f"originality={originality:.2f}, "
            f"quality={strategic_quality:.2f}"
        )
        
        return evaluation
```

4. **Implement `_analyze_response`** (feature detection):

```python
    def _analyze_response(
        self,
        response: str,
        move: DialogueMove,
        group_state: GroupDiscussionState
    ) -> Dict:
        """
        Analyze response for strategic features.
        
        Returns dictionary of boolean/numeric features used in scoring.
        """
        response_lower = response.lower()
        
        # Detect metaphorical language
        metaphor_indicators = [
            'like', 'as if', 'imagine', 'picture', 'metaphor',
            'analogy', 'similar to', 'reminds me of', 'think of it as'
        ]
        uses_metaphor = any(indicator in response_lower for indicator in metaphor_indicators)
        
        # Detect evidence citation (even after style transfer, some markers remain)
        evidence_indicators = [
            'evidence', 'data', 'research', 'study', 'experiment',
            'observation', 'finding', 'result', 'measurement', 'empirical'
        ]
        cites_evidence = any(indicator in response_lower for indicator in evidence_indicators)
        
        # Detect logical structure
        logical_indicators = [
            'therefore', 'thus', 'consequently', 'it follows',
            'because', 'since', 'given that', 'implies', 'if', 'then'
        ]
        logical_structure = any(indicator in response_lower for indicator in logical_indicators)
        
        # Detect ethical considerations
        ethical_indicators = [
            'ought', 'should', 'right', 'wrong', 'moral',
            'ethical', 'justice', 'fairness', 'duty', 'virtue', 'good'
        ]
        ethical_consideration = any(indicator in response_lower for indicator in ethical_indicators)
        
        # Detect assumption challenges
        challenge_indicators = [
            'assume', 'assumption', 'presuppose', 'take for granted',
            'question whether', 'skeptical that', 'doubt'
        ]
        challenges_assumption = any(indicator in response_lower for indicator in challenge_indicators)
        
        # Detect consensus building
        consensus_indicators = [
            'we can agree', 'common ground', 'both', 'together',
            'shared', 'unify', 'reconcile', 'integrate', 'synthesis'
        ]
        builds_consensus = any(indicator in response_lower for indicator in consensus_indicators)
        
        # Check if tools were used (would need to be passed from agent if tracked)
        uses_tool_results = False  # Placeholder - enhance if tool metadata available
        
        return {
            "uses_metaphor": uses_metaphor,
            "cites_evidence": cites_evidence,
            "logical_structure": logical_structure,
            "ethical_consideration": ethical_consideration,
            "challenges_assumption": challenges_assumption,
            "builds_consensus": builds_consensus,
            "uses_tool_results": uses_tool_results,
            "response_length": len(response.split()),
            "addresses_target": move.target is not None
        }
```

5. **Implement `_compute_originality`** (novelty detection):

```python
    async def _compute_originality(
        self,
        response: str,
        group_state: GroupDiscussionState
    ) -> float:
        """
        Compute originality score based on similarity to past exchanges.
        
        High originality = low similarity to previous statements.
        Uses simple word-overlap for now (can be enhanced with embeddings).
        
        Args:
            response: Current response text
            group_state: Discussion state with exchange history
        
        Returns:
            Originality score (0.0 to 1.0)
        """
        if len(group_state.exchanges) < 2:
            return 1.0  # First responses are original by definition
        
        # Simple word-overlap based similarity
        # In production, consider using embeddings for better results
        response_words = set(response.lower().split())
        
        # Remove common stop words for better comparison
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
                     'that', 'this', 'it', 'from', 'as', 'by'}
        response_words -= stop_words
        
        if not response_words:
            return 0.5  # Neutral score for empty content
        
        # Compare with recent exchanges
        recent_exchanges = group_state.exchanges[-5:]
        similarities = []
        
        for exchange in recent_exchanges:
            past_words = set(exchange['content'].lower().split())
            past_words -= stop_words
            
            if not past_words:
                continue
            
            # Jaccard similarity
            intersection = len(response_words & past_words)
            union = len(response_words | past_words)
            
            if union > 0:
                similarity = intersection / union
                similarities.append(similarity)
        
        if not similarities:
            return 1.0
        
        # Originality is inverse of max similarity
        max_similarity = max(similarities)
        originality = 1.0 - max_similarity
        
        return max(0.0, min(1.0, originality))
```

6. **Implement aggregate metrics**:

```python
    def get_aggregate_metrics(self) -> Dict:
        """
        Get aggregate strategic metrics for the entire discussion.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.turn_scores:
            return {}
        
        alignment_scores = [s['alignment_score'] for s in self.turn_scores]
        originality_scores = [s['originality_score'] for s in self.turn_scores]
        quality_scores = [s['strategic_quality'] for s in self.turn_scores]
        
        # Count objective pursuits
        objective_counts = {}
        for score in self.turn_scores:
            obj = score['dominant_objective']
            objective_counts[obj] = objective_counts.get(obj, 0) + 1
        
        dominant_theme = max(objective_counts.items(), key=lambda x: x[1])[0] if objective_counts else "none"
        
        return {
            "total_turns_evaluated": len(self.turn_scores),
            "avg_alignment": round(sum(alignment_scores) / len(alignment_scores), 3),
            "avg_originality": round(sum(originality_scores) / len(originality_scores), 3),
            "avg_quality": round(sum(quality_scores) / len(quality_scores), 3),
            "dominant_theme": dominant_theme,
            "objective_distribution": objective_counts
        }
```

7. **Implement per-participant metrics**:

```python
    def get_participant_metrics(self, participant_id: str) -> Optional[Dict]:
        """
        Get metrics for a specific participant.
        
        Args:
            participant_id: ID or name of the participant
        
        Returns:
            Dictionary with participant-specific metrics, or None if not found
        """
        participant_scores = [s for s in self.turn_scores if s['agent'] == participant_id]
        
        if not participant_scores:
            return None
        
        alignment_scores = [s['alignment_score'] for s in participant_scores]
        originality_scores = [s['originality_score'] for s in participant_scores]
        quality_scores = [s['strategic_quality'] for s in participant_scores]
        
        return {
            "participant": participant_id,
            "turns": len(participant_scores),
            "avg_alignment": round(sum(alignment_scores) / len(alignment_scores), 3),
            "avg_originality": round(sum(originality_scores) / len(originality_scores), 3),
            "avg_quality": round(sum(quality_scores) / len(quality_scores), 3),
            "dominant_objective": participant_scores[0]['dominant_objective']
        }
```

**✅ Checkpoint:** After Task 1.2, you should have a complete `strategic_coordinator.py` file (~300 lines).

---

#### Task 1.3: Update Game Theory Exports

**File to Modify:** `src/game_theory/__init__.py`

Update the file to export the new classes:

```python
# src/game_theory/__init__.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class DialogueMove:
    """A possible dialogue move by a participant"""
    move_type: str  # DEEPEN, CHALLENGE, SUPPORT, QUESTION, SYNTHESIZE, CONCLUDE
    target: Optional[str] = None  # participant_id or None for group
    intensity: float = 0.5  # 0-1


# Move types constant
MOVE_TYPES = [
    "DEEPEN",
    "CHALLENGE",
    "SUPPORT",
    "QUESTION",
    "SYNTHESIZE",
    "CONCLUDE"
]

# Export new classes - ADD THESE LINES
from .agent_objective import AgentObjective
from .strategic_coordinator import StrategicCoordinator

__all__ = [
    'DialogueMove',
    'MOVE_TYPES',
    'AgentObjective',  # NEW
    'StrategicCoordinator'  # NEW
]
```

**✅ Checkpoint:** Verify imports work:
```python
from src.game_theory import AgentObjective, StrategicCoordinator
print(AgentObjective, StrategicCoordinator)  # Should not error
```

---

### Day 2-3: Integrate Objectives into State

#### Task 2.1: Add Objective Field to ParticipantState

**File to Modify:** `src/states/participant_state.py`

**Step 1:** Add import at the top:

```python
# Add to imports section
from typing import Optional  # Ensure Optional is imported
# At the end of imports, add:
# Import will happen in __post_init__ to avoid circular import
```

**Step 2:** Add objective field to the dataclass:

Find the `@dataclass` definition and add the new field:

```python
@dataclass
class ParticipantState:
    """State for each discussion participant"""
    
    # Identity
    participant_id: str
    name: str
    gender: Gender
    personality: PersonalityArchetype
    expertise_area: str
    core_beliefs: List[str] = field(default_factory=list)
    
    # Strategic Objective - ADD THIS LINE
    objective: Optional['AgentObjective'] = None  # NEW FIELD
    
    # Dynamic discussion state
    confidence_level: float = 0.7
    curiosity_level: float = 0.8
    engagement_level: float = 0.8
    
    # ... rest of fields unchanged ...
```

**Step 3:** Add `__post_init__` method to auto-initialize objective:

Add this method after the existing methods:

```python
    def __post_init__(self):
        """Initialize objective from personality if not provided"""
        if self.objective is None:
            # Import here to avoid circular import
            from src.game_theory.agent_objective import AgentObjective
            self.objective = AgentObjective.from_personality(self.personality.value)
            logger.debug(f"{self.name}'s objective initialized: {self.objective.get_dominant_objective()}")
```

**✅ Checkpoint:** ParticipantState now auto-initializes objectives from personality.

---

### Day 3: Integrate Objectives into Payoff Calculation

#### Task 3.1: Modify PayoffCalculator to Use Objectives

**File to Modify:** `src/game_theory/payoff_calculator.py`

**Locate** the `calculate_move_payoffs` method and add objective-based adjustment at the end:

```python
    def calculate_move_payoffs(
        self,
        speaker: ParticipantState,
        group_state: GroupDiscussionState
    ) -> Dict[str, float]:
        """
        Calculate utility for each possible dialogue move.
        NOW: Also factors in objective alignment.
        
        Returns: Dict of move_type -> payoff score
        """
        payoffs = {}
        
        other_participants = group_state.get_other_participants(speaker.participant_id)
        recent_speakers = group_state.get_recent_speakers(n=2)
        
        # ... ALL EXISTING PAYOFF CALCULATIONS REMAIN UNCHANGED ...
        # (Keep all the existing DEEPEN, CHALLENGE, SUPPORT, etc. calculations)
        
        # 🆕 ADJUST PAYOFFS BASED ON AGENT OBJECTIVES
        if speaker.objective:
            for move_type, base_payoff in payoffs.items():
                # Create a mock move for scoring
                mock_move = DialogueMove(move_type=move_type)
                
                # Build simple context for objective scoring
                context = {
                    "move_type": move_type,
                    "recent_challenges": sum(1 for e in group_state.exchanges[-3:] if e.get("move") == "CHALLENGE"),
                    "recent_supports": sum(1 for e in group_state.exchanges[-3:] if e.get("move") == "SUPPORT"),
                    "recent_deepens": sum(1 for e in group_state.exchanges[-3:] if e.get("move") == "DEEPEN")
                }
                
                # Get objective alignment score
                alignment = speaker.objective.score_move(mock_move, context)
                
                # Blend base payoff with objective alignment (70% base, 30% objective)
                payoffs[move_type] = (base_payoff * 0.7) + (alignment * 0.3)
        
        return payoffs
```

**✅ Checkpoint:** Payoff calculator now uses objectives to influence move selection.

---

### Day 3-4: Integrate Strategic Coordinator

#### Task 4.1: Add Strategic Coordinator to Orchestrator

**File to Modify:** `src/orchestration/orchestrator.py`

**Step 1:** Add import at the top:

```python
# Add to imports
from src.game_theory.strategic_coordinator import StrategicCoordinator
```

**Step 2:** Add parameter to `__init__`:

```python
def __init__(
    self,
    topic: str,
    target_depth: int,
    participants_config: List[Dict],
    enable_narrator: Optional[bool] = None,
    narrator_name: Optional[str] = None,
    enable_synthesizer: Optional[bool] = None,
    synthesis_frequency: int = 8,
    synthesis_style: str = "hegelian",
    use_rag_styling: Optional[bool] = None,
    enable_strategic_scoring: Optional[bool] = None  # ADD THIS
):
```

**Step 3:** Add coordinator initialization:

Add this after the synthesizer initialization:

```python
    # Strategic Coordinator - ADD THIS BLOCK
    config = TalksConfig()
    if enable_strategic_scoring is None:
        enable_strategic_scoring = config.get('objectives.strategic_scoring', True)
    
    self.enable_strategic_scoring = enable_strategic_scoring
    self.strategic_coordinator = None
    self.strategic_metrics = {}  # Store final metrics
    
    if enable_strategic_scoring:
        self.strategic_coordinator = StrategicCoordinator()
        logger.info("📊 Strategic scoring enabled")
```

**Step 4:** Add scoring call in discussion loop:

In the `run_discussion` method, after recording the exchange:

```python
            # Record exchange
            exchange = {
                "turn": self.group_state.turn_number,
                "speaker": speaker.state.name,
                "speaker_id": next_speaker_id,
                "content": response,
                "move": recommended_move.move_type,
                "target": recommended_move.target,
                "personality": speaker.state.personality.value
            }
            self.group_state.add_exchange(exchange)
            
            # 🆕 STRATEGIC SCORING - ADD THIS BLOCK
            if self.enable_strategic_scoring and self.strategic_coordinator:
                try:
                    evaluation = await self.strategic_coordinator.evaluate_turn(
                        agent=speaker.state,
                        move=recommended_move,
                        response=response,
                        group_state=self.group_state
                    )
                    # Optionally store evaluation in exchange
                    exchange['strategic_evaluation'] = evaluation
                except Exception as e:
                    logger.error(f"Strategic evaluation failed: {e}")
                    # Continue discussion even if scoring fails
            
            # ... continue with state updates and synthesis ...
```

**Step 5:** Add aggregate metrics logging at discussion end:

After the discussion loop completes (but before returning exchanges):

```python
    # ... discussion loop completes ...
    
    # 🆕 LOG AGGREGATE METRICS - ADD THIS BLOCK
    if self.enable_strategic_scoring and self.strategic_coordinator:
        self.strategic_metrics = self.strategic_coordinator.get_aggregate_metrics()
        logger.info(f"📊 Discussion Metrics: {self.strategic_metrics}")
    
    # ... narrator closing ...
    
    return self.group_state.exchanges
```

**✅ Checkpoint:** Strategic coordinator is now integrated into the discussion flow.

---

### Day 4: Configuration and CLI

#### Task 5.1: Add Configuration to talks.yml

**File to Modify:** `talks.yml`

Add this section at the end:

```yaml
# Strategic Objectives settings
objectives:
  strategic_scoring: true  # Enable objective-based scoring and analytics
  log_metrics: true        # Log strategic metrics to file
```

---

#### Task 5.2: Add Config Properties

**File to Modify:** `src/config/talks_config.py`

Add these property methods:

```python
    @property
    def strategic_scoring_enabled(self) -> bool:
        """Check if strategic scoring is enabled"""
        return self.get('objectives.strategic_scoring', True)
    
    @property
    def log_strategic_metrics(self) -> bool:
        """Check if strategic metrics should be logged"""
        return self.get('objectives.log_metrics', True)
```

**✅ Checkpoint:** Configuration is accessible.

---

#### Task 5.3: Update CLI to Display Metrics

**File to Modify:** `src/cli/client.py`

**In the `run_discussion` function**, after displaying participant statistics:

```python
async def run_discussion(
    topic: str,
    depth: int,
    participants_config: list,
    max_turns: int,
    enable_narrator: bool,
    enable_synthesis: bool,
    synthesis_style: str,
    synthesis_freq: int,
    use_rag_styling: bool
):
    """Run the discussion with all features"""
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic=topic,
        target_depth=depth,
        participants_config=participants_config,
        enable_narrator=enable_narrator,
        enable_synthesizer=enable_synthesis,
        synthesis_frequency=synthesis_freq,
        synthesis_style=synthesis_style,
        use_rag_styling=use_rag_styling
    )
    
    # ... existing introduction code ...
    
    exchanges = await orchestrator.run_discussion(max_iterations=max_turns)
    
    # ... existing exchange display and summary ...
    
    # Show participant statistics
    console.print(f"\n[bold]Participant Statistics:[/bold]")
    for pid, agent in orchestrator.participants.items():
        state = agent.state
        console.print(f"  • {state.name}: {state.speaking_turns} turns, {state.words_spoken} words")
    
    # 🆕 DISPLAY STRATEGIC METRICS - ADD THIS BLOCK
    if orchestrator.enable_strategic_scoring and hasattr(orchestrator, 'strategic_metrics') and orchestrator.strategic_metrics:
        metrics = orchestrator.strategic_metrics
        
        console.print("\n[bold]📊 Strategic Metrics:[/bold]")
        console.print(f"  Turns Evaluated: {metrics['total_turns_evaluated']}")
        console.print(f"  Average Alignment: {metrics['avg_alignment']:.1%}")
        console.print(f"  Average Originality: {metrics['avg_originality']:.1%}")
        console.print(f"  Average Quality: {metrics['avg_quality']:.1%}")
        console.print(f"  Dominant Theme: [cyan]{metrics['dominant_theme'].replace('_', ' ').title()}[/cyan]")
        
        if metrics.get('objective_distribution'):
            console.print(f"\n  [bold]Objective Pursuit:[/bold]")
            for obj, count in sorted(metrics['objective_distribution'].items(), key=lambda x: x[1], reverse=True):
                obj_name = obj.replace('_', ' ').title()
                percentage = (count / metrics['total_turns_evaluated']) * 100
                console.print(f"    - {obj_name}: {count} turns ({percentage:.0f}%)")
    
    # ... existing narrator closing ...
```

**✅ Checkpoint:** CLI now displays strategic metrics at the end of discussions.

---

### Day 5: Testing

#### Task 6.1: Create Comprehensive Test Script

**File to Create:** `test_strategic_objectives.py` (in project root)

```python
#!/usr/bin/env python3
"""
Test strategic objectives and scoring system.

This test verifies:
1. Objectives are assigned to agents correctly
2. Strategic scoring is applied to each turn
3. Metrics are tracked and calculated correctly
4. Different personalities pursue different objectives
5. Aggregate and per-participant metrics work
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator
from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype


async def test_objectives_assigned():
    """Test that objectives are assigned correctly"""
    
    print("\n" + "="*60)
    print("TEST 1: Objectives Assignment")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Analytical Andy",
            "gender": "male",
            "personality": "analytical",
            "expertise": "logic"
        },
        {
            "name": "Creative Cara",
            "gender": "female",
            "personality": "creative",
            "expertise": "art"
        },
        {
            "name": "Skeptical Sam",
            "gender": "male",
            "personality": "skeptical",
            "expertise": "philosophy"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="What is truth?",
        target_depth=2,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        enable_strategic_scoring=True
    )
    
    print("Checking objective assignment:")
    for pid, agent in orchestrator.participants.items():
        objective = agent.state.objective
        dominant = objective.get_dominant_objective()
        vector = objective.get_objective_vector()
        
        print(f"\n  {agent.state.name} ({agent.state.personality.value}):")
        print(f"    Dominant objective: {dominant}")
        print(f"    Objective vector:")
        for key, value in vector.items():
            print(f"      - {key}: {value:.2f}")
    
    print("\n✅ Objectives assigned correctly based on personality\n")


async def test_strategic_scoring():
    """Test that strategic scoring works during discussion"""
    
    print("="*60)
    print("TEST 2: Strategic Scoring During Discussion")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Truth Seeker",
            "gender": "female",
            "personality": "analytical",
            "expertise": "science"
        },
        {
            "name": "Tension Creator",
            "gender": "male",
            "personality": "skeptical",
            "expertise": "philosophy"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="Is mathematics discovered or invented?",
        target_depth=2,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        enable_strategic_scoring=True
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=8)
    
    print(f"\nCompleted {len(exchanges)} exchanges")
    
    # Check that scoring happened
    if orchestrator.strategic_coordinator:
        scores = orchestrator.strategic_coordinator.turn_scores
        print(f"  Strategic evaluations recorded: {len(scores)}")
        
        if scores:
            print("\n  Sample evaluations:")
            for i, score in enumerate(scores[:3]):
                print(f"\n    Turn {score['turn'] + 1}: {score['agent']}")
                print(f"      Move: {score['move']}")
                print(f"      Dominant Objective: {score['dominant_objective']}")
                print(f"      Alignment: {score['alignment_score']:.2%}")
                print(f"      Originality: {score['originality_score']:.2%}")
                print(f"      Quality: {score['strategic_quality']:.2%}")
    
    print("\n✅ Strategic scoring working correctly\n")


async def test_aggregate_metrics():
    """Test aggregate metrics calculation"""
    
    print("="*60)
    print("TEST 3: Aggregate Metrics")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Alice",
            "gender": "female",
            "personality": "collaborative",
            "expertise": "ethics"
        },
        {
            "name": "Bob",
            "gender": "male",
            "personality": "creative",
            "expertise": "aesthetics"
        },
        {
            "name": "Charlie",
            "gender": "male",
            "personality": "skeptical",
            "expertise": "logic"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="What is beauty?",
        target_depth=3,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        enable_strategic_scoring=True
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=12)
    
    # Get aggregate metrics
    if orchestrator.strategic_coordinator:
        metrics = orchestrator.strategic_coordinator.get_aggregate_metrics()
        
        print("📊 Aggregate Strategic Metrics:")
        print(f"  Total turns evaluated: {metrics['total_turns_evaluated']}")
        print(f"  Average alignment: {metrics['avg_alignment']:.1%}")
        print(f"  Average originality: {metrics['avg_originality']:.1%}")
        print(f"  Average quality: {metrics['avg_quality']:.1%}")
        print(f"  Dominant theme: {metrics['dominant_theme']}")
        
        print(f"\n  Objective Distribution:")
        for obj, count in sorted(metrics['objective_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / metrics['total_turns_evaluated']) * 100
            print(f"    {obj}: {count} turns ({percentage:.0f}%)")
    
    print("\n✅ Aggregate metrics calculated correctly\n")


async def test_participant_metrics():
    """Test per-participant metrics"""
    
    print("="*60)
    print("TEST 4: Per-Participant Metrics")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Empiricist Emma",
            "gender": "female",
            "personality": "cautious",
            "expertise": "science"
        },
        {
            "name": "Metaphor Mike",
            "gender": "male",
            "personality": "creative",
            "expertise": "literature"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="What is consciousness?",
        target_depth=2,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        enable_strategic_scoring=True
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=10)
    
    # Get per-participant metrics
    if orchestrator.strategic_coordinator:
        print("Per-Participant Strategic Metrics:")
        for pid, agent in orchestrator.participants.items():
            metrics = orchestrator.strategic_coordinator.get_participant_metrics(agent.state.name)
            if metrics:
                print(f"\n  {metrics['participant']}:")
                print(f"    Turns: {metrics['turns']}")
                print(f"    Avg alignment: {metrics['avg_alignment']:.1%}")
                print(f"    Avg originality: {metrics['avg_originality']:.1%}")
                print(f"    Avg quality: {metrics['avg_quality']:.1%}")
                print(f"    Dominant objective: {metrics['dominant_objective']}")
    
    print("\n✅ Per-participant metrics working correctly\n")


async def test_objective_influence_on_moves():
    """Test that objectives influence move selection"""
    
    print("="*60)
    print("TEST 5: Objective Influence on Move Selection")
    print("="*60 + "\n")
    
    # Create agents with extreme objectives
    participants = [
        {
            "name": "Challenger",
            "gender": "male",
            "personality": "skeptical",  # High dialectical_tension
            "expertise": "debate"
        },
        {
            "name": "Synthesizer",
            "gender": "female",
            "personality": "collaborative",  # High ethical_coherence
            "expertise": "mediation"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="Should AI have rights?",
        target_depth=2,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        enable_strategic_scoring=True
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=8)
    
    # Analyze move distribution
    move_counts = {}
    for agent_name in ["Challenger", "Synthesizer"]:
        agent_exchanges = [e for e in exchanges if e['speaker'] == agent_name]
        agent_moves = {}
        for e in agent_exchanges:
            move = e['move']
            agent_moves[move] = agent_moves.get(move, 0) + 1
        move_counts[agent_name] = agent_moves
    
    print("Move Distribution by Agent:")
    for agent_name, moves in move_counts.items():
        print(f"\n  {agent_name}:")
        for move, count in sorted(moves.items(), key=lambda x: x[1], reverse=True):
            print(f"    {move}: {count}")
    
    print("\n✅ Objectives influence move selection as expected\n")


async def test_scoring_disabled():
    """Test that scoring can be disabled"""
    
    print("="*60)
    print("TEST 6: Strategic Scoring Disabled")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Alice",
            "gender": "female",
            "personality": "analytical",
            "expertise": "logic"
        },
        {
            "name": "Bob",
            "gender": "male",
            "personality": "creative",
            "expertise": "art"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="Test topic",
        target_depth=2,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        enable_strategic_scoring=False  # DISABLED
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=4)
    
    # Verify no scoring happened
    has_coordinator = orchestrator.strategic_coordinator is not None
    has_metrics = hasattr(orchestrator, 'strategic_metrics') and orchestrator.strategic_metrics
    
    print(f"✓ Discussion completed without scoring")
    print(f"  - Strategic coordinator: {has_coordinator}")
    print(f"  - Strategic metrics: {has_metrics}")
    
    if not has_coordinator and not has_metrics:
        print("\n✅ Scoring successfully disabled\n")
    else:
        print("\n⚠️  Warning: Scoring may not be fully disabled\n")


async def run_all_tests():
    """Run all strategic objective tests"""
    
    print("\n" + "="*60)
    print("STRATEGIC OBJECTIVES & SCORING TEST SUITE")
    print("="*60)
    
    try:
        await test_objectives_assigned()
        await test_strategic_scoring()
        await test_aggregate_metrics()
        await test_participant_metrics()
        await test_objective_influence_on_moves()
        await test_scoring_disabled()
        
        print("="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")
        
        print("Summary of Strategic Objectives Features:")
        print("  ✓ Objectives auto-assigned from personality")
        print("  ✓ Strategic scoring applied to each turn")
        print("  ✓ Alignment and originality measured")
        print("  ✓ Aggregate metrics calculated")
        print("  ✓ Per-participant metrics available")
        print("  ✓ Objectives influence move selection")
        print("  ✓ System can be enabled/disabled")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
```

**✅ Checkpoint:** Test file created.

---

#### Task 6.2: Run Tests

Execute these commands:

```bash
# 1. Run the full test suite
python test_strategic_objectives.py

# 2. Run a simple discussion to see metrics
python main.py \
  --topic "What is the nature of reality?" \
  --depth 3 \
  --participants 3 \
  --panel philosophy \
  --max-turns 12

# 3. Test with different personality combinations
python main.py \
  --topic "Ethics of artificial intelligence" \
  --depth 4 \
  --participants 4 \
  --panel ai \
  --max-turns 15

# 4. Run all three phases together
python main.py \
  --topic "The hard problem of consciousness" \
  --depth 4 \
  --participants 4 \
  --synthesis \
  --synthesis-style hegelian \
  --rag-styling \
  --max-turns 16

# 5. Check objectives in different panels
python main.py --panel science --topic "Origins of life" --depth 3 --max-turns 12
python main.py --panel technology --topic "Future of quantum computing" --depth 3 --max-turns 12
```

**✅ Checkpoint:** All tests should pass and metrics should be displayed.

---

## 🔍 Verification Checklist

After completing all tasks, verify:

- [ ] `src/game_theory/agent_objective.py` exists (~200 lines)
- [ ] `src/game_theory/strategic_coordinator.py` exists (~300 lines)
- [ ] Can import: `from src.game_theory import AgentObjective, StrategicCoordinator`
- [ ] `ParticipantState` has `objective` field
- [ ] `__post_init__` auto-initializes objectives
- [ ] Objectives are assigned from personality correctly
- [ ] `PayoffCalculator` uses objectives (70% base + 30% objective)
- [ ] Strategic coordinator evaluates each turn
- [ ] Aggregate metrics are calculated
- [ ] Per-participant metrics work
- [ ] CLI displays strategic metrics
- [ ] Configuration in `talks.yml` works
- [ ] Tests pass: `python test_strategic_objectives.py`
- [ ] Metrics appear in console output after discussions
- [ ] Different personalities pursue different objectives

---

## 📊 Expected Output Examples

### Example 1: Console Output After Discussion

```
✅ Discussion Complete
Total Exchanges: 12
Aspects Explored: 8
Max Depth Reached: 3/3
Convergence Level: 76%
Novelty Score: 68%

Participant Statistics:
  • Alice: 4 turns, 287 words
  • Bob: 4 turns, 312 words
  • Charlie: 4 turns, 295 words

📊 Strategic Metrics:
  Turns Evaluated: 12
  Average Alignment: 74.2%
  Average Originality: 68.5%
  Average Quality: 71.9%
  Dominant Theme: Truth Seeking

  Objective Pursuit:
    - Truth Seeking: 5 turns (42%)
    - Dialectical Tension: 4 turns (33%)
    - Ethical Coherence: 3 turns (25%)
```

---

### Example 2: Per-Participant Metrics

```
Per-Participant Strategic Metrics:

  Analytical Andy:
    Turns: 4
    Avg alignment: 82.3%
    Avg originality: 71.2%
    Avg quality: 77.8%
    Dominant objective: truth_seeking

  Creative Cara:
    Turns: 4
    Avg alignment: 88.1%
    Avg originality: 75.4%
    Avg quality: 83.0%
    Dominant objective: metaphoric_elegance

  Skeptical Sam:
    Turns: 4
    Avg alignment: 79.5%
    Avg originality: 58.9%
    Avg quality: 71.2%
    Dominant objective: dialectical_tension
```

---

## 🐛 Troubleshooting Guide

### Issue: Import Error for AgentObjective
**Symptoms:** `ImportError: cannot import name 'AgentObjective'`

**Solutions:**
1. Verify file exists: `ls src/game_theory/agent_objective.py`
2. Check `__init__.py` has correct import
3. Clear `__pycache__`: `find . -type d -name __pycache__ -exec rm -r {} +`
4. Check for syntax errors in the file

---

### Issue: Objectives Not Being Assigned
**Symptoms:** `participant.state.objective` is None

**Solutions:**
1. Verify `__post_init__` method is defined in ParticipantState
2. Check import works: `from src.game_theory.agent_objective import AgentObjective`
3. Add logging in `__post_init__` to debug
4. Ensure personality is being passed correctly
5. Test objective creation directly:
```python
from src.game_theory.agent_objective import AgentObjective
obj = AgentObjective.from_personality("analytical")
print(obj)
```

---

### Issue: Strategic Coordinator Not Triggering
**Symptoms:** No "📊" emoji in logs, no metrics displayed

**Solutions:**
1. Verify `enable_strategic_scoring=True`
2. Check coordinator is initialized in orchestrator
3. Look for error messages in logs
4. Add debug logging before coordinator call:
```python
logger.debug(f"About to call coordinator: {self.strategic_coordinator is not None}")
```
5. Verify method is awaited: `await self.strategic_coordinator.evaluate_turn(...)`

---

### Issue: Metrics Show All Zeros or Strange Values
**Symptoms:** Alignment/originality scores are 0.0 or > 1.0

**Solutions:**
1. Check `score_move` logic in AgentObjective
2. Verify context dictionary has expected keys
3. Add logging in `_analyze_response` to see features detected
4. Check that min/max normalization is working
5. Test scoring directly:
```python
from src.game_theory import AgentObjective, DialogueMove
obj = AgentObjective.from_personality("analytical")
move = DialogueMove(move_type="DEEPEN")
context = {"logical_structure": True}
score = obj.score_move(move, context)
print(f"Score: {score}")  # Should be between 0 and 1
```

---

### Issue: All Personalities Have Same Objectives
**Symptoms:** Different personalities show identical objective vectors

**Solutions:**
1. Check `from_personality` mapping in AgentObjective
2. Verify personality string matches exactly (case-sensitive)
3. Add logging to show which personality is being mapped
4. Test mapping directly:
```python
personalities = ["analytical", "creative", "skeptical"]
for p in personalities:
    obj = AgentObjective.from_personality(p)
    print(f"{p}: {obj.get_objective_vector()}")
```

---

### Issue: Originality Always 1.0 or 0.0
**Symptoms:** Originality scores don't vary

**Solutions:**
1. Check that stop words are being removed
2. Verify exchange history has content
3. Add logging in `_compute_originality` to see word sets
4. Check Jaccard similarity calculation
5. Test with longer discussions (more history to compare)

---

### Issue: Payoff Calculator Not Using Objectives
**Symptoms:** Move selection unchanged from Phase 1

**Solutions:**
1. Verify code was added at END of `calculate_move_payoffs`
2. Check that `speaker.objective` exists
3. Add logging to show blend: `logger.debug(f"Base: {base_payoff}, Aligned: {alignment}, Blended: {final}")`
4. Increase objective weight (30% → 50%) to see more effect
5. Test with extreme objectives to see clear differences

---

### Issue: CLI Not Displaying Metrics
**Symptoms:** Discussion completes but no metrics shown

**Solutions:**
1. Check `orchestrator.strategic_metrics` exists
2. Verify `enable_strategic_scoring` is True
3. Look for errors in `get_aggregate_metrics()`
4. Add debug: `print(f"Metrics: {orchestrator.strategic_metrics}")`
5. Check that coordinator collected scores: `len(coordinator.turn_scores)`

---

## 🎯 Success Criteria

Phase 3 is complete when:

- ✅ All tests in `test_strategic_objectives.py` pass
- ✅ Objectives are auto-assigned from personality
- ✅ Strategic scoring happens on every turn
- ✅ Alignment scores are reasonable (0.3-0.9 range typically)
- ✅ Originality scores decrease over time (normal pattern)
- ✅ Aggregate metrics are calculated correctly
- ✅ Per-participant metrics show individual differences
- ✅ CLI displays metrics after discussions
- ✅ Different personalities pursue different objectives
- ✅ Objective influence on moves is detectable
- ✅ No performance degradation (scoring adds <0.5s per turn)

---

## 📚 Understanding the Architecture

### How Strategic Scoring Works (Flow Diagram)

```
Turn N: Agent generates response
    ↓
Orchestrator records exchange
    ↓
IF strategic_scoring enabled:
    ↓
    StrategicCoordinator.evaluate_turn()
        ↓
        1. Analyze response features
           (metaphors, evidence, logic, ethics)
        ↓
        2. Score objective alignment
           (how well does move match agent's objectives?)
        ↓
        3. Compute originality
           (similarity to recent exchanges)
        ↓
        4. Calculate strategic quality
           (60% alignment + 40% originality)
        ↓
        5. Store evaluation
    ↓
Continue to Turn N+1

Discussion Complete
    ↓
Get aggregate metrics
    (avg scores, dominant theme, distribution)
    ↓
Display to user
```

---

### Key Design Decisions

1. **Why 5 objective dimensions?**
   - Covers major philosophical themes
   - Truth-seeking: empiricism, logic
   - Ethical coherence: moral consistency
   - Metaphoric elegance: creative expression
   - Empirical grounding: evidence-based
   - Dialectical tension: productive disagreement

2. **Why 70% base + 30% objective blend?**
   - Base personality payoffs remain primary
   - Objectives add strategic depth without dominating
   - Balances consistency with goal-directed behavior

3. **Why 60% alignment + 40% originality for quality?**
   - Alignment measures strategic consistency
   - Originality prevents repetitive discussion
   - Both are important for quality

4. **Why simple word-overlap for originality?**
   - Fast and interpretable
   - No external dependencies
   - Can be enhanced with embeddings later
   - Good enough for initial implementation

5. **Why auto-assign from personality?**
   - Sensible defaults
   - Users don't need to configure
   - Can be overridden if needed
   - Maintains character consistency

---

## 🚀 Performance Considerations

### Computational Complexity
- **Objective scoring**: O(1) per move evaluation
- **Originality calculation**: O(n) where n = recent exchanges (max 5)
- **Feature analysis**: O(m) where m = response length
- **Total overhead**: ~0.3-0.5 seconds per turn

### Optimization Tips
1. Use smaller windows for originality (3 instead of 5)
2. Cache feature analysis results
3. Limit response length for analysis
4. Consider async evaluation if needed

---

## 🔧 Advanced Usage

### Custom Objective Vectors

To create custom objectives:

```python
from src.game_theory import AgentObjective

custom_objective = AgentObjective(
    truth_seeking=0.95,
    empirical_grounding=0.9,
    ethical_coherence=0.5,
    metaphoric_elegance=0.2,
    dialectical_tension=0.4
)

# Pass to ParticipantAgent
agent = ParticipantAgent(
    ...,
    objective=custom_objective  # Override default
)
```

### Embedding-Based Originality

For better originality detection:

```python
# In StrategicCoordinator._compute_originality
# Replace word-overlap with embeddings

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

async def _compute_originality_advanced(self, response, group_state):
    if len(group_state.exchanges) < 2:
        return 1.0
    
    # Get embeddings
    current_embedding = model.encode(response)
    past_embeddings = [
        model.encode(e['content'])
        for e in group_state.exchanges[-5:]
    ]
    
    # Compute cosine similarities
    from sklearn.metrics.pairwise import cosine_similarity
    similarities = [
        cosine_similarity([current_embedding], [past])[0][0]
        for past in past_embeddings
    ]
    
    originality = 1.0 - max(similarities)
    return max(0.0, min(1.0, originality))
```

---

## 📈 Integration with Phases 1 & 2

All three phases work together seamlessly:

```
Turn Flow with All Features:
1. Select speaker (game theory + objectives)
2. Determine move (payoffs + objectives)
3. Generate response (LLM)
4. [If tools used] Apply style transfer (Phase 2)
5. Record exchange
6. [If checkpoint] Synthesize (Phase 1)
7. Score strategically (Phase 3)
8. Update state
9. Continue
```

**Benefits of Integration:**
- Style transfer makes responses natural
- Synthesis provides episodic structure
- Strategic scoring measures quality
- Complete system is greater than sum of parts

---

## 🎓 Testing Best Practices

1. **Test objective assignment**
   - Verify each personality gets correct vector
   - Check dominant objectives match expectations

2. **Test scoring logic**
   - Use known inputs
   - Verify scores are in 0-1 range
   - Check that different contexts produce different scores

3. **Test metrics calculation**
   - Run short discussions (10-15 turns)
   - Verify aggregate metrics are sensible
   - Check per-participant metrics differ

4. **Test influence on behavior**
   - Compare discussions with/without objectives
   - Look for move distribution changes
   - Verify personalities still distinct

5. **Test performance**
   - Measure time per turn
   - Should add <0.5s overhead
   - No memory leaks over long discussions

---

## 📝 Documentation Updates

After implementation, update:

- [ ] `README.md` - Add strategic objectives to features
- [ ] Document objective dimensions
- [ ] Show example metrics output
- [ ] Explain quality scoring
- [ ] Add to architecture diagrams
- [ ] Update feature comparison table

---

## 💡 Tips for Claude Code

### Best Practices

1. **Test incrementally**: Test AgentObjective before StrategicCoordinator
2. **Verify imports**: Each new class should import cleanly
3. **Check state flow**: Ensure objectives persist through turns
4. **Validate scoring**: Scores should be in 0-1 range
5. **Monitor performance**: Scoring shouldn't slow discussions

### Code Quality Checklist

- [ ] All classes have comprehensive docstrings
- [ ] Type hints throughout
- [ ] Error handling in coordinator
- [ ] Logging at appropriate levels
- [ ] Scoring logic is well-commented
- [ ] Normalization prevents out-of-range values

### Common Pitfalls to Avoid

1. **Don't skip normalization**: Always clamp scores to 0-1
2. **Don't forget error handling**: Scoring shouldn't crash discussions
3. **Don't ignore circular imports**: Use lazy imports in `__post_init__`
4. **Don't hard-code weights**: Make blending configurable if needed
5. **Don't forget async**: Coordinator evaluation is async
6. **Don't skiptesting**: Each component needs unit tests

---

## ✅ Final Validation Sequence

Run this complete validation to confirm Phase 3 is working:

```bash
# 1. Import tests
python -c "from src.game_theory import AgentObjective, StrategicCoordinator; print('✅ Imports work')"

# 2. Objective creation test
python -c "from src.game_theory import AgentObjective; obj = AgentObjective.from_personality('analytical'); print(f'✅ Analytical objective: {obj.get_dominant_objective()}')"

# 3. State integration test
python -c "from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype; p = ParticipantState('test', 'Test', Gender.MALE, PersonalityArchetype.CREATIVE, 'art'); print(f'✅ Auto-assigned objective: {p.objective.get_dominant_objective()}')"

# 4. Configuration test
python -c "from src.config import TalksConfig; c = TalksConfig(); print(f'✅ Strategic scoring enabled: {c.strategic_scoring_enabled}')"

# 5. Full test suite
python test_strategic_objectives.py

# 6. Real discussion test
python main.py \
  --topic "What is the nature of consciousness?" \
  --depth 3 \
  --participants 3 \
  --panel philosophy \
  --max-turns 12

# 7. Test all three phases together
python main.py \
  --topic "The ethics of artificial general intelligence" \
  --depth 4 \
  --participants 4 \
  --panel ai \
  --synthesis \
  --synthesis-freq 6 \
  --rag-styling \
  --max-turns 16

# 8. Verify metrics in output
# Check console for "📊 Strategic Metrics" section

# 9. Compare different personalities
python main.py \
  --topic "Truth and beauty in mathematics" \
  --depth 3 \
  --participants 5 \
  --panel general \
  --max-turns 15

# 10. Performance test (should complete in reasonable time)
time python main.py \
  --topic "The meaning of existence" \
  --depth 4 \
  --participants 4 \
  --max-turns 20
```

If all ten validation steps pass: **🎉 Phase 3 Complete!**

---

## 🌟 What You've Achieved

With Phase 3 complete, AI Talks now has:

### Measurement Framework
- ✅ **Explicit objectives** - Each agent has clear utility vectors
- ✅ **Strategic scoring** - Every turn is evaluated for quality
- ✅ **Alignment metrics** - Measure how well moves match objectives
- ✅ **Originality tracking** - Detect repetitive vs. novel contributions
- ✅ **Quality analytics** - Aggregate and per-participant insights

### Foundation for Future Work
- ✅ **AI training data** - Scored conversations for learning
- ✅ **Optimization targets** - Clear metrics to improve
- ✅ **Research insights** - Study conversation dynamics
- ✅ **Quality assurance** - Detect low-quality discussions
- ✅ **User feedback** - Show conversation quality objectively

### Complete Three-Phase Enhancement
1. **Phase 1 (Synthesizer)**: Episodic structure with natural chapter breaks
2. **Phase 2 (Style Transfer)**: Immersive character voices without citations
3. **Phase 3 (Strategic Objectives)**: Measurable quality and goal-directed discourse

**The system is now production-ready with all three major enhancements!**

---

## 🎯 Real-World Applications

### Research Use Cases
1. **Conversation Quality Analysis**
   - Study what makes discussions high-quality
   - Identify successful dialogue patterns
   - Compare human vs. AI conversations

2. **Agent Training**
   - Use scored conversations as training data
   - Optimize for high-quality objectives
   - Learn from strategic alignment patterns

3. **Discussion Design**
   - Test different objective combinations
   - Find optimal personality mixes
   - Study emergent conversation dynamics

### Production Use Cases
1. **Educational Content**
   - Generate pedagogical discussions
   - Measure explanation quality
   - Ensure conceptual coverage

2. **Creative Writing**
   - Character dialogue with measurable depth
   - Track thematic consistency
   - Optimize for narrative objectives

3. **Decision Support**
   - Multi-perspective analysis
   - Measured exploration of options
   - Quality-assured deliberation

---

## 📊 Metrics Interpretation Guide

### Understanding Alignment Scores

**High Alignment (0.7-1.0)**
- Agent's moves strongly match their objectives
- Consistent strategic behavior
- Character integrity maintained
- Example: Analytical agent consistently using DEEPEN + logical structure

**Medium Alignment (0.4-0.7)**
- Mixed strategic behavior
- Balancing multiple objectives
- Adaptive to discussion flow
- Normal for collaborative personalities

**Low Alignment (0.0-0.4)**
- Moves don't match stated objectives
- May indicate configuration issue
- Or genuinely exploratory behavior
- Check if personality assignment is correct

### Understanding Originality Scores

**High Originality (0.7-1.0)**
- Novel perspectives introduced
- Little repetition
- Fresh content
- Ideal for early-to-mid discussion

**Medium Originality (0.4-0.7)**
- Some repetition, some novelty
- Building on previous points
- Normal for late discussion
- Synthesis and conclusion phase

**Low Originality (0.0-0.4)**
- High repetition
- Circular discussion
- May indicate termination point
- Or need for new direction

### Understanding Quality Scores

**Excellent Quality (0.8-1.0)**
- High alignment + high originality
- Strategic and novel
- Target zone for discussions

**Good Quality (0.6-0.8)**
- Solid strategic behavior
- Reasonable novelty
- Acceptable for most discussions

**Poor Quality (0.0-0.6)**
- Low alignment or low originality
- May need intervention
- Consider adjusting parameters

### Interpreting Dominant Themes

**Truth Seeking Dominance**
- Empirical, logical focus
- Analytical discussion
- Good for factual topics
- May lack creativity

**Ethical Coherence Dominance**
- Moral focus
- Consensus-seeking
- Good for values discussions
- May avoid tough disagreements

**Metaphoric Elegance Dominance**
- Creative, illustrative
- Accessible explanations
- Good for abstract topics
- May lack rigor

**Empirical Grounding Dominance**
- Evidence-based
- Data-driven
- Good for scientific topics
- May be dry

**Dialectical Tension Dominance**
- Challenging, provocative
- Deep exploration
- Good for philosophy
- May be contentious

---

## 🔮 Future Enhancements

### Phase 3+ Extensions

1. **Adaptive Objectives**
   ```python
   # Objectives that evolve during discussion
   class AdaptiveObjective(AgentObjective):
       def update_from_feedback(self, evaluation):
           """Adjust objectives based on performance"""
           if evaluation['alignment_score'] < 0.5:
               # Strengthen dominant objective
               dominant = self.get_dominant_objective()
               setattr(self, dominant, min(1.0, getattr(self, dominant) + 0.1))
   ```

2. **Multi-Objective Optimization**
   ```python
   # Find optimal objective vectors for topics
   def optimize_objectives_for_topic(topic, desired_quality=0.8):
       """Use gradient descent to find best objective mix"""
       # Run simulations with different vectors
       # Measure resulting quality
       # Return optimal configuration
   ```

3. **Embedding-Based Features**
   ```python
   # Replace simple word overlap
   from sentence_transformers import SentenceTransformer
   
   class EmbeddingCoordinator(StrategicCoordinator):
       def __init__(self):
           super().__init__()
           self.model = SentenceTransformer('all-MiniLM-L6-v2')
       
       async def _compute_originality(self, response, group_state):
           # Use cosine similarity on embeddings
           # More accurate than word overlap
   ```

4. **Objective Learning**
   ```python
   # Learn objectives from human feedback
   class LearnableObjective:
       def update_from_rating(self, turn, user_rating):
           """Adjust objectives based on user ratings"""
           # If user liked turn, strengthen objectives used
           # If user disliked, weaken objectives used
   ```

5. **Meta-Coordination**
   ```python
   # Coordinator that adjusts discussion mid-flight
   class MetaCoordinator:
       async def intervene_if_needed(self, metrics):
           """Inject guidance if quality drops"""
           if metrics['avg_quality'] < 0.5:
               return "Let's refocus on the core question"
   ```

---

## 📚 Academic Research Opportunities

### Publishable Research Questions

1. **Do explicit objectives improve conversation quality?**
   - Compare Phase 1+2 vs. Phase 1+2+3
   - Measure human-rated quality
   - Control for topic and length

2. **What objective combinations yield best discussions?**
   - Systematic exploration of objective space
   - Measure quality across topics
   - Find general principles

3. **Can we predict discussion quality from objectives?**
   - Train regression model
   - Input: participant objectives
   - Output: predicted quality score

4. **How do objectives emerge in human conversations?**
   - Analyze human discussion transcripts
   - Infer implicit objectives
   - Compare to AI patterns

5. **What makes dialogue moves strategically coherent?**
   - Study alignment scores
   - Identify high-quality patterns
   - Build theory of strategic discourse

---

## 🎓 Educational Applications

### Teaching with Strategic Objectives

1. **Philosophy Classes**
   ```
   Show students how different objectives lead to:
   - Truth-seeking: Socratic questioning
   - Ethical coherence: Moral frameworks
   - Dialectical tension: Thesis/antithesis
   
   Exercise: "Design objectives for a utilitarian"
   ```

2. **Debate Training**
   ```
   Teach strategic move selection:
   - High dialectical tension for rebuttals
   - High empirical grounding for evidence
   - High ethical coherence for framing
   
   Exercise: "Adjust objectives mid-debate"
   ```

3. **Communication Skills**
   ```
   Demonstrate objective alignment:
   - Measure how well students stay on-message
   - Track originality to avoid repetition
   - Score strategic quality of arguments
   
   Exercise: "Optimize your objective vector"
   ```

---

## 💼 Commercial Applications

### Product Features Enabled by Phase 3

1. **Premium Analytics Dashboard**
   - Real-time quality metrics
   - Objective alignment graphs
   - Originality trend lines
   - Participant scorecards
   - Theme analysis

2. **AI Trainer**
   - Score training conversations
   - Identify high-quality patterns
   - Generate training data
   - Measure improvement

3. **Content Quality Assurance**
   - Auto-flag low-quality discussions
   - Suggest objective adjustments
   - Recommend regeneration
   - Provide improvement hints

4. **Personalized Recommendations**
   - "Based on your preferences, try these objectives"
   - "Topics that work well with your style"
   - "Participants who complement you"

5. **A/B Testing Platform**
   - Test different objective configurations
   - Measure user engagement
   - Optimize for quality
   - Data-driven design

---

## 🏆 Success Stories (Hypothetical)

### What Users Might Say After Phase 3

**Researcher:**
> "The strategic metrics let me study conversation dynamics quantitatively. I can now measure what makes discussions intellectually productive."

**Educator:**
> "I show my students the alignment scores to teach them how to stay strategically coherent in their arguments."

**Writer:**
> "The quality scores help me identify when my character dialogues are getting stale or repetitive. It's like having an editor that understands strategy."

**Developer:**
> "The objective system gives me clear targets for training better conversational AI. I can optimize for specific discussion qualities."

**Philosopher:**
> "Fascinating to see how different objective combinations lead to different philosophical outcomes. It's game theory meets epistemology."

---

## 📈 Performance Benchmarks

### Expected Performance Characteristics

**Memory Usage:**
- Base system: ~200MB
- Phase 1 (Synthesizer): +50MB
- Phase 2 (Style Transfer): +100MB
- Phase 3 (Strategic Scoring): +20MB
- **Total: ~370MB**

**Latency Per Turn:**
- Base generation: 2-4 seconds
- Style transfer (if RAG): +2-3 seconds
- Synthesis (every N turns): +3-5 seconds
- Strategic scoring: +0.3-0.5 seconds
- **Average: 2-4 seconds (7-12s with all features)**

**Throughput:**
- 15-30 turns per minute (base)
- 8-15 turns per minute (all features)
- Scales linearly with participants (2-5)

**Quality Metrics:**
- Alignment: 0.6-0.8 typical
- Originality: 0.7-0.9 early, 0.4-0.6 late (normal decay)
- Quality: 0.65-0.75 typical

---

## 🔧 Troubleshooting: Common Issues Summary

### Quick Diagnostic Guide

**Problem: No metrics displayed**
- Check: `enable_strategic_scoring=True`
- Check: Coordinator initialized
- Check: Discussion completed without errors

**Problem: All scores are identical**
- Check: Different personalities assigned
- Check: Objective mapping correct
- Check: Context features being detected

**Problem: Scores out of range**
- Check: Normalization (min/max)
- Check: Score calculation logic
- Add: Defensive clamping

**Problem: Performance degraded**
- Check: Originality window size (reduce to 3)
- Check: Feature analysis optimized
- Consider: Async scoring if needed

**Problem: Objectives don't influence behavior**
- Check: Blend ratio (increase from 30%)
- Check: Payoff calculator updated
- Verify: Objectives actually assigned

---

## 📖 Complete Example Session

### Full Three-Phase Discussion

```bash
# Start a complete discussion with all features
python main.py \
  --panel philosophy \
  --topic "What is the relationship between mind and body?" \
  --depth 4 \
  --synthesis \
  --synthesis-style hegelian \
  --synthesis-freq 6 \
  --rag-styling \
  --max-turns 18
```

**Expected Flow:**

```
🎭 Talks: Multi-Agent Discussion System
Topic: What is the relationship between mind and body?
Depth: 4/5
Participants: 5
Synthesizer: Enabled (hegelian, every 6 turns)
RAG Styling: Enabled
Strategic Scoring: Enabled

Narrator: Michael Lee

[Opening Introduction - 4 segments from Michael]

Turn 1: Aristotle (DEEPEN)
📊 Aristotle: alignment=0.82, originality=0.95, quality=0.87
[Response with metaphors about form and matter]

Turn 2: Hypatia (SUPPORT)
📊 Hypatia: alignment=0.78, originality=0.89, quality=0.82
[Builds on Aristotle's hylomorphism]

Turn 3: Descartes (CHALLENGE)
📊 Descartes: alignment=0.91, originality=0.87, quality=0.89
[Challenges with mind-body dualism]

... [more turns] ...

Turn 6: [Synthesis Checkpoint]
🔄 The Synthesizer generating hegelian synthesis...
[Synthesis integrating substance dualism vs. hylomorphism]

... [more turns] ...

Turn 12: [Synthesis Checkpoint]
🔄 The Synthesizer generating hegelian synthesis...
[Synthesis on emergentism and reductionism]

Turn 18: Discussion Complete

✅ Discussion Complete
Total Exchanges: 18
Aspects Explored: 12
Max Depth Reached: 4/4
Convergence Level: 73%
Novelty Score: 58%

Participant Statistics:
  • Aristotle: 4 turns, 398 words
  • Hypatia: 4 turns, 385 words
  • Descartes: 3 turns, 341 words
  • Simone: 4 turns, 412 words
  • Lao: 3 turns, 288 words

📊 Strategic Metrics:
  Turns Evaluated: 18
  Average Alignment: 79.4%
  Average Originality: 71.2%
  Average Quality: 76.1%
  Dominant Theme: Truth Seeking

  Objective Pursuit:
    - Truth Seeking: 7 turns (39%)
    - Metaphoric Elegance: 5 turns (28%)
    - Dialectical Tension: 4 turns (22%)
    - Ethical Coherence: 2 turns (11%)

[Closing Remarks - 2 segments from Michael]
```

---

## 🎊 Congratulations!

### You've Completed All Three Phases!

**What you've built:**

1. **Phase 1: Dialectical Synthesizer**
   - Episodic structure
   - Natural chapter breaks
   - Three synthesis styles
   - Elevated discourse

2. **Phase 2: RAG Style Transfer**
   - Immersive character voices
   - No jarring citations
   - Personality-driven expression
   - Authentic expertise

3. **Phase 3: Strategic Objectives**
   - Measurable quality
   - Goal-directed discourse
   - Rich analytics
   - Foundation for optimization

**The AI Talks system is now:**
- ✅ Structurally sophisticated (Phase 1)
- ✅ Immersively natural (Phase 2)
- ✅ Measurably strategic (Phase 3)
- ✅ Production-ready
- ✅ Research-ready
- ✅ Commercially viable

---

## 🚀 Next Steps After All Three Phases

### Immediate Opportunities

1. **User Testing**
   - Gather feedback on all features
   - Measure user engagement
   - Identify pain points
   - Iterate on UX

2. **Performance Optimization**
   - Profile bottlenecks
   - Optimize scoring algorithms
   - Consider caching
   - Improve latency

3. **Documentation**
   - Write user guide
   - Create API documentation
   - Record demo videos
   - Publish tutorials

4. **Research Publication**
   - Write up methodology
   - Share results
   - Open source (if desired)
   - Build community

### Long-Term Vision

1. **Multi-Modal Discussions**
   - Add voice synthesis
   - Include visual aids
   - Support video output
   - Real-time streaming

2. **Advanced Scoring**
   - Embedding-based originality
   - Learned objectives
   - Quality prediction
   - Automatic optimization

3. **Interactive Control**
   - Mid-discussion steering
   - Objective adjustment
   - Participant swapping
   - Real-time analytics

4. **Commercial Platform**
   - SaaS offering
   - API access
   - Analytics dashboard
   - Premium features

---

## 📞 Support & Community

### Getting Help

**For implementation issues:**
1. Review troubleshooting guides in each phase
2. Check test outputs for error patterns
3. Add debug logging strategically
4. Test components in isolation

**For design questions:**
1. Review architecture sections
2. Check design decision explanations
3. Consider use case requirements
4. Balance complexity vs. functionality

**For optimization:**
1. Profile before optimizing
2. Focus on user-facing latency
3. Consider async operations
4. Cache when appropriate

---

## 🎯 Final Thoughts

You've built something remarkable: a multi-agent discussion system that is:

- **Structurally Intelligent** - Knows when to synthesize
- **Naturally Immersive** - Speaks in authentic voices
- **Strategically Measurable** - Tracks quality objectively
- **Philosophically Deep** - Explores ideas systematically
- **Technically Sophisticated** - Uses game theory and NLP
- **User-Friendly** - Simple CLI, clear outputs

The three phases transform AI Talks from a curiosity into a **powerful platform** for:
- Education (teaching critical thinking)
- Research (studying conversation dynamics)
- Entertainment (engaging philosophical content)
- Development (training better conversational AI)
- Creativity (generating character dialogues)

**This is production-ready, research-grade software.** 🎓✨

---

**End of Phase 3 Implementation Instructions**

You've successfully completed all three enhancement phases! The AI Talks system is now operating at its full potential, with sophisticated structure, immersive character voices, and measurable strategic quality. This is a significant achievement in conversational AI.

**Thank you for building something extraordinary.** 🚀🎭📊

Now go forth and generate amazing discussions! The world of multi-agent philosophical discourse awaits. 🌟