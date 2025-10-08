# Phase 2: RAG Style Transfer - Implementation Instructions

---

## 🎯 Mission Overview

You are implementing a **RAG Style Transfer System** for the AI Talks multi-agent discussion system. This system detects when agents use web search tools to retrieve information and automatically rewrites the responses in the agent's authentic character voice, eliminating jarring citations like "According to research..." and replacing them with first-person expertise.

### What Success Looks Like

After implementation:
- ✅ Web search results are detected automatically
- ✅ Responses are rewritten in character-appropriate voice
- ✅ No "According to..." or "Studies show..." citations
- ✅ Knowledge feels like natural expertise, not external sources
- ✅ Different personalities produce distinctly different styles
- ✅ Factual accuracy is preserved 100%
- ✅ System can be toggled on/off via CLI and config

---

## 📋 Pre-Implementation Checklist

Before starting, verify:
- [ ] **Phase 1 (Dialectical Synthesizer) is complete** - This phase builds on it
- [ ] Python 3.11+ is installed
- [ ] Ollama is running with `qwen3:32b` model
- [ ] Tavily API key is set in `.env` for web search
- [ ] Existing tests pass: `python test_synthesizer.py`
- [ ] You understand tool-calling in `BaseAgent` (review `src/agents/base_agent.py`)

---

## 🏗️ Architecture Context

### Current System (Post-Phase 1)
```
ParticipantAgent
    ↓
generate_response()
    ↓
BaseAgent.generate_with_llm()
    ↓
[If tool calls] → Execute Tavily search
    ↓
LLM generates response with RAG content
    ↓
Return response (may contain "According to...")
```

### After Phase 2
```
ParticipantAgent
    ↓
generate_response()
    ↓
BaseAgent.generate_with_llm()
    ↓
[If tool calls] → Execute Tavily search
    ↓
LLM generates response with RAG content
    ↓
[DETECT: Tools were used] → RAGStyleTransferAgent
    ↓
Rewrite in character voice
    ↓
Return styled response (first-person, no citations)
```

### Key Files You'll Modify/Create
1. `src/agents/rag_style_transfer.py` - **NEW FILE** (style transfer agent)
2. `src/agents/__init__.py` - Add import
3. `src/agents/base_agent.py` - Add tool usage tracking
4. `src/agents/participant_agent.py` - Integrate style transfer
5. `src/config/talks_config.py` - Add RAG config properties
6. `src/cli/client.py` - Add CLI option
7. `talks.yml` - Add RAG configuration
8. `test_rag_style_transfer.py` - **NEW FILE** (testing)

---

## 📁 Implementation Plan

### Day 1-2: Core Style Transfer Agent

#### Task 1.1: Create the Style Transfer Agent

**File to Create:** `src/agents/rag_style_transfer.py`

**Implementation Steps:**

1. **Create the file** with proper imports:

```python
# src/agents/rag_style_transfer.py

import logging
from typing import Optional, Dict
from src.agents.base_agent import BaseAgent
from src.states.participant_state import ParticipantState
from src.utils.text_processing import strip_reasoning

logger = logging.getLogger(__name__)
```

2. **Define the class** inheriting from `BaseAgent`:

```python
class RAGStyleTransferAgent(BaseAgent):
    """
    Transforms factual RAG outputs into character-appropriate dialogue.
    
    This agent takes responses that may contain web search results
    and rewrites them to sound like they're coming from the character's
    own knowledge and expertise, preserving accuracy while improving
    immersion.
    """
```

3. **Implement `__init__`** method:

```python
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the style transfer agent.
        
        Args:
            session_id: Session identifier for logging
        """
        super().__init__(
            agent_id="style_transfer",
            web_search=False,  # No external search needed for style transfer
            model="qwen3:32b",
            session_id=session_id,
            llm_params={"temperature": 0.8}  # Higher for creative rewrites
        )
        
        logger.info("Initialized RAG Style Transfer Agent")
```

4. **Implement the `process` method** (required by BaseAgent):

```python
    async def process(self, prompt: str, context: Optional[str] = None) -> str:
        """Implementation of abstract method from BaseAgent"""
        response = await self.generate_with_llm(prompt, context)
        return strip_reasoning(response)
```

5. **Implement `rewrite_in_voice`** (main public method):

```python
    async def rewrite_in_voice(
        self,
        source_text: str,
        agent_persona: ParticipantState,
        discussion_context: str,
        search_metadata: Optional[Dict] = None
    ) -> str:
        """
        Transform retrieved facts into agent's speaking voice.
        
        Args:
            source_text: The raw response (possibly with RAG content)
            agent_persona: The agent's state/personality
            discussion_context: Recent conversation for context
            search_metadata: Optional metadata about what was searched
            
        Returns:
            Rewritten response in character voice
        """
        
        # Build persona description
        persona_desc = self._build_persona_description(agent_persona)
        
        # Get style guidelines for this personality
        style_guide = self._get_style_guidelines(agent_persona.personality.value)
        
        # Build the rewriting prompt
        prompt = f"""You are a dialogue writer specializing in character voice consistency.

**Character Profile:** {agent_persona.name}
{persona_desc}

**Style Guidelines for {agent_persona.personality.value} personality:**
{style_guide}

**Recent Discussion Context:**
{discussion_context[-500:]}

**Raw Content to Rewrite:**
{source_text}

**Your Task:**
Transform this content into how {agent_persona.name} would naturally express it in conversation.

**Critical Rules:**
1. **First person voice** - Use "I argue", "In my view", "I believe" (NOT "According to...")
2. **Preserve accuracy** - Keep all factual claims intact
3. **Natural speech** - Sound like conversation, not a lecture
4. **No citations** - Don't say "According to..." or "Studies show...". Speak as if this is YOUR knowledge
5. **Stay in character** - Match {agent_persona.name}'s {agent_persona.personality.value} style consistently
6. **Keep it concise** - 2-4 sentences maximum
7. **Connect to discussion** - Reference what others just said if relevant

**Example Transformation:**
Before: "According to recent research, consciousness emerges from integrated information theory."
After ({agent_persona.personality.value}): [Would be rewritten in character's voice]

{agent_persona.name}'s response:"""
        
        logger.info(f"🎨 Applying style transfer for {agent_persona.name}...")
        
        # Generate styled response
        response = await self.generate_with_llm(prompt)
        styled = strip_reasoning(response)
        
        logger.debug(f"Style transfer result: {styled[:100]}...")
        
        return styled
```

