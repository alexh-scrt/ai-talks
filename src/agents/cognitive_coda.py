# src/agents/cognitive_coda.py

import logging
import re
from typing import Dict, Optional
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


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


class CognitiveCodaAgent(BaseAgent):
    """
    Generates a single-line poetic theorem that distills an entire discussion.
    
    This agent takes the full discussion (or final synthesis) and compresses it
    into a philosophical equation or aphorism under 15 words.
    """
    
    def __init__(
        self,
        name: str = "Cognitive Coda",
        model: str = "qwen3:32b",
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
        self.name = name
        
        super().__init__(
            agent_id=name.lower().replace(" ", "_"),
            web_search=False,  # Coda agent doesn't need web search
            model=model,
            session_id=session_id,
            llm_params={"temperature": temperature}
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
    
    async def process(self, **kwargs) -> str:
        """
        Required implementation of abstract process method from BaseAgent.
        This method allows the agent to be used in standardized workflows.
        """
        episode_summary = kwargs.get('episode_summary', '')
        topic = kwargs.get('topic', '')
        
        result = await self.generate_coda(episode_summary, topic)
        return f"Cognitive Coda: {result['coda']}\n\nReasoning: {result['reasoning']}"