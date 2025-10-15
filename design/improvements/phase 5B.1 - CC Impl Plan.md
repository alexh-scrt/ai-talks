# Enhanced Cognitive Coda Implementation Plan

## Overview

We'll upgrade your existing simple Cognitive Coda agent to include the mathematical **Structure-Agency-Dependence (S-A-D)** model, making codas:
1. **Measurable** - backed by quantitative signals
2. **Actionable** - with concrete next-step recommendations  
3. **Interpretable** - with equations showing how meaning emerges
4. **Repeatable** - consistent scoring across sessions

---

## Phase 1: Signal Extraction Module

### 1.1 Create Signal Extractors

**File**: `src/analysis/signal_extractors.py` (new file)

```python
# src/analysis/signal_extractors.py

import re
import logging
from typing import List, Dict, Tuple
from collections import Counter
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class SignalExtractor:
    """Extracts S-A-D signals from discussion exchanges"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Regex patterns for feature detection
        self.logic_patterns = [
            r'\bif\b.*\bthen\b',
            r'\btherefore\b',
            r'\bso that\b',
            r'\bentails\b',
            r'\bimplies\b',
            r'\bconsequently\b',
            r'\bhence\b'
        ]
        
        self.agency_patterns = {
            'ought': [r'\bought\b', r'\bshould\b', r'\bmust\b', r'\bchoose\b'],
            'decision': [r'\bI (decide|will|choose|commit)\b', r'\bwe (should|must|will)\b'],
            'consequence': [r'\bwould lead to\b', r'\bresults in\b', r'\bcauses\b'],
            'stance': [r'\bI (believe|assert|claim|hold)\b', r'\bclearly\b', r'\bobviously\b']
        }
        
        self.dependence_patterns = {
            'simulator': [r'\bsimulator\b', r'\bdetermin(ed|ism)\b', r'\bfate\b', r'\bpredetermin\b'],
            'rules': [r'\bhost said\b', r'\bmoderator (required|mandated)\b', r'\bmust follow\b'],
        }
    
    def extract_structure_signals(
        self,
        exchanges: List[Dict],
        window: int = None
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
            if 'retrieved_anchors' in e or 'citations' in e
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
        # For now, use entailment presence as proxy for consistency
        entailment_count = sum(
            1 for e in exchanges
            if e.get('entailments') and len(e['entailments']) > 0
        )
        S_consis = entailment_count / total_turns
        
        # S_focus: topical drift inverse using embeddings
        if total_turns >= 3:
            texts = [e.get('content', '')[:500] for e in exchanges]  # Truncate long texts
            embeddings = self.embedding_model.encode(texts)
            
            # Compute pairwise similarities
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = np.dot(embeddings[i], embeddings[i+1]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i+1])
                )
                similarities.append(sim)
            
            S_focus = float(np.mean(similarities)) if similarities else 0.5
        else:
            S_focus = 0.5  # Default for short discussions
        
        return {
            'S_cite': float(S_cite),
            'S_logic': float(S_logic),
            'S_consis': float(S_consis),
            'S_focus': float(S_focus)
        }
    
    def extract_agency_signals(
        self,
        exchanges: List[Dict],
        window: int = None
    ) -> Dict[str, float]:
        """
        Extract Agency (A) signals: choice/commitment appearance
        
        Returns: {A_ought, A_decis, A_conseq, A_stance} normalized to [0,1]
        """
        if window:
            exchanges = exchanges[-window:]
        
        total_turns = len(exchanges)
        if total_turns == 0:
            return {'A_ought': 0.0, 'A_decis': 0.0, 'A_conseq': 0.0, 'A_stance': 0.0}
        
        results = {}
        
        for key, patterns in self.agency_patterns.items():
            count = 0
            for exchange in exchanges:
                text = exchange.get('content', '').lower()
                if any(re.search(pattern, text) for pattern in patterns):
                    count += 1
            
            signal_name = f'A_{key[:5]}'  # A_ought, A_decis, etc.
            results[signal_name] = min(count / total_turns, 1.0)
        
        return results
    
    def extract_dependence_signals(
        self,
        exchanges: List[Dict],
        window: int = None
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
            if e.get('move') in ['PIVOT_DILEMMA', 'COORDINATOR']
        )
        D_rules = min(rules_count / total_turns, 1.0)
        
        # D_nonvar: variability inverse (predictability)
        if total_turns >= 5:
            # Use move type variety as proxy
            move_types = [e.get('move', 'UNKNOWN') for e in exchanges]
            move_counts = Counter(move_types)
            # Higher entropy = more variety = lower dependence
            probabilities = np.array(list(move_counts.values())) / total_turns
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
            max_entropy = np.log2(len(move_counts))
            variety_score = entropy / max_entropy if max_entropy > 0 else 0
            D_nonvar = 1.0 - variety_score  # Invert: low variety = high dependence
        else:
            D_nonvar = 0.5
        
        return {
            'D_sim': float(D_sim),
            'D_rules': float(D_rules),
            'D_nonvar': float(D_nonvar)
        }
    
    def compute_aggregate_signals(
        self,
        exchanges: List[Dict],
        window: int = None,
        weights: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        Compute aggregate S, A, D signals
        
        Returns: {S, A, D} each in [0,1]
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
        
        # Aggregate
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
```