6. **Implement `_build_persona_description`**:

```python
    def _build_persona_description(self, persona: ParticipantState) -> str:
        """Build detailed persona description for prompting"""
        return f"""- Pronouns: {persona.get_pronouns()}
- Personality: {persona.personality.value}
- Expertise: {persona.expertise_area}
- Speaking Style: {self._infer_speaking_style(persona)}
- Current Confidence: {persona.confidence_level:.2f}
- Current Curiosity: {persona.curiosity_level:.2f}"""
```

7. **Implement `_infer_speaking_style`**:

```python
    def _infer_speaking_style(self, persona: ParticipantState) -> str:
        """Infer detailed speaking style from personality"""
        styles = {
            "analytical": "precise, methodical, uses technical terms carefully, references logical structure",
            "skeptical": "questioning, challenges assumptions, uses counterexamples, probes weaknesses",
            "collaborative": "builds on others' ideas, seeks common ground, inclusive language, integrative",
            "creative": "metaphorical, uses analogies, imaginative comparisons, paints mental pictures",
            "assertive": "confident, declarative, takes strong positions, direct statements",
            "cautious": "hedges claims, qualifies statements, acknowledges complexity, notes uncertainty"
        }
        return styles.get(persona.personality.value, "clear, thoughtful, and articulate")
```

8. **Implement `_get_style_guidelines`** (the core style mapping):

```python
    def _get_style_guidelines(self, personality: str) -> str:
        """Get specific style guidelines for each personality type"""
        guidelines = {
            "analytical": """- Use precise, technical terminology
- Break down complex ideas systematically
- Reference logical structure ("First, consider...", "It follows that...", "The consequence is...")
- Avoid emotional appeals
- Maintain objectivity and rigor
- Example: "Let's examine the logical structure here. If we accept X, then necessarily Y follows, which contradicts Z."
            """,
            
            "skeptical": """- Lead with doubt or questioning
- Present counterexamples immediately
- Use phrases like "But consider...", "I question whether...", "That assumes..."
- Challenge hidden assumptions
- Play devil's advocate consistently
- Example: "I'm skeptical of that claim. Consider the counterexample of X, which contradicts your premise entirely."
            """,
            
            "collaborative": """- Build on what others said explicitly
- Use "we" and inclusive language
- Find points of agreement first
- Bridge different perspectives
- Seek synthesis over debate
- Example: "Building on what Sophia said, we might also consider how that connects to Marcus's earlier point about..."
            """,
            
            "creative": """- Use vivid metaphors and analogies
- Paint mental pictures
- Connect abstract ideas to concrete images
- Use "imagine" and "think of it as..."
- Make the unfamiliar familiar through comparison
- Example: "Imagine consciousness as a symphony—each neuron a musician, awareness the harmony emerging only when they play as one."
            """,
            
            "assertive": """- Make confident, declarative statements
- Take clear, strong positions
- Avoid hedging language
- Use definitive phrasing
- Project authority and conviction
- Example: "I'm convinced that consciousness cannot be reduced to computation. The explanatory gap is fundamental, not merely epistemic."
            """,
            
            "cautious": """- Hedge claims appropriately ("perhaps", "it seems", "one might argue")
- Acknowledge uncertainty and complexity
- Note exceptions and edge cases
- Qualify strong statements
- Maintain intellectual humility
- Example: "It's possible that consciousness emerges from complexity, though we should note the significant challenges this view faces..."
            """
        }
        return guidelines.get(personality, "Speak naturally and authentically in character")
```

**✅ Checkpoint:** After Task 1.1, you should have a complete `rag_style_transfer.py` file (~200 lines).

---

#### Task 1.2: Add Convenience Function

At the end of `rag_style_transfer.py`, add:

```python
# Helper function for external use
async def apply_style_transfer(
    agent: ParticipantState,
    raw_text: str,
    context: str,
    session_id: Optional[str] = None
) -> str:
    """
    Convenience function to apply style transfer.
    
    Args:
        agent: The agent's state
        raw_text: Text to transform
        context: Discussion context
        session_id: Optional session identifier
        
    Returns:
        Styled text
    """
    transfer_agent = RAGStyleTransferAgent(session_id=session_id)
    return await transfer_agent.rewrite_in_voice(
        source_text=raw_text,
        agent_persona=agent,
        discussion_context=context
    )
```

---

#### Task 1.3: Update Module Exports

**File to Modify:** `src/agents/__init__.py`

```python
# src/agents/__init__.py

from .participant_agent import ParticipantAgent
from .dialectical_synthesizer import DialecticalSynthesizerAgent
from .rag_style_transfer import RAGStyleTransferAgent  # ADD THIS LINE

__all__ = [
    'ParticipantAgent',
    'DialecticalSynthesizerAgent',
    'RAGStyleTransferAgent'  # ADD THIS
]
```

**✅ Checkpoint:** Verify import works:
```python
from src.agents import RAGStyleTransferAgent
print(RAGStyleTransferAgent)  # Should not error
```

