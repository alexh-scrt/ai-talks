# Phase 4: Cognitive Coda Generator - Implementation Instructions

---

## 🎯 Mission Overview

You are implementing a **Cognitive Coda Generator Agent** for the AI Talks multi-agent discussion system. This agent will distill the entire philosophical discussion into a single poetic theorem — a compressed, elegant statement that captures the essence of the conversation in under 15 words.

### What Success Looks Like

After implementation:
- ✅ A new `CognitiveCodaAgent` class exists and works
- ✅ The coda generator triggers at the end of discussions
- ✅ Produces one-line philosophical theorems (≤15 words)
- ✅ Includes reasoning chain explaining the distillation
- ✅ Supports symbolic notation (×, ÷, =, ∞, →)
- ✅ Appears in conversation logs and published outputs
- ✅ Users can enable/disable via CLI and config

---

## 📋 Pre-Implementation Checklist

Before starting, verify:
- [ ] **Phases 1-3 (Synthesizer, RAG, Strategic Objectives) are complete**
- [ ] Python 3.11+ is installed
- [ ] Ollama is running with `qwen3:32b` model
- [ ] Existing tests pass
- [ ] You understand the agent architecture (`src/agents/base_agent.py`)
- [ ] You understand synthesis generation (`src/agents/dialectical_synthesizer.py`)

---

## 🏗️ Architecture Context

### Current System (Post-Phase 3)
```
Orchestrator
    ↓
ParticipantAgents (2-5 agents)
    ↓
[Every N turns] → DialecticalSynthesizerAgent
    ↓
[End of discussion] → Narrator closing
```

### After Phase 4
```
Orchestrator
    ↓
ParticipantAgents (2-5 agents)
    ↓
[Every N turns] → DialecticalSynthesizerAgent
    ↓
[End of discussion] → CognitiveCodaAgent
    ↓
Final one-line theorem + reasoning
    ↓
[Append to log] → Narrator closing
```

### Key Files You'll Create/Modify
1. `src/agents/cognitive_coda.py` - **NEW FILE** (main implementation)
2. `src/agents/__init__.py` - Add import
3. `src/orchestration/orchestrator.py` - Integrate coda generation
4. `src/config/talks_config.py` - Add coda config properties
5. `src/cli/client.py` - Add CLI option
6. `talks.yml` - Add coda configuration
7. `test_cognitive_coda.py` - **NEW FILE** (testing)

---

## 📁 Implementation Plan

### Day 1: Core Cognitive Coda Agent

#### Task 1.1: Create the Cognitive Coda Agent

**File to Create:** `src/agents/cognitive_coda.py`

**Implementation Steps:**

1. **Create the file** with proper imports:

```python
# src/agents/cognitive_coda.py

import logging
import re
from typing import Dict, Optional
from src.agents.base_agent import BaseAgent
from src.utils.text_processing import strip_reasoning

logger = logging.getLogger(__name__)
```

2. **Define the system prompt**:

```python
COGNITIVE_CODA_SYSTEM_PROMPT = """You are the **Cognitive Coda Generator**, the closing voice in a dialectical pipeline.
Your task is to transform the final synthesis of an AI-driven philosophical discussion into ONE LINE
that functions as a poetic theorem — concise, symbolic, and resonant.

Input: A full discussion transcript or final synthesis summary.
Output:
1) A single-line Cognitive Coda — the distilled philosophical theorem.
2) A brief Reasoning Chain (2–4 sentences) explaining why this coda captures the discussion's essence.

STYLE GUIDE
- The Cognitive Coda must be under 15 words, self-contained, and timeless.
- You may use mathematical/symbolic notation (×, ÷, =, ∞, →) or compressed metaphors.
- Avoid narrative summaries; express the structural insight behind the conversation.
- Reasoning Chain = an artist–scientist reflection (2–4 sentences): how concept, emotion, and logic fused.

OUTPUT FORMAT
Cognitive Coda: <the one-line theorem>

Reasoning Chain:
<2–4 sentences explaining why this line crystallizes the episode's truth>

EXAMPLES

Cognitive Coda: Faith = Reason × Wonder ÷ Certainty.

Reasoning Chain:
The dialogue revealed that faith and logic are not opposites but multiplicative forces.
Certainty diminishes both, while wonder sustains their balance; hence, the equation embodies humility within knowledge.

Cognitive Coda: Truth is a verb: critique braided with care.

Reasoning Chain:
The speakers treated truth as lived process, not static proposition.
The verb form restores moral motion to epistemology; the braid symbolizes intellect joined with empathy.

Cognitive Coda: Meaning = (shared practice × honest doubt)ᵗ, t → tomorrow.

Reasoning Chain:
The discussion revealed meaning as exponentially compounding from the interplay of collective rituals and individual skepticism.
The temporal variable embodies how ethics must evolve continuously, never static.

Now generate the Cognitive Coda for the following discussion.
"""
```

3. **Implement the CognitiveCodaAgent class**:

```python
class CognitiveCodaAgent(BaseAgent):
    """
    Generates a single-line poetic theorem that distills an entire discussion.
    
    This agent takes the full discussion (or final synthesis) and compresses it
    into a philosophical equation or aphorism under 15 words.
    """
    
    def __init__(
        self,
        name: str = "Cognitive Coda",
        model: str = "qwen2.5:32b",
        temperature: float = 0.7,
        session_id: Optional[str] = None
    ):
        """
        Initialize the cognitive coda agent.
        
        Args:
            name: Agent name
            model: Ollama model to use
            temperature: Higher for creativity (0.6-0.8 recommended)
            session_id: Optional session ID for tracking
        """
        super().__init__(
            agent_id=name.lower().replace(" ", "_"),
            name=name,
            model=model,
            temperature=temperature,
            session_id=session_id
        )
        
        # Regex patterns for parsing response
        self.coda_pattern = re.compile(
            r"^Cognitive Coda:\s*(.+)$", 
            re.IGNORECASE | re.MULTILINE
        )
        self.reasoning_pattern = re.compile(
            r"Reasoning Chain:\s*(.+)$", 
            re.IGNORECASE | re.DOTALL
        )
        
        logger.info(f"🧠 CognitiveCodaAgent initialized: {name}")
    
    async def generate_coda(
        self,
        episode_summary: str,
        topic: str = ""
    ) -> Dict[str, str]:
        """
        Generate the cognitive coda for a discussion.
        
        Args:
            episode_summary: Full discussion text or final synthesis
            topic: Original discussion topic
            
        Returns:
            Dictionary with 'coda' and 'reasoning' keys
        """
        logger.info("🧠 Generating Cognitive Coda...")
        
        # Build the prompt
        user_prompt = self._build_prompt(episode_summary, topic)
        
        # Generate response
        raw_response = await self.generate_with_llm(
            prompt=user_prompt,
            system_prompt=COGNITIVE_CODA_SYSTEM_PROMPT
        )
        
        # Parse and validate
        try:
            result = self._parse_response(raw_response)
            self._validate_coda(result['coda'])
            
            logger.info(f"✅ Coda generated: {result['coda']}")
            return result
            
        except ValueError as e:
            logger.error(f"❌ Coda generation failed: {e}")
            # Return a fallback
            return {
                'coda': "Truth emerges where dialogue and doubt converge.",
                'reasoning': "Fallback coda due to parsing error."
            }
    
    def _build_prompt(self, episode_summary: str, topic: str) -> str:
        """Build the user prompt for coda generation"""
        prompt = f"Topic: {topic}\n\n" if topic else ""
        prompt += f"Discussion Summary:\n{episode_summary.strip()}\n\n"
        prompt += "Generate the Cognitive Coda for this episode."
        return prompt
    
    def _parse_response(self, raw_text: str) -> Dict[str, str]:
        """
        Parse the LLM response to extract coda and reasoning.
        
        Args:
            raw_text: Raw LLM output
            
        Returns:
            Dictionary with 'coda' and 'reasoning'
            
        Raises:
            ValueError: If parsing fails
        """
        # Extract coda
        coda_match = self.coda_pattern.search(raw_text)
        if not coda_match:
            raise ValueError("Could not find 'Cognitive Coda:' in response")
        
        coda = self._postprocess_coda(coda_match.group(1))
        
        # Extract reasoning
        reasoning_match = self.reasoning_pattern.search(raw_text)
        if not reasoning_match:
            raise ValueError("Could not find 'Reasoning Chain:' in response")
        
        reasoning = reasoning_match.group(1).strip()
        
        return {
            'coda': coda,
            'reasoning': reasoning
        }
    
    def _postprocess_coda(self, coda: str) -> str:
        """Clean and normalize the coda text"""
        # Normalize whitespace and ensure single line
        coda = " ".join(coda.strip().split())
        
        # Ensure it ends with a period unless it has strong punctuation
        if coda and coda[-1] not in ".!?…":
            coda += "."
        
        return coda
    
    def _validate_coda(self, coda: str) -> None:
        """
        Validate that the coda meets requirements.
        
        Args:
            coda: The coda string to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check word count (≤15 words)
        word_count = len(re.findall(r"\b[\w''-]+\b", coda))
        if word_count > 15:
            raise ValueError(
                f"Cognitive Coda too long ({word_count} words). Must be ≤15."
            )
        
        # Check single line
        if "\n" in coda:
            raise ValueError("Cognitive Coda must be a single line.")
        
        # Check minimum length (at least 3 words)
        if word_count < 3:
            raise ValueError("Cognitive Coda too short. Must be at least 3 words.")
```