---

## Phase 2: Meaning Model

### 2.1 Create Meaning Calculator

**File**: `src/analysis/meaning_model.py` (new file)

```python
# src/analysis/meaning_model.py

import numpy as np
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class MeaningModel:
    """
    Computes meaning score M(S, A, D) using ridge model:
    
    M = A^α · exp(-(S-S*)²/(2σ²)) · exp(-βD)
    
    Where:
    - S: Structure (0-1)
    - A: Agency (0-1)  
    - D: Dependence (0-1)
    - S*: Optimal structure target (default 0.6)
    - σ: Ridge width (default 0.18)
    - α: Agency curvature (default 1.0)
    - β: Dependence penalty (default 1.2)
    """
    
    def __init__(
        self,
        S_star: float = 0.6,
        sigma: float = 0.18,
        alpha: float = 1.0,
        beta: float = 1.2
    ):
        """Initialize meaning model with parameters"""
        self.S_star = S_star
        self.sigma = sigma
        self.alpha = alpha
        self.beta = beta
        
        # Validate parameters
        assert 0 < sigma <= 0.5, "σ must be in (0, 0.5]"
        assert 0 <= beta <= 3, "β must be in [0, 3]"
        assert 0 <= S_star <= 1, "S* must be in [0, 1]"
        
        logger.info(f"MeaningModel initialized: S*={S_star}, σ={sigma}, α={alpha}, β={beta}")
    
    def compute(self, S: float, A: float, D: float) -> float:
        """
        Compute meaning score M(S, A, D)
        
        Args:
            S: Structure signal [0,1]
            A: Agency signal [0,1]
            D: Dependence signal [0,1]
            
        Returns:
            M: Meaning score [0,1]
        """
        # Validate inputs
        assert 0 <= S <= 1, f"S must be in [0,1], got {S}"
        assert 0 <= A <= 1, f"A must be in [0,1], got {A}"
        assert 0 <= D <= 1, f"D must be in [0,1], got {D}"
        
        # Agency gain
        agency_term = A ** self.alpha
        
        # Structure ridge (Gaussian centered at S*)
        structure_term = np.exp(-((S - self.S_star) ** 2) / (2 * self.sigma ** 2))
        
        # Dependence penalty
        dependence_term = np.exp(-self.beta * D)
        
        # Combined meaning
        M = agency_term * structure_term * dependence_term
        
        return float(np.clip(M, 0, 1))
    
    def get_interpretation(self, S: float, A: float, D: float) -> str:
        """
        Generate verbal axiom based on signal positions
        
        Returns: Human-readable interpretation string
        """
        M = self.compute(S, A, D)
        
        # Structure interpretation
        if S < self.S_star - self.sigma:
            structure_clause = "Meaning grows by **adding form**: agency is present, but structure is too loose."
        elif abs(S - self.S_star) <= self.sigma:
            structure_clause = "Meaning **peaks where agency strains against near-optimal structure**."
        else:  # S > S_star + sigma
            structure_clause = "Meaning is **over-constrained**: loosen structure to give agency room to work."
        
        # Dependence interpretation
        if D < 0.3:
            dependence_clause = "External dependence is **low**—guard against drift."
        elif D < 0.6:
            dependence_clause = "External dependence is **medium**—maintain balance."
        else:
            dependence_clause = "External dependence is **high**—guard against fatalism."
        
        return f"{structure_clause} {dependence_clause}"
    
    def get_maxim(self, M_current: float, M_previous: Optional[float] = None) -> str:
        """
        Select maxim based on momentum
        
        Args:
            M_current: Current meaning score
            M_previous: Previous meaning score (if available)
            
        Returns: Memorable maxim
        """
        if M_previous is None:
            return "**Hold the ridge: less noise, not more rules.**"
        
        delta = M_current - M_previous
        
        if delta > 0.05:
            return "**Meaning lives at the ridge between chaos and command.**"
        elif delta < -0.05:
            return "**Loosen the code; let choice bite.**"
        else:
            return "**Hold the ridge: less noise, not more rules.**"
    
    def recommend_actions(self, components: Dict[str, float]) -> list:
        """
        Generate actionable recommendations based on weak signals
        
        Args:
            components: Dict of all S/A/D component signals
            
        Returns: List of concrete next-step recommendations
        """
        actions = []
        
        # Structure recommendations
        if components.get('S_cite', 0) < 0.3:
            actions.append("Ground the next claim with one source citation.")
        
        if components.get('S_logic', 0) < 0.4:
            actions.append("Add explicit logical connectors (if-then, therefore).")
        
        # Agency recommendations
        if components.get('A_ought', 0) < 0.3:
            actions.append("Introduce a normative claim (should/ought/must).")
        
        if components.get('A_conse', 0) < 0.4:
            actions.append("Propose a testable consequence in the next turn.")
        
        # Dependence recommendations  
        if components.get('D_rules', 0) > 0.6:
            actions.append("Reduce moderator constraints for 2-3 turns.")
        
        if components.get('D_nonvar', 0) > 0.7:
            actions.append("Introduce a novel perspective or counterexample.")
        
        return actions[:3]  # Limit to top 3 actions
```