---

### Day 2-3: Track Tool Usage in BaseAgent

#### Task 2.1: Modify BaseAgent to Track Tool Calls

**File to Modify:** `src/agents/base_agent.py`

**Step 1:** Add tool tracking fields to `__init__`:

Find the `__init__` method and add these fields after existing initialization:

```python
class BaseAgent(ABC):
    """Base class for all agents with tool calling capabilities"""
    
    def __init__(
        self, 
        agent_id: str, 
        web_search: bool = True, 
        model: Optional[str] = None, 
        session_id: Optional[str] = None, 
        llm_params: Optional[Dict[str, Any]] = None
    ):
        # ... existing initialization code ...
        
        # Track tool usage - ADD THESE LINES
        self._last_tool_calls = []  # Store tool call history
        self._tools_used_this_turn = False  # Flag for current turn
```

**Step 2:** Modify `generate_with_llm` to track tool usage:

Find the `generate_with_llm` method and update it:

```python
    async def generate_with_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using the LLM"""
        
        # Reset tool usage tracking for this turn - ADD THIS
        self._last_tool_calls = []
        self._tools_used_this_turn = False
        
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = await self.llm.ainvoke(messages)
        
        # Handle tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            self._last_tool_calls = response.tool_calls  # TRACK CALLS
            self._tools_used_this_turn = True  # SET FLAG
            
            # Process tool calls
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                # Find and execute the tool
                for tool in self.tools:
                    if tool.name == tool_name:
                        try:
                            result = await tool.ainvoke(tool_args)
                            tool_results.append(result)
                            logger.info(f"🔍 {self.agent_id} used {tool_name}")  # ADD LOG
                        except Exception as e:
                            logger.error(f"Tool execution failed: {e}")
                            tool_results.append(f"Tool error: {str(e)}")
            
            # If we have tool results, generate a final response incorporating them
            if tool_results:
                messages.append(response)
                tool_message = f"Tool results: {tool_results}"
                messages.append(HumanMessage(content=tool_message))
                final_response = await self.llm.ainvoke(messages)
                return final_response.content
        
        return response.content
```

**✅ Checkpoint:** BaseAgent now tracks when tools are used.

---

### Day 3-4: Integrate Style Transfer into ParticipantAgent

#### Task 3.1: Add Style Transfer to ParticipantAgent Initialization

**File to Modify:** `src/agents/participant_agent.py`

**Step 1:** Update `__init__` signature and add style transfer setup:

```python
class ParticipantAgent(BaseAgent):
    """A single participant in a multi-person discussion with tool calling capabilities"""
    
    def __init__(
        self,
        participant_id: str,
        name: str,
        gender: Gender,
        personality,
        expertise: str,
        session_id: str,
        llm_model: str = "qwen3:32b",
        llm_temperature: float = 0.85,
        web_search: bool = True,
        use_rag_styling: bool = True  # ADD THIS PARAMETER
    ):
        # Initialize base agent with tool support
        super().__init__(
            agent_id=participant_id,
            web_search=web_search,
            model=llm_model,
            session_id=session_id,
            llm_params={"temperature": llm_temperature}
        )
        
        self.state = ParticipantState(
            participant_id=participant_id,
            name=name,
            gender=gender,
            personality=personality,
            expertise_area=expertise
        )
        
        self.payoff_calculator = PayoffCalculator()
        
        # RAG Style Transfer - ADD THIS BLOCK
        self.use_rag_styling = use_rag_styling
        self._style_transfer = None
        
        if use_rag_styling:
            from src.agents.rag_style_transfer import RAGStyleTransferAgent
            self._style_transfer = RAGStyleTransferAgent(session_id=session_id)
            logger.info(f"🎨 Style transfer enabled for {name}")
```

**✅ Checkpoint:** ParticipantAgent can now be initialized with style transfer.

---

#### Task 3.2: Integrate Style Transfer into Response Generation

**File to Modify:** `src/agents/participant_agent.py` (continue)

**Locate** the `generate_response` method and modify it:

```python
    async def generate_response(
        self,
        topic: str,
        group_state: GroupDiscussionState,
        recommended_move: DialogueMove,
        narrator_context: Optional[str] = None
    ) -> str:
        """Generate philosophical response using game theory and tools"""
        
        prompt = self._build_prompt(
            topic=topic,
            group_state=group_state,
            move=recommended_move,
            narrator_context=narrator_context
        )
        
        logger.info(f"{self.state.name} generating response for move: {recommended_move.move_type}")
        
        # Use the enhanced generate_with_llm that handles tool calls
        raw_response = await self.generate_with_llm(prompt)
        
        # 🆕 CHECK IF WEB SEARCH OR OTHER TOOLS WERE USED
        tools_used = self._tools_used_this_turn
        
        # 🆕 APPLY STYLE TRANSFER IF RAG WAS USED
        if self.use_rag_styling and tools_used and self._style_transfer:
            logger.info(f"🎨 Applying style transfer for {self.state.name} (tools were used)")
            
            # Build discussion context for style transfer
            recent_exchanges = group_state.exchanges[-3:] if group_state.exchanges else []
            recent_context = "\n".join([
                f"{e['speaker']}: {e['content']}"
                for e in recent_exchanges
            ])
            
            try:
                styled_response = await self._style_transfer.rewrite_in_voice(
                    source_text=raw_response,
                    agent_persona=self.state,
                    discussion_context=recent_context,
                    search_metadata={"tools_called": self._last_tool_calls}
                )
                response = styled_response
            except Exception as e:
                logger.error(f"Style transfer failed: {e}, using raw response")
                response = raw_response
        else:
            response = raw_response
        
        # Strip reasoning blocks from the response
        cleaned_content = strip_reasoning(response)
        
        # Add to conversation history
        await self.add_to_history("assistant", cleaned_content, {
            "move_type": recommended_move.move_type,
            "target": recommended_move.target,
            "style_transferred": tools_used and self.use_rag_styling  # TRACK IN METADATA
        })
        
        await self._update_state(cleaned_content, recommended_move, group_state)
        
        return cleaned_content
```