**✅ Checkpoint:** After Task 1.1, you should have a complete `cognitive_coda.py` file (~200 lines).

---

#### Task 1.2: Update Agent Exports

**File to Modify:** `src/agents/__init__.py`

Add the import:

```python
from .cognitive_coda import CognitiveCodaAgent

__all__ = [
    'BaseAgent',
    'ParticipantAgent',
    'NarratorAgent',
    'DialecticalSynthesizerAgent',
    'RAGStyleTransferAgent',
    'CognitiveCodaAgent',  # NEW
]
```

---

### Day 2: Integration with Orchestrator

#### Task 2.1: Add Configuration Support

**File to Modify:** `src/config/talks_config.py`

Add coda configuration properties:

```python
class TalksConfig:
    # ... existing code ...
    
    @property
    def coda_enabled(self) -> bool:
        """Check if cognitive coda generation is enabled"""
        return self.data.get('coda', {}).get('enabled', True)
    
    @property
    def coda_temperature(self) -> float:
        """Temperature for coda generation"""
        return self.data.get('coda', {}).get('temperature', 0.7)
```

**File to Modify:** `talks.yml`

Add coda configuration:

```yaml
# Cognitive Coda Configuration
coda:
  enabled: true
  temperature: 0.7
  model: "qwen2.5:32b"
```

---

#### Task 2.2: Integrate with Orchestrator

**File to Modify:** `src/orchestration/orchestrator.py`

1. **Import the agent**:

```python
from src.agents import CognitiveCodaAgent
```

2. **Add to __init__**:

```python
def __init__(
    self,
    # ... existing params ...
    enable_coda: bool = True,
):
    # ... existing init code ...
    
    # Initialize cognitive coda agent
    self.coda_agent = None
    if enable_coda:
        self.coda_agent = CognitiveCodaAgent(
            model=config.get('coda', {}).get('model', 'qwen2.5:32b'),
            temperature=config.coda_temperature,
            session_id=self.session_id
        )
        logger.info("🧠 Cognitive Coda generation enabled")
```