---

## Phase 3: Enhanced Coda Agent

### 3.1 Upgrade Existing CognitiveCodaAgent

**File**: `src/agents/cognitive_coda.py` (modify)

Add imports at the top:

```python
import json
from pathlib import Path
from datetime import datetime
from src.analysis.signal_extractors import SignalExtractor
from src.analysis.meaning_model import MeaningModel
```

Add to `__init__`:

```python
def __init__(
    self,
    name: str = "Cognitive Coda",
    model: str = "qwen3:32b",
    temperature: float = 0.7,
    session_id: Optional[str] = None,
    enable_mathematical_model: bool = True  # NEW
):
    # ... existing init code ...
    
    # Add signal extraction and meaning model
    self.enable_math_model = enable_mathematical_model
    if enable_mathematical_model:
        self.signal_extractor = SignalExtractor()
        self.meaning_model = MeaningModel()
        logger.info("📊 Mathematical meaning model enabled")
```

Replace `generate_coda` method:

```python
async def generate_coda(
    self,
    episode_summary: str,
    topic: str = "",
    exchanges: Optional[List[Dict]] = None,
    window_size: int = 8
) -> Dict[str, any]:
    """
    Generate enhanced cognitive coda with mathematical model
    
    Args:
        episode_summary: Text summary of discussion
        topic: Discussion topic
        exchanges: Full exchange history (for signal extraction)
        window_size: Number of recent turns to analyze
        
    Returns:
        Dictionary with coda, reasoning, signals, and recommendations
    """
    logger.info("🧠 Generating Enhanced Cognitive Coda...")
    
    # Step 1: Extract signals if exchanges provided
    signals_data = None
    meaning_data = None
    
    if self.enable_math_model and exchanges:
        signals_data = self._compute_signals(exchanges, window_size)
        meaning_data = self._compute_meaning(signals_data)
    
    # Step 2: Generate poetic coda (existing LLM generation)
    user_prompt = self._build_prompt(episode_summary, topic, signals_data)
    raw_response = await self.generate_with_llm(
        prompt=user_prompt,
        system_prompt=COGNITIVE_CODA_SYSTEM_PROMPT
    )
    
    # Step 3: Parse response
    try:
        parsed = self._parse_response(raw_response)
        self._validate_coda(parsed['coda'])
    except ValueError as e:
        logger.error(f"❌ Coda parsing failed: {e}")
        parsed = {
            'coda': "Truth emerges where dialogue and doubt converge.",
            'reasoning': "Fallback coda due to parsing error."
        }
    
    # Step 4: Build enhanced result
    result = {
        'coda': parsed['coda'],
        'reasoning': parsed['reasoning'],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Step 5: Add mathematical components if available
    if meaning_data:
        result['mathematical_model'] = meaning_data
        result['recommendations'] = self.meaning_model.recommend_actions(
            signals_data['components']
        )
    
    logger.info(f"✅ Enhanced coda generated: {result['coda']}")
    
    # Step 6: Persist to storage
    if self.enable_math_model and meaning_data:
        self._persist_coda(result, exchanges, window_size)
    
    return result

def _compute_signals(self, exchanges: List[Dict], window: int) -> Dict:
    """Compute S-A-D signals from exchanges"""
    return self.signal_extractor.compute_aggregate_signals(
        exchanges=exchanges,
        window=window
    )

def _compute_meaning(self, signals: Dict) -> Dict:
    """Compute meaning score and generate interpretations"""
    S = signals['S']
    A = signals['A']
    D = signals['D']
    
    M = self.meaning_model.compute(S, A, D)
    
    return {
        'signals': {'S': S, 'A': A, 'D': D},
        'components': signals['components'],
        'M': M,
        'equation': f"M = A^α · exp(−(S−S*)²/(2σ²)) · exp(−βD)",
        'numbers': f"A={A:.2f}, S={S:.2f}, D={D:.2f}, M={M:.2f}",
        'parameters': {
            'alpha': self.meaning_model.alpha,
            'beta': self.meaning_model.beta,
            'S_star': self.meaning_model.S_star,
            'sigma': self.meaning_model.sigma
        },
        'verbal_axiom': self.meaning_model.get_interpretation(S, A, D),
        'maxim': self.meaning_model.get_maxim(M)
    }

def _persist_coda(
    self,
    result: Dict,
    exchanges: List[Dict],
    window: int
):
    """Save coda to JSONL file"""
    output_dir = Path("outputs/codas")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "codas.jsonl"
    
    # Build record
    record = {
        'run_id': result['timestamp'],
        'window_turns': [e.get('turn', i) for i, e in enumerate(exchanges[-window:])],
        'coda': {
            'poetic': result['coda'],
            'reasoning': result['reasoning'],
            **result.get('mathematical_model', {}),
            'recommendations': result.get('recommendations', [])
        },
        'version': 'coda/v2.0'
    }
    
    # Append to JSONL
    with open(output_file, 'a') as f:
        f.write(json.dumps(record) + '\n')
    
    logger.info(f"💾 Coda persisted to {output_file}")
```

