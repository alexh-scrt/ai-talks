# src/agents/rag_style_transfer.py

import logging
from typing import Optional, Dict
from src.agents.base_agent import BaseAgent
from src.states.participant_state import ParticipantState
from src.utils.text_processing import strip_reasoning

logger = logging.getLogger(__name__)


class RAGStyleTransferAgent(BaseAgent):
    """
    Transforms factual RAG outputs into character-appropriate dialogue.
    
    This agent takes responses that may contain web search results
    and rewrites them to sound like they're coming from the character's
    own knowledge and expertise, preserving accuracy while improving
    immersion.
    """
    
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
    
    async def process(self, prompt: str, context: Optional[str] = None) -> str:
        """Implementation of abstract method from BaseAgent"""
        response = await self.generate_with_llm(prompt, context)
        return strip_reasoning(response)
    
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
    
    def _build_persona_description(self, persona: ParticipantState) -> str:
        """Build detailed persona description for prompting"""
        return f"""- Pronouns: {persona.get_pronouns()}
- Personality: {persona.personality.value}
- Expertise: {persona.expertise_area}
- Speaking Style: {self._infer_speaking_style(persona)}
- Current Confidence: {persona.confidence_level:.2f}
- Current Curiosity: {persona.curiosity_level:.2f}"""
    
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