3. **Generate coda at end of discussion**:

```python
async def run_discussion(self, max_iterations: int = 20) -> List[Dict]:
    """Main discussion loop"""
    
    # ... existing discussion loop code ...
    
    # After discussion completes, generate cognitive coda
    if self.coda_agent:
        await self._generate_cognitive_coda()
    
    # Then generate narrator closing
    if self.narrator:
        await self._generate_narrator_closing()
    
    return self.group_state.exchanges

async def _generate_cognitive_coda(self):
    """Generate the final cognitive coda"""
    logger.info("\n🧠 Generating Cognitive Coda...")
    
    # Gather all synthesizer outputs or full discussion
    synthesis_texts = []
    for exchange in self.group_state.exchanges:
        if exchange.get('speaker') == 'Synthesizer':
            synthesis_texts.append(exchange['content'])
    
    # Use final synthesis or full discussion summary
    if synthesis_texts:
        episode_summary = "\n\n".join(synthesis_texts[-3:])  # Last 3 syntheses
    else:
        # Fallback: use recent exchanges
        recent = self.group_state.exchanges[-10:]
        episode_summary = "\n\n".join([
            f"{e['speaker']}: {e['content']}" for e in recent
        ])
    
    # Generate coda
    coda_result = await self.coda_agent.generate_coda(
        episode_summary=episode_summary,
        topic=self.topic
    )
    
    # Store as special exchange
    coda_exchange = {
        'turn': len(self.group_state.exchanges),
        'speaker': 'Cognitive Coda',
        'content': coda_result['coda'],
        'reasoning': coda_result['reasoning'],
        'move': 'CODA',
        'addressed_to': None
    }
    
    self.group_state.exchanges.append(coda_exchange)
    
    # Queue to log
    await self._queue_message(
        'Cognitive Coda',
        f"{coda_result['coda']}\n\n*Reasoning: {coda_result['reasoning']}*",
        "closing"
    )
    
    return coda_result
```

---

### Day 3: CLI and Testing

#### Task 3.1: Add CLI Option

**File to Modify:** `src/cli/client.py`

Add CLI flag:

```python
@click.option(
    '--coda/--no-coda',
    default=True,
    help='Enable/disable cognitive coda generation'
)
def main(
    # ... existing params ...
    coda: bool,
):
    # ... existing code ...
    
    # Pass to orchestrator
    orchestrator = MultiAgentDiscussionOrchestrator(
        # ... existing params ...
        enable_coda=coda,
    )
```

---

#### Task 3.2: Create Test Script

**File to Create:** `test_cognitive_coda.py`

```python
#!/usr/bin/env python3
"""Test script for Cognitive Coda Generator"""

import asyncio
from src.agents.cognitive_coda import CognitiveCodaAgent

async def test_coda_generation():
    """Test basic coda generation"""
    
    print("Testing Cognitive Coda Generator")
    print("=" * 60)
    
    # Create agent
    agent = CognitiveCodaAgent()
    
    # Test episode summary
    summary = """
    The discussion explored whether religion is necessary in the 21st century.
    Participants debated between rational structures (Hypatia's equations, Aristotle's habits)
    and fluid spirituality (Lao's Tao, Simone's existential freedom).
    
    The synthesis revealed that both camps seek transcendent coherence—a framework
    to bind fragile selves to something larger. The deeper question emerged:
    How does humanity forge practices that sustain meaning without dogma?
    """
    
    # Generate coda
    result = await agent.generate_coda(
        episode_summary=summary,
        topic="Do we need religion in the 21st century?"
    )
    
    print("\n✨ Generated Cognitive Coda:")
    print(f"   {result['coda']}")
    print(f"\n📖 Reasoning Chain:")
    print(f"   {result['reasoning']}")
    print("\n" + "=" * 60)
    print("✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_coda_generation())
```

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] CognitiveCodaAgent can be instantiated
- [ ] Coda generation returns valid format
- [ ] Word count validation works (≤15 words)
- [ ] Single-line validation works
- [ ] Parsing handles various response formats
- [ ] Fallback works on parsing errors