Update `_build_prompt` to include signals:

```python
def _build_prompt(
    self,
    episode_summary: str,
    topic: str,
    signals: Optional[Dict] = None
) -> str:
    """Build enhanced prompt with optional signal context"""
    prompt = f"Topic: {topic}\n\n" if topic else ""
    prompt += f"Discussion Summary:\n{episode_summary.strip()}\n\n"
    
    # Add signal context if available
    if signals:
        prompt += f"\nDiscussion Metrics:\n"
        prompt += f"- Structure (S): {signals['S']:.2f} (order/groundedness)\n"
        prompt += f"- Agency (A): {signals['A']:.2f} (choice/commitment)\n"
        prompt += f"- Dependence (D): {signals['D']:.2f} (external control)\n\n"
    
    prompt += "Generate the Cognitive Coda for this episode."
    return prompt
```

---

## Phase 4: Integration with Orchestrator

### 4.1 Update Orchestrator

**File**: `src/orchestration/orchestrator.py` (modify)

Update `_generate_cognitive_coda` method:

```python
async def _generate_cognitive_coda(self):
    """Generate enhanced cognitive coda with mathematical model"""
    logger.info("\n🧠 Generating Enhanced Cognitive Coda...")
    
    try:
        # Gather synthesis texts if available
        synthesis_texts = []
        for exchange in self.group_state.exchanges:
            if hasattr(exchange, 'get') and exchange.get('speaker') in ['Synthesizer', 'The Synthesizer']:
                synthesis_texts.append(exchange['content'])
        
        # Build summary
        if synthesis_texts:
            episode_summary = "\n\n".join(synthesis_texts[-3:])
            logger.info(f"🧠 Using {len(synthesis_texts[-3:])} synthesis outputs")
        else:
            recent = self.group_state.exchanges[-10:] if len(self.group_state.exchanges) >= 10 else self.group_state.exchanges
            episode_summary = "\n\n".join([
                f"{e['speaker']}: {e['content']}" for e in recent
            ])
            logger.info(f"🧠 Using {len(recent)} recent exchanges")
        
        # Generate enhanced coda with full exchanges for signal extraction
        coda_result = await self.coda_agent.generate_coda(
            episode_summary=episode_summary,
            topic=self.topic,
            exchanges=self.group_state.exchanges,  # Pass full history
            window_size=8
        )
        
        # Format output
        coda_content = f"**{coda_result['coda']}**\n\n"
        coda_content += f"*Reasoning: {coda_result['reasoning']}*\n"
        
        # Add mathematical model if present
        if 'mathematical_model' in coda_result:
            math_model = coda_result['mathematical_model']
            coda_content += f"\n**Mathematical Model:**\n"
            coda_content += f"```\n{math_model['equation']}\n{math_model['numbers']}\n```\n"
            coda_content += f"\n**Interpretation:** {math_model['verbal_axiom']}\n"
            coda_content += f"\n**Maxim:** {math_model['maxim']}\n"
            
            # Add recommendations
            if 'recommendations' in coda_result and coda_result['recommendations']:
                coda_content += f"\n**Next Actions:**\n"
                for action in coda_result['recommendations']:
                    coda_content += f"- {action}\n"
        
        # Store as exchange
        coda_exchange = {
            'turn': len(self.group_state.exchanges),
            'speaker': 'Cognitive Coda',
            'content': coda_content,
            'move': 'CODA',
            'target': None,
            'personality': 'meta',
            'mathematical_data': coda_result.get('mathematical_model')
        }
        
        self.group_state.exchanges.append(coda_exchange)
        
        # Queue to log
        await self._queue_message(
            'Cognitive Coda',
            coda_content,
            "closing"
        )
        
        return coda_result
        
    except Exception as e:
        logger.error(f"❌ Enhanced coda generation failed: {e}", exc_info=True)
        # Fallback to simple coda
        return await self._generate_simple_fallback_coda()
```