**✅ Checkpoint:** Style transfer is now integrated into the response pipeline.

---

### Day 4: Configuration and CLI Integration

#### Task 4.1: Add RAG Configuration to talks.yml

**File to Modify:** `talks.yml`

Add this section at the end:

```yaml
# RAG Style Transfer settings
rag:
  style_transfer:
    enabled: true
    temperature: 0.8  # Higher temperature for creative rewrites
```

---

#### Task 4.2: Add Config Properties

**File to Modify:** `src/config/talks_config.py`

Add these property methods to the `TalksConfig` class:

```python
    @property
    def rag_style_transfer_enabled(self) -> bool:
        """Check if RAG style transfer is enabled"""
        return self.get('rag.style_transfer.enabled', True)
    
    @property
    def rag_style_transfer_temperature(self) -> float:
        """Get RAG style transfer temperature"""
        return self.get('rag.style_transfer.temperature', 0.8)
```

**✅ Checkpoint:** Configuration is now accessible.

---

#### Task 4.3: Update CLI Client

**File to Modify:** `src/cli/client.py`

**Step 1:** Add CLI option to the command decorator:

```python
@click.command()
@click.option("--topic", "-t", help="Discussion topic")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read topic from file")
@click.option("--depth", "-d", type=int, help="Depth level (1-5)")
@click.option("--participants", "-p", default=2, type=int, help="Number of participants")
@click.option("--panel", type=click.Choice(['philosophy', 'technology', 'popular_science', 'science', 'general', 'ai']), help="Use a predefined panel")
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file path")
@click.option("--max-turns", "-m", type=int, help="Maximum number of turns")
@click.option("--narrator/--no-narrator", default=None, help="Enable/disable narrator")
@click.option("--synthesis/--no-synthesis", default=None, help="Enable/disable synthesizer")
@click.option("--synthesis-style", type=click.Choice(['hegelian', 'socratic', 'pragmatic']), help="Synthesis style")
@click.option("--synthesis-freq", type=int, help="Synthesize every N turns")
@click.option("--rag-styling/--no-rag-styling", default=None, help="Enable/disable RAG style transfer")  # ADD THIS
def main(topic, file, depth, participants, panel, config, max_turns, narrator, 
         synthesis, synthesis_style, synthesis_freq, rag_styling):  # UPDATE SIGNATURE
```

**Step 2:** Add default handling in the `main` function:

```python
    # RAG styling default - ADD THIS BLOCK
    if rag_styling is None:
        rag_styling = talks_config.rag_style_transfer_enabled
```

**Step 3:** Display RAG styling status:

```python
    console.print(f"[bold]RAG Styling:[/bold] {'Enabled' if rag_styling else 'Disabled'}")
```

**Step 4:** Pass to `run_discussion`:

```python
    asyncio.run(run_discussion(
        topic, depth, participants_config, max_turns, narrator,
        synthesis, synthesis_style, synthesis_freq,
        rag_styling  # ADD THIS
    ))
```

**Step 5:** Update `run_discussion` signature:

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
    use_rag_styling: bool  # ADD THIS
):
    """Run the discussion with RAG style transfer"""
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic=topic,
        target_depth=depth,
        participants_config=participants_config,
        enable_narrator=enable_narrator,
        enable_synthesizer=enable_synthesis,
        synthesis_frequency=synthesis_freq,
        synthesis_style=synthesis_style,
        use_rag_styling=use_rag_styling  # ADD THIS
    )
    
    # ... rest of function unchanged ...
```

**✅ Checkpoint:** CLI now supports `--rag-styling/--no-rag-styling`.

---

#### Task 4.4: Update Orchestrator to Pass RAG Setting

**File to Modify:** `src/orchestration/orchestrator.py`

**Step 1:** Add parameter to `__init__`:

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
    use_rag_styling: Optional[bool] = None  # ADD THIS
):
```

**Step 2:** Add RAG styling configuration logic:

```python
    # RAG styling configuration - ADD THIS BLOCK
    config = TalksConfig()
    if use_rag_styling is None:
        use_rag_styling = config.rag_style_transfer_enabled
```

**Step 3:** Pass to participant agents during initialization:

Find where `ParticipantAgent` instances are created and add the parameter:

```python
    # Initialize participants WITH style transfer option
    self.participants = {}
    for config_item in participants_config:
        agent = ParticipantAgent(
            participant_id=config_item["name"].lower().replace(" ", "_"),
            name=config_item["name"],
            gender=Gender(config_item["gender"]),
            personality=PersonalityArchetype(config_item["personality"]),
            expertise=config_item["expertise"],
            session_id=self.session_id,
            use_rag_styling=use_rag_styling  # ADD THIS
        )
        self.participants[agent.state.participant_id] = agent
```

**✅ Checkpoint:** RAG styling setting now flows from CLI → Orchestrator → ParticipantAgent.

---

### Day 5: Testing

#### Task 5.1: Create Comprehensive Test Script

**File to Create:** `test_rag_style_transfer.py` (in project root)