### Integration Tests
- [ ] Orchestrator creates coda agent when enabled
- [ ] Coda generates at end of discussion
- [ ] Coda appears in conversation log
- [ ] Coda can be disabled via config
- [ ] CLI flag works correctly

### End-to-End Test
```bash
# Run a full discussion with coda
python main.py --panel philosophy \
  --topic "What is consciousness?" \
  --depth 3 \
  --max-turns 12 \
  --coda

# Check the output file
cat outputs/conversation_talks_*.md | grep -A 5 "Cognitive Coda"
```

---

## 📝 Example Output

In the conversation log, the coda should appear like:

```markdown
## Closing

**Cognitive Coda:**

Religion = (ritual × doubt) ÷ dogma, tending toward ∞.

*Reasoning: The discussion revealed religion's essence as the dynamic interplay between structured practice and honest questioning. When dogma diminishes toward zero, meaning approaches infinity—a living synthesis that honors both tradition and transformation.*

**Michael Lee:**

That's a wrap on today's AI Talks...
```

---

## 🎨 Style Guidelines

### Good Codas (Examples)
- ✅ "Faith = Reason × Wonder ÷ Certainty."
- ✅ "Truth is a verb: critique braided with care."
- ✅ "Meaning = (shared practice × honest doubt)ᵗ, t → tomorrow."
- ✅ "Sacred = attention + responsibility − dogma."
- ✅ "Freedom emerges where structure dissolves into flow."

### Poor Codas (Avoid)
- ❌ "The participants discussed many interesting perspectives on religion." (narrative summary)
- ❌ "We should think carefully about the role of faith in modern society." (advice, not insight)
- ❌ "Religion is complex and has many dimensions that require careful consideration." (too generic)

---

## 🐛 Troubleshooting

### Issue: Coda is too long
**Solution:** Increase temperature slightly (0.75-0.8) to encourage more compressed language, or add examples of very short codas in the prompt.

### Issue: Coda is too abstract/generic
**Solution:** Pass more specific synthesis text rather than full transcript. Focus on the final 2-3 synthesis blocks.

### Issue: Parsing fails frequently
**Solution:** Add retry logic with prompt refinement, or loosen regex patterns to handle variations.

### Issue: Coda doesn't use symbolic notation
**Solution:** Add more examples with symbols in the prompt, or explicitly request: "Use symbolic notation (×, ÷, =, →) if appropriate."

---

## ✅ Final Validation

Run this complete validation sequence:

```bash
# 1. Import test
python -c "from src.agents import CognitiveCodaAgent; print('✅ Import works')"

# 2. Unit test
python test_cognitive_coda.py

# 3. Full discussion with coda
python main.py --panel philosophy \
  --topic "What is beauty?" \
  --depth 3 \
  --max-turns 10 \
  --coda

# 4. Check output
grep -A 3 "Cognitive Coda" outputs/conversation_talks_*.md | tail -5

# 5. Test disabling
python main.py --panel philosophy \
  --topic "What is truth?" \
  --depth 2 \
  --max-turns 6 \
  --no-coda
```

If all five pass: **🎉 Phase 4 Complete!**

---

## 🚀 Future Enhancements

1. **Multiple Coda Styles**: Add different compression styles (mathematical, poetic, koan-like)
2. **Coda Refinement**: Allow the agent to generate 3 options and select the best
3. **Visual Codas**: Generate ASCII art or symbolic diagrams
4. **Coda Chains**: Show how codas evolve across multiple discussions on the same topic
5. **Audio Codas**: Generate spoken word performances of the coda

---

**End of Phase 4 Implementation Instructions**

The Cognitive Coda Generator transforms your discussions into timeless philosophical statements—the perfect closing note for any AI Talks episode. 🧠✨