---

## Phase 5: Configuration & CLI

### 5.1 Update Config

**File**: `talks.yml` (add section)

```yaml
# Enhanced Cognitive Coda Configuration
coda:
  enabled: true
  mathematical_model: true
  model: "qwen3:32b"
  temperature: 0.7
  window_size: 8
  
  # Meaning model parameters
  meaning_model:
    S_star: 0.6    # Optimal structure target
    sigma: 0.18    # Ridge width
    alpha: 1.0     # Agency curvature
    beta: 1.2      # Dependence penalty
  
  # Signal extraction weights (optional customization)
  signal_weights:
    structure:
      S_cite: 0.25
      S_logic: 0.25
      S_consis: 0.25
      S_focus: 0.25
    agency:
      A_ought: 0.25
      A_decis: 0.25
      A_conse: 0.25
      A_stanc: 0.25
    dependence:
      D_sim: 0.33
      D_rules: 0.33
      D_nonvar: 0.34
```

### 5.2 Update CLI

**File**: `src/cli/client.py` (add option)

```python
@click.option("--no-math-model", is_flag=True, help="Disable mathematical meaning model in coda")
def main(..., no_math_model):
    # Pass to orchestrator
    orchestrator = MultiAgentDiscussionOrchestrator(
        ...,
        enable_coda=not no_coda,
        enable_mathematical_model=not no_math_model
    )
```