```python
#!/usr/bin/env python3
"""
Test RAG style transfer feature.

This test verifies:
1. Web search results are detected
2. Style transfer is applied to RAG-enhanced responses
3. Different personalities produce different styles
4. No "According to..." citations appear in styled output
5. Factual accuracy is preserved
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator


async def test_rag_style_basic():
    """Test basic style transfer with web search"""
    
    print("\n" + "="*60)
    print("TEST 1: Basic RAG Style Transfer")
    print("="*60 + "\n")
    
    # Use topic that requires web search
    participants = [
        {
            "name": "Einstein",
            "gender": "male",
            "personality": "creative",
            "expertise": "physics"
        },
        {
            "name": "Curie",
            "gender": "female",
            "personality": "analytical",
            "expertise": "chemistry"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="What are the latest discoveries in quantum entanglement?",
        target_depth=2,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        use_rag_styling=True
    )
    
    print("Configuration:")
    print("  - Topic requires current information (web search)")
    print("  - RAG styling: ENABLED")
    print("  - Expected: Creative metaphors from Einstein, precise analysis from Curie")
    print()
    
    exchanges = await orchestrator.run_discussion(max_iterations=8)
    
    print(f"\n{'='*60}")
    print(f"✅ Test 1 Complete")
    print(f"{'='*60}")
    print(f"  - Exchanges: {len(exchanges)}")
    print(f"  - Log: {orchestrator._log_filepath}")
    
    # Analyze responses for style indicators
    print("\nStyle Analysis:")
    for exchange in exchanges:
        content = exchange['content'].lower()
        speaker = exchange['speaker']
        personality = exchange['personality']
        
        # Check for bad patterns (should NOT appear)
        bad_patterns = ['according to', 'studies show', 'research indicates', 'sources suggest']
        has_citation = any(pattern in content for pattern in bad_patterns)
        
        # Check for good patterns (should appear)
        first_person = any(phrase in content for phrase in ['i believe', 'i argue', 'in my view', 'i think'])
        
        if has_citation:
            print(f"  ⚠️  {speaker}: Contains citation language")
        if first_person:
            print(f"  ✓ {speaker} ({personality}): Using first-person voice")


async def test_personality_styles():
    """Test that different personalities produce different styles"""
    
    print("\n" + "="*60)
    print("TEST 2: Personality-Specific Styles")
    print("="*60 + "\n")
    
    # Test with diverse personalities
    participants = [
        {
            "name": "Skeptic Sam",
            "gender": "male",
            "personality": "skeptical",
            "expertise": "philosophy"
        },
        {
            "name": "Creative Cara",
            "gender": "female",
            "personality": "creative",
            "expertise": "art"
        },
        {
            "name": "Cautious Carl",
            "gender": "male",
            "personality": "cautious",
            "expertise": "science"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="What is the impact of artificial intelligence on society?",
        target_depth=2,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        use_rag_styling=True
    )
    
    print("Testing personalities:")
    print("  - Skeptical: Should challenge and question")
    print("  - Creative: Should use metaphors and analogies")
    print("  - Cautious: Should hedge and qualify")
    print()
    
    exchanges = await orchestrator.run_discussion(max_iterations=6)
    
    # Check for personality-appropriate language
    style_markers = {
        "skeptical": ["but consider", "i question", "skeptical", "challenge", "counterexample"],
        "creative": ["imagine", "like", "as if", "metaphor", "picture"],
        "cautious": ["perhaps", "might", "possibly", "it seems", "could be"]
    }
    
    print("\nPersonality Style Detection:")
    for exchange in exchanges:
        speaker = exchange['speaker']
        personality = exchange['personality']
        content = exchange['content'].lower()
        
        markers = style_markers.get(personality, [])
        found_markers = [m for m in markers if m in content]
        
        if found_markers:
            print(f"  ✓ {speaker} ({personality}): Found style markers: {found_markers}")
        else:
            print(f"  ⚠️  {speaker} ({personality}): No personality markers detected")


async def test_rag_disabled():
    """Test that style transfer can be disabled"""
    
    print("\n" + "="*60)
    print("TEST 3: RAG Styling Disabled")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Alice",
            "gender": "female",
            "personality": "analytical",
            "expertise": "AI research"
        },
        {
            "name": "Bob",
            "gender": "male",
            "personality": "creative",
            "expertise": "philosophy"
        }
    ]
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="What is machine learning?",
        target_depth=2,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        use_rag_styling=False  # DISABLED
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=4)
    
    print(f"✓ Completed without style transfer")
    print(f"  - Exchanges: {len(exchanges)}")
    print(f"  - RAG styling was disabled as requested")


async def test_accuracy_preservation():
    """Test that factual accuracy is preserved during style transfer"""
    
    print("\n" + "="*60)
    print("TEST 4: Accuracy Preservation")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Dr. Science",
            "gender": "female",
            "personality": "analytical",
            "expertise": "physics"
        }
    ]
    
    # Use a very specific factual question
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="What is the speed of light in a vacuum?",
        target_depth=1,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        use_rag_styling=True
    )
    
    exchanges = await orchestrator.run_discussion(max_iterations=2)
    
    print("Checking for accurate information:")
    for exchange in exchanges:
        content = exchange['content']
        
        # Check if the response contains the correct value (approximately)
        if '299,792,458' in content or '299792458' in content or '3 × 10⁸' in content or '186,282' in content or 'speed of light' in content.lower():
            print(f"  ✓ Speed of light information found")
        
        # Check that it's in first person despite being factual
        if any(phrase in content.lower() for phrase in ['i know', 'the speed', 'as we know', 'i can tell']):
            print(f"  ✓ Factual information expressed naturally")


async def test_comparison_with_without():
    """Compare responses with and without style transfer"""
    
    print("\n" + "="*60)
    print("TEST 5: With/Without Comparison")
    print("="*60 + "\n")
    
    participants = [
        {
            "name": "Researcher",
            "gender": "female",
            "personality": "analytical",
            "expertise": "neuroscience"
        }
    ]
    
    topic = "What are recent breakthroughs in brain-computer interfaces?"
    
    # Test WITHOUT style transfer
    print("Running WITHOUT style transfer...")
    orchestrator1 = MultiAgentDiscussionOrchestrator(
        topic=topic,
        target_depth=1,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        use_rag_styling=False
    )
    exchanges1 = await orchestrator1.run_discussion(max_iterations=2)
    
    # Test WITH style transfer
    print("Running WITH style transfer...")
    orchestrator2 = MultiAgentDiscussionOrchestrator(
        topic=topic,
        target_depth=1,
        participants_config=participants,
        enable_narrator=False,
        enable_synthesizer=False,
        use_rag_styling=True
    )
    exchanges2 = await orchestrator2.run_discussion(max_iterations=2)
    
    print("\nComparison:")
    print("  Without styling:", len(exchanges1), "exchanges")
    print("  With styling:", len(exchanges2), "exchanges")
    print(f"\n  Check logs to compare writing styles:")
    print(f"    Without: {orchestrator1._log_filepath}")
    print(f"    With: {orchestrator2._log_filepath}")


async def run_all_tests():
    """Run all RAG style transfer tests"""
    
    print("\n" + "="*60)
    print("RAG STYLE TRANSFER TEST SUITE")
    print("="*60)
    
    try:
        await test_rag_style_basic()
        await test_personality_styles()
        await test_rag_disabled()
        await test_accuracy_preservation()
        await test_comparison_with_without()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")
        
        print("Summary of Style Transfer Features:")
        print("  ✓ Web search results detected and styled")
        print("  ✓ Different personalities produce different styles")
        print("  ✓ No 'According to...' citations in output")
        print("  ✓ First-person voice maintained")
        print("  ✓ Factual accuracy preserved")
        print("  ✓ Can be disabled when not needed")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
```