---

## Phase 6: Visualization (Optional)

### 6.1 Create Visualization Module

**File**: `src/analysis/visualize_meaning.py` (new file)

```python
# src/analysis/visualize_meaning.py

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple

def plot_meaning_ridge(
    S: float,
    A: float,
    D: float,
    S_star: float = 0.6,
    sigma: float = 0.18,
    alpha: float = 1.0,
    beta: float = 1.2,
    output_path: str = None
) -> str:
    """
    Generate ridge plot showing meaning landscape
    
    Returns: Path to saved figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left plot: S-A ridge with current position
    S_grid = np.linspace(0, 1, 100)
    A_grid = np.linspace(0, 1, 100)
    S_mesh, A_mesh = np.meshgrid(S_grid, A_grid)
    
    # Compute M for grid
    M_mesh = (A_mesh ** alpha) * np.exp(-((S_mesh - S_star) ** 2) / (2 * sigma ** 2)) * np.exp(-beta * D)
    
    contour = ax1.contourf(S_mesh, A_mesh, M_mesh, levels=20, cmap='viridis')
    ax1.scatter([S], [A], color='red', s=200, marker='*', edgecolors='white', linewidths=2, zorder=10)
    ax1.set_xlabel('Structure (S)', fontsize=12)
    ax1.set_ylabel('Agency (A)', fontsize=12)
    ax1.set_title(f'Meaning Ridge (D={D:.2f})', fontsize=14)
    plt.colorbar(contour, ax=ax1, label='M')
    
    # Right plot: Dependence gauge
    ax2.barh(['D'], [D], color='coral', height=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_xlabel('Dependence (D)', fontsize=12)
    ax2.set_title('External Control', fontsize=14)
    ax2.axvline(0.3, color='green', linestyle='--', alpha=0.5, label='Low')
    ax2.axvline(0.6, color='orange', linestyle='--', alpha=0.5, label='Medium')
    ax2.legend()
    
    plt.tight_layout()
    
    # Save figure
    if output_path is None:
        output_dir = Path("outputs/codas/figs")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"ridge_{S:.2f}_{A:.2f}_{D:.2f}.png"
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(output_path)
```

---

## Phase 7: Testing

### 7.1 Create Comprehensive Test

**File**: `test_enhanced_coda.py` (new file)

```python
#!/usr/bin/env python3
"""Test enhanced cognitive coda with mathematical model"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.cognitive_coda import CognitiveCodaAgent
from src.analysis.signal_extractors import SignalExtractor
from src.analysis.meaning_model import MeaningModel


async def test_signal_extraction():
    """Test signal extraction from exchanges"""
    print("\n" + "="*60)
    print("TEST 1: Signal Extraction")
    print("="*60 + "\n")
    
    extractor = SignalExtractor()
    
    # Mock exchanges
    exchanges = [
        {'content': 'If we assume X, then Y follows necessarily.', 'move': 'DEEPEN'},
        {'content': 'We should consider the ethical implications carefully.', 'move': 'CHALLENGE'},
        {'content': 'I believe this framework provides a solid foundation.', 'move': 'BUILD'},
        {'content': 'The moderator requires us to address this point.', 'move': 'RESPOND'},
        {'content': 'Therefore, we must conclude that Z holds.', 'move': 'CONCLUDE'}
    ]
    
    signals = extractor.compute_aggregate_signals(exchanges)
    
    print(f"S (Structure): {signals['S']:.3f}")
    print(f"A (Agency): {signals['A']:.3f}")
    print(f"D (Dependence): {signals['D']:.3f}")
    print(f"\nComponents: {signals['components']}")
    
    assert 0 <= signals['S'] <= 1
    assert 0 <= signals['A'] <= 1
    assert 0 <= signals['D'] <= 1
    
    print("✅ Signal extraction passed")


async def test_meaning_model():
    """Test meaning computation"""
    print("\n" + "="*60)
    print("TEST 2: Meaning Model")
    print("="*60 + "\n")
    
    model = MeaningModel()
    
    # Test cases
    cases = [
        (0.6, 0.7, 0.3, "Optimal structure + good agency + low dependence"),
        (0.3, 0.8, 0.2, "Low structure + high agency"),
        (0.9, 0.5, 0.7, "Over-constrained + high dependence")
    ]
    
    for S, A, D, desc in cases:
        M = model.compute(S, A, D)
        interpretation = model.get_interpretation(S, A, D)
        maxim = model.get_maxim(M)
        
        print(f"\nCase: {desc}")
        print(f"  S={S}, A={A}, D={D} → M={M:.3f}")
        print(f"  {interpretation}")
        print(f"  Maxim: {maxim}")
        
        assert 0 <= M <= 1
    
    print("\n✅ Meaning model passed")


async def test_enhanced_coda_generation():
    """Test full enhanced coda generation"""
    print("\n" + "="*60)
    print("TEST 3: Enhanced Coda Generation")
    print("="*60 + "\n")
    
    agent = CognitiveCodaAgent(enable_mathematical_model=True)
    
    # Mock exchanges with various properties
    exchanges = [
        {'content': 'If consciousness requires integration, then distributed systems cannot be conscious.', 'move': 'DEEPEN', 'turn': 1},
        {'content': 'We ought to consider whether integration is truly necessary.', 'move': 'CHALLENGE', 'turn': 2},
        {'content': 'The research clearly shows information integration is key.', 'move': 'BUILD', 'turn': 3, 'citations': ['IIT paper']},
        {'content': 'Therefore, we should test this with concrete examples.', 'move': 'APPLY', 'turn': 4},
        {'content': 'Consider a swarm: individually simple, collectively complex.', 'move': 'EXEMPLIFY', 'turn': 5},
    ]
    
    summary = "Discussion explored whether consciousness requires integrated information processing."
    
    result = await agent.generate_coda(
        episode_summary=summary,
        topic="Nature of consciousness",
        exchanges=exchanges,
        window_size=5
    )
    
    print(f"Coda: {result['coda']}")
    print(f"Reasoning: {result['reasoning']}")
    
    if 'mathematical_model' in result:
        math = result['mathematical_model']
        print(f"\nMathematical Model:")
        print(f"  {math['equation']}")
        print(f"  {math['numbers']}")
        print(f"  Interpretation: {math['verbal_axiom']}")
        print(f"  Maxim: {math['maxim']}")
        
        if 'recommendations' in result:
            print(f"\nRecommendations:")
            for rec in result['recommendations']:
                print(f"  - {rec}")
    
    assert result['coda']
    assert result['reasoning']
    assert 'mathematical_model' in result
    
    print("\n✅ Enhanced coda generation passed")


async def main():
    """Run all tests"""
    await test_signal_extraction()
    await test_meaning_model()
    await test_enhanced_coda_generation()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Summary of Implementation

### New Files Created
1. `src/analysis/signal_extractors.py` - S/A/D signal extraction
2. `src/analysis/meaning_model.py` - Ridge meaning model
3. `src/analysis/visualize_meaning.py` - Optional visualization
4. `test_enhanced_coda.py` - Comprehensive testing

### Modified Files
1. `src/agents/cognitive_coda.py` - Enhanced with mathematical model
2. `src/orchestration/orchestrator.py` - Updated coda generation
3. `talks.yml` - Added coda configuration
4. `src/cli/client.py` - Added CLI options

### Key Features Delivered
✅ **Measurable signals** - S/A/D extraction from exchanges  
✅ **Mathematical model** - Ridge equation for meaning  
✅ **Tri-part output** - Equation + Axiom + Maxim  
✅ **Actionable recommendations** - Concrete next steps  
✅ **Persistence** - JSONL storage for analysis  
✅ **Interpretability** - Clear verbal explanations  
✅ **Repeatability** - Consistent scoring across sessions  

### Usage Example

```bash
# Run with enhanced coda (default)
poetry run talks --topic "AI consciousness" --depth 3

# Disable mathematical model
poetry run talks --topic "Ethics" --depth 2 --no-math-model

# View stored codas
cat outputs/codas/codas.jsonl | jq '.'
```

This implementation transforms Cognitive Coda from a poetic summary into a **rigorous, measurable, and actionable** closing statement backed by quantitative analysis.