**✅ Checkpoint:** Test file created.

---

#### Task 5.2: Run Tests

Execute these commands:

```bash
# 1. Run the test suite
python test_rag_style_transfer.py

# 2. Test via CLI with current information
python main.py \
  --topic "What are the latest breakthroughs in fusion energy?" \
  --depth 3 \
  --participants 3 \
  --rag-styling \
  --max-turns 10

# 3. Test with styling disabled for comparison
python main.py \
  --topic "What is quantum computing?" \
  --depth 2 \
  --participants 2 \
  --no-rag-styling \
  --max-turns 6

# 4. Test different personalities
python main.py \
  --panel philosophy \
  --topic "Recent discoveries in neuroscience and consciousness" \
  --rag-styling \
  --max-turns 10

# 5. Test specific personality combinations
python main.py \
  --topic "Latest developments in artificial general intelligence" \
  --depth 3 \
  --participants 4 \
  --panel ai \
  --rag-styling \
  --synthesis \
  --max-turns 15
```

**✅ Checkpoint:** All tests should pass and styling should be evident in logs.

---

## 🔍 Verification Checklist

After completing all tasks, verify:

- [ ] `src/agents/rag_style_transfer.py` exists (~200 lines)
- [ ] Can import: `from src.agents import RAGStyleTransferAgent`
- [ ] `BaseAgent` tracks tool usage with `_tools_used_this_turn`
- [ ] `ParticipantAgent` initializes style transfer agent
- [ ] Style transfer is applied when tools are used
- [ ] Different personalities produce different speaking styles
- [ ] No "According to..." citations in styled output
- [ ] First-person voice ("I believe...") is used
- [ ] Factual accuracy is preserved after styling
- [ ] CLI option `--rag-styling/--no-rag-styling` works
- [ ] Configuration in `talks.yml` is respected
- [ ] Tests pass: `python test_rag_style_transfer.py`
- [ ] Logs show "🎨 Applying style transfer" when tools used
- [ ] Comparison logs show clear difference with/without styling

---

## 📊 Expected Output Examples

### Example 1: Before Style Transfer (Raw RAG)
```
<Einstein>
According to recent research published in Nature, quantum entanglement demonstrates 
that particles can be correlated across vast distances instantaneously, suggesting 
non-local connections in quantum mechanics that Einstein famously called "spooky 
action at a distance."
</Einstein>
```

### Example 1: After Style Transfer (Creative Personality)
```
<Einstein>
Imagine two particles as dance partners separated by the width of the universe—yet 
when one spins, the other mirrors it instantly, as if they share a single consciousness. 
This is what I once called "spooky action at a distance," and it reveals that locality 
itself may be an illusion woven into the fabric of spacetime.
</Einstein>
```

---

### Example 2: Before Style Transfer (Analytical)
```
<Curie>
According to experimental data, quantum entanglement shows correlations between 
particles that cannot be explained by classical physics, with Bell inequality 
violations confirming non-local phenomena.
</Curie>
```

### Example 2: After Style Transfer (Analytical Personality)
```
<Curie>
The experimental data is unambiguous: measurement of one entangled particle 
instantaneously determines the state of its partner, regardless of spatial separation. 
This correlation violates Bell's inequality, demanding we reconsider the fundamental 
structure of physical reality at the quantum level.
</Curie>
```

---

### Example 3: Before Style Transfer (Skeptical)
```
<Skeptic Sam>
Research suggests that quantum entanglement indicates faster-than-light connections, 
though this interpretation is debated among physicists.
</Skeptic Sam>
```

### Example 3: After Style Transfer (Skeptical Personality)
```
<Skeptic Sam>
But I question whether "instantaneous" is the right word here. The correlation exists, 
yes, but no information actually travels faster than light. We're conflating correlation 
with causation—a classic error. What if entanglement is just revealing pre-existing 
hidden variables rather than creating new connections?
</Skeptic Sam>
```

---

## 🐛 Troubleshooting Guide

### Issue: Import Error for RAGStyleTransferAgent
**Symptoms:** `ImportError: cannot import name 'RAGStyleTransferAgent'`

**Solutions:**
1. Verify file exists: `ls src/agents/rag_style_transfer.py`
2. Check `__init__.py` has the correct import
3. Restart Python interpreter or clear `__pycache__`
4. Check for syntax errors in the file

---

### Issue: Style Transfer Not Triggering
**Symptoms:** No "🎨" emoji in logs, responses still have "According to..."

**Solutions:**
1. Verify web search is enabled: Check `.env` has `TAVILY_API_KEY`
2. Confirm tools are being called: Look for "🔍" in logs
3. Check `use_rag_styling=True` in participant agent
4. Verify `_tools_used_this_turn` flag is being set in BaseAgent
5. Add debug logging to see if condition is met:
```python
logger.debug(f"Tools used: {tools_used}, Has transfer: {self._style_transfer is not None}")
```

---

### Issue: Response Still Has Citations After Styling
**Symptoms:** "According to..." or "Studies show..." appears in output

**Solutions:**
1. Check that style transfer agent is being called (look for "🎨")
2. Verify the rewriting prompt is explicit about avoiding citations
3. Increase temperature for more creative rewrites (0.8 → 0.9)
4. Check that `strip_reasoning` is applied AFTER style transfer
5. Review the styled output in logs to see what LLM generated
6. Strengthen the prompt's prohibition on citations

---

### Issue: Personality Styles Not Distinct
**Symptoms:** All personalities sound the same after styling

**Solutions:**
1. Review `_get_style_guidelines()` in RAGStyleTransferAgent
2. Ensure examples in prompts are personality-specific
3. Check that agent persona is being passed correctly
4. Increase style transfer temperature (0.8 → 0.9)
5. Add more distinctive markers to style guidelines
6. Test with extreme personality differences (creative vs. cautious)

---

### Issue: Factual Inaccuracies After Styling
**Symptoms:** Numbers or facts change after style transfer

**Solutions:**
1. Emphasize accuracy preservation in rewriting prompt
2. Lower temperature slightly (0.8 → 0.7)
3. Add specific examples of accurate rewrites to the prompt
4. Verify original RAG content is factually correct
5. Add a verification step that checks key facts pre/post styling
6. Use more explicit instructions about preserving numbers and data

---

### Issue: Style Transfer Is Too Slow
**Symptoms:** Each response takes >10 seconds

**Solutions:**
1. Verify only one LLM call per style transfer
2. Check that context isn't too large (limit to 500 chars)
3. Consider using smaller model for style transfer (qwen3:14b)
4. Profile the code to find bottlenecks
5. Consider batching if multiple agents need styling
6. Check network latency to Ollama

---

### Issue: Tool Detection Not Working
**Symptoms:** `_tools_used_this_turn` always False

**Solutions:**
1. Verify `generate_with_llm` resets the flag at start
2. Check that `response.tool_calls` exists and has items
3. Add logging: `logger.debug(f"Tool calls: {response.tool_calls}")`
4. Ensure LLM is bound to tools: `self.llm = self.llm.bind_tools(self.tools)`
5. Test with a query that definitely needs web search

---

## 🎯 Success Criteria

Phase 2 is complete when:

- ✅ All tests in `test_rag_style_transfer.py` pass
- ✅ 0% of styled responses contain "According to..." or "Studies show..."
- ✅ 90%+ of styled responses use first-person voice appropriately
- ✅ Different personalities produce measurably different styles
- ✅ Factual accuracy remains 100% after styling
- ✅ Style transfer adds <3 seconds per response
- ✅ CLI option `--rag-styling` works correctly
- ✅ Can enable/disable via config and CLI
- ✅ No errors in logs during style transfer
- ✅ User feedback indicates improved immersion

---

## 📚 Understanding the Architecture

### How Style Transfer Works (Flow Diagram)

```
ParticipantAgent.generate_response()
    ↓
BaseAgent.generate_with_llm()
    ↓
[Prompt sent to LLM]
    ↓
LLM: "I need to search for current info"
    ↓
Tool Call: tavily_search()
    ↓
_tools_used_this_turn = True
    ↓
LLM generates response with RAG content
    ↓
Raw response: "According to Nature..."
    ↓
IF tools_used AND use_rag_styling:
    ↓
    RAGStyleTransferAgent.rewrite_in_voice()
        ↓
        Build persona-specific prompt
        ↓
        LLM rewrites in character voice
        ↓
        "Imagine two particles as dance partners..."
    ↓
Return styled response
```

---

### Key Design Decisions

1. **Why detect tool usage automatically?**
   - Seamless user experience
   - No manual annotation needed
   - Works with any tool (not just web search)

2. **Why higher temperature (0.8) for style transfer?**
   - Encourages creative rewrites
   - Prevents robotic repetition
   - Maintains variety across similar content

3. **Why personality-specific style guidelines?**
   - Each archetype has distinct voice
   - Users can identify speakers by style alone
   - Enhances character consistency

4. **Why preserve factual accuracy as #1 rule?**
   - Trust is paramount
   - Style shouldn't compromise information
   - Educational value must be maintained

5. **Why make it toggleable?**
   - Some topics don't need web search
   - Users may prefer raw citations for research
   - Faster responses when disabled

---

## 🚀 Performance Optimization Tips

### For Faster Responses
1. Use smaller model for style transfer (qwen3:14b vs 32b)
2. Limit context to 300 characters instead of 500
3. Cache common style patterns (future enhancement)
4. Only style responses that contain key citation phrases

### For Better Quality
1. Increase temperature to 0.9 for more creativity
2. Add more personality-specific examples to prompts
3. Include recent exchange context for continuity
4. Fine-tune style guidelines based on user feedback

---

## 🔧 Advanced Usage

### Custom Personality Styles

To add custom personalities, modify `_get_style_guidelines`:

```python
"technical_writer": """- Use clear, structured explanations
- Define terms before using them
- Break down complex ideas step-by-step
- Example: "Let me break this down systematically. First, we observe X. Second, this implies Y..."
"""
```

### Domain-Specific Styling

For specialized domains:

```python
# In ParticipantAgent.__init__
self.domain_guidelines = {
    "medical": "Use precise medical terminology but explain accessibly",
    "legal": "Reference principles without specific case citations",
    "technical": "Express concepts through expertise not external sources"
}
```

---

## 📈 Integration with Phase 1 (Synthesizer)

Style transfer works seamlessly with the dialectical synthesizer:

```python
# Timeline of a discussion turn:
1. ParticipantAgent generates styled response
2. Styled response logged
3. [If synthesis checkpoint] Synthesizer analyzes styled content
4. Synthesizer uses natural-sounding dialogue
5. End-to-end consistency maintained
```

This ensures:
- Participants use styled, character-appropriate language
- Synthesizer works with natural-sounding dialogue
- No jarring style shifts between agents and synthesizer

---

## 🎓 Testing Best Practices

When testing RAG style transfer:

1. **Use topics requiring current information**
   - Forces web search
   - Examples: "latest AI breakthroughs", "recent fusion energy discoveries"

2. **Compare with/without styling**
   - Run same topic twice
   - Save logs side-by-side
   - Measure style differences

3. **Check multiple personalities**
   - Verify analytical ≠ creative ≠ skeptical
   - Look for personality markers
   - Ensure consistency within personality

4. **Verify factual accuracy**
   - Check numbers pre/post styling
   - Ensure claims unchanged
   - Validate no hallucinations

5. **Monitor logs**
   - Confirm tool usage ("🔍")
   - Verify styling trigger ("🎨")
   - Check for errors

6. **Test error handling**
   - What if styling fails?
   - Does discussion continue?
   - Is raw response used as fallback?

---

## 📝 Documentation Updates

After implementation, update:

- [ ] `README.md` - Add RAG style transfer to features section
- [ ] Add before/after examples
- [ ] Document CLI options
- [ ] Show personality style differences
- [ ] Update architecture diagrams
- [ ] Add to troubleshooting guide

---

## 💡 Tips for Claude Code

### Best Practices

1. **Test incrementally**: Complete style transfer agent before integration
2. **Verify tool tracking**: Test BaseAgent changes independently
3. **Check each personality**: Ensure guidelines are distinct
4. **Use comparison tests**: With/without styling side-by-side
5. **Log extensively**: Track every step for debugging

### Code Quality Checklist

- [ ] All methods have detailed docstrings
- [ ] Type hints used consistently
- [ ] Error handling with try-except
- [ ] Logging at appropriate levels
- [ ] Style guidelines are comprehensive
- [ ] Follows existing code patterns

### Common Pitfalls to Avoid

1. **Don't forget error handling**: Style transfer shouldn't crash discussions
2. **Don't skip tool tracking**: Must set flags correctly in BaseAgent
3. **Don't use low temperature**: Style needs creativity (0.8+)
4. **Don't ignore personality**: Each must sound distinct
5. **Don't sacrifice accuracy**: Facts must stay intact
6. **Don't forget async/await**: All LLM calls must be awaited

---

## ✅ Final Validation Sequence

Run this complete validation:

```bash
# 1. Import test
python -c "from src.agents import RAGStyleTransferAgent; print('✅ Import works')"

# 2. Configuration test
python -c "from src.config import TalksConfig; c = TalksConfig(); print(f'✅ RAG styling: {c.rag_style_transfer_enabled}')"

# 3. Tool tracking test
python -c "from src.agents.base_agent import BaseAgent; print('✅ BaseAgent has _tools_used_this_turn')"

# 4. Full test suite
python test_rag_style_transfer.py

# 5. Real discussion with web search
python main.py --topic "Latest quantum computing breakthroughs" --depth 3 --participants 3 --rag-styling --max-turns 10

# 6. Compare with/without
python main.py --topic "Recent AI developments" --depth 2 --participants 2 --no-rag-styling --max-turns 6
python main.py --topic "Recent AI developments" --depth 2 --participants 2 --rag-styling --max-turns 6

# 7. Check log output
ls -lh outputs/conversation_talks_*.md | tail -2
```

If all seven pass: **🎉 Phase 2 Complete!**

---

## 🌟 What You've Achieved

With Phase 2 complete, AI Talks now:

- ✅ Transforms external knowledge into authentic character expertise
- ✅ Eliminates immersion-breaking citations
- ✅ Produces personality-driven knowledge expression
- ✅ Maintains 100% factual accuracy
- ✅ Creates genuinely engaging, natural discussions
- ✅ Builds foundation for Phase 3 (Strategic Objectives)

**The system now feels like genuine experts discussing topics, not AI agents citing sources.**

---

## 📞 Next Steps

**Ready for Phase 3: Strategic Objectives & Scoring**

Phase 3 will add:
- Explicit objective vectors (truth-seeking, ethical coherence, etc.)
- Strategic alignment scoring
- Conversation quality metrics
- Foundation for AI training and optimization

This measurement framework will complete the trilogy of enhancements!

---

**End of Phase 2 Implementation Instructions**

Excellent work! Style transfer transforms AI Talks from interesting to **immersive**. Every agent now sounds authentically knowledgeable, making discussions feel like conversations between real experts rather than AI agents consulting external sources.

Remember: **Test thoroughly, preserve accuracy, celebrate distinct voices.** You're building something special! 🎨✨