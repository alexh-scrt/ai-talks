"""Agent for enriching discussion with strategically placed philosophical quotes"""

import logging
import random
from typing import Optional, Dict, List, Tuple
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.base_agent import BaseAgent
from src.retrieval.quote_retriever import QuoteRetriever
from src.states.participant_state import ParticipantState
from src.utils.text_processing import clean_llm_response

logger = logging.getLogger(__name__)


QUOTE_ADAPTATION_SYSTEM_PROMPT = """You are a philosophical dialogue writer specializing in voice adaptation.

Your task is to take a philosophical quote and rewrite it in a specific character's voice while:
1. Preserving the core meaning and wisdom
2. Maintaining the original author's attribution
3. Adapting the phrasing to match the speaker's personality and style

The adaptation should feel natural, as if the speaker is invoking the quote but expressing it in their own words.

CRITICAL RULES:
- Keep the essence and meaning intact
- Always attribute to original author
- Match the speaker's personality and rhetorical style
- Make it conversational, not academic
- Aim for approximately the same length

CRITICAL OUTPUT FORMAT:
- Return ONLY the adapted quote in this EXACT format: "Quote text" — Author Name
- NO prefixes like "Adapted quote:" or "Response:"
- NO explanations, commentary, or notes in parentheses
- NO reasoning blocks or meta-text
- NO additional formatting or asterisks
- JUST the quote in quotes and attribution with em dash

EXAMPLE OUTPUT:
"When we wrestle with the forces that pervert the rational order, let us ensure our own souls remain uncorrupted by the very shadows we seek to dispel." — Friedrich Nietzsche

Do NOT include anything else."""


class QuoteEnrichmentAgent(BaseAgent):
    """
    Enriches discussion with strategically placed philosophical quotes.
    
    Responsibilities:
    1. Retrieve relevant quotes based on discussion context
    2. Adapt quotes to speaker's voice
    3. Determine optimal placement timing
    4. Track diversity and impact
    """
    
    def __init__(
        self,
        quote_interval: int = 8,
        enable_voice_adaptation: bool = True,
        session_id: Optional[str] = None
    ):
        """
        Initialize quote enrichment agent
        
        Args:
            quote_interval: Turns between quote placements
            enable_voice_adaptation: Whether to adapt quotes to speaker voice
            session_id: Session identifier
        """
        super().__init__(
            agent_id="quote_enrichment",
            web_search=False,
            model="qwen3:32b",
            session_id=session_id,
            llm_params={"temperature": 0.7}
        )
        
        self.quote_interval = quote_interval
        self.enable_voice_adaptation = enable_voice_adaptation
        self.retriever = QuoteRetriever()
        
        # Tracking
        self.turns_since_last_quote = 0
        self.quotes_used_this_session: List[Dict] = []
        
        logger.info(f"📚 QuoteEnrichmentAgent initialized (interval={quote_interval})")
    
    def should_enrich(self, turn_number: int, phase: str = 'mid') -> bool:
        """
        Determine if current turn should include a quote
        
        Args:
            turn_number: Current turn number
            phase: Discussion phase (opening/mid/closing)
            
        Returns:
            True if quote should be added
        """
        # Don't quote on first turn
        if turn_number == 0:
            return False
        
        # Simple interval check: every Nth turn after initial delay
        return turn_number > 0 and turn_number % self.quote_interval == 0
    
    async def enrich_response(
        self,
        response: str,
        speaker: ParticipantState,
        discussion_topics: List[str],
        current_tension: Optional[Tuple[str, str]] = None,
        discussion_context: str = ""
    ) -> str:
        """
        Add a philosophical quote to the response
        
        Args:
            response: Original response text
            speaker: The speaking agent
            discussion_topics: Current discussion topics
            current_tension: Optional philosophical tension
            discussion_context: Recent discussion for context
            
        Returns:
            Enhanced response with quote
        """
        logger.info(f"📖 Enriching {speaker.name}'s response with quote")
        
        # Retrieve relevant quotes
        quotes = self.retriever.retrieve(
            topics=discussion_topics,
            current_tension=current_tension,
            exclude_authors=[speaker.name],  # Don't quote themselves
            top_k=3,
            relevance_threshold=0.4  # Lower threshold for keyword fallback
        )
        
        if not quotes:
            logger.warning("No relevant quotes found")
            return response
        
        # Select best quote
        selected_quote = quotes[0]
        logger.info(f"📚 Selected quote from {selected_quote['author']}")
        
        # Adapt to speaker's voice if enabled
        if self.enable_voice_adaptation:
            adapted_quote = await self._adapt_quote_to_voice(
                quote=selected_quote,
                speaker=speaker,
                context=discussion_context
            )
        else:
            adapted_quote = selected_quote['quote']
        
        # Format the enriched response
        enriched = self._format_quote_placement(
            original_response=response,
            quote=adapted_quote,
            author=selected_quote['author'],
            speaker=speaker
        )
        
        # Track usage
        self.quotes_used_this_session.append({
            'quote_id': selected_quote['id'],
            'author': selected_quote['author'],
            'speaker': speaker.name,
            'turn': len(self.quotes_used_this_session),
            'relevance_score': selected_quote.get('relevance_score', 0.0)
        })
        
        return enriched
    
    async def _adapt_quote_to_voice(
        self,
        quote: Dict,
        speaker: ParticipantState,
        context: str
    ) -> str:
        """
        Adapt philosophical quote to speaker's voice
        
        Uses similar voice adaptation logic to RAG style transfer
        """
        prompt = f"""Speaker: {speaker.name}
Personality: {speaker.personality.value}
Expertise: {speaker.expertise_area}

Original Quote: "{quote['quote']}" — {quote['author']}

Recent Discussion Context:
{context[-300:] if context else "Philosophical discussion in progress"}

Adapt this quote to how {speaker.name} would naturally express it in conversation.
Maintain the core wisdom and attribute to {quote['author']}, but phrase it in {speaker.name}'s voice."""
        
        try:
            system_message = SystemMessage(content=QUOTE_ADAPTATION_SYSTEM_PROMPT)
            human_message = HumanMessage(content=prompt)
            
            response = await self.llm.ainvoke([system_message, human_message])
            
            # Use comprehensive cleaning pipeline for quote responses
            adapted = clean_llm_response(response.content, is_quote=True)
            
            # Fallback to original if cleaning resulted in empty string
            if not adapted or adapted.isspace():
                logger.warning("Quote adaptation resulted in empty response, using original")
                adapted = f'"{quote["quote"]}" — {quote["author"]}'
            
            logger.debug(f"Adapted quote: {adapted[:80]}...")
            return adapted
            
        except Exception as e:
            logger.warning(f"Quote adaptation failed: {e}, using original")
            return f'"{quote["quote"]}" — {quote["author"]}'
    
    def _format_quote_placement(
        self,
        original_response: str,
        quote: str,
        author: str,
        speaker: ParticipantState
    ) -> str:
        """
        Format how the quote is integrated into the response
        
        Different styles based on personality
        """
        personality = speaker.personality.value
        
        # Template variations by personality
        templates = {
            'analytical': [
                f"{original_response}\n\nAs {author} observed, \"{quote}\" This analytical lens helps us see the structure beneath.",
                f"{original_response}\n\n{author} formalized this insight: \"{quote}\" The principle still holds.",
            ],
            'creative': [
                f"{original_response}\n\n{author} painted it beautifully: \"{quote}\" Can you see the resonance?",
                f"{original_response}\n\nImagine {author}'s words: \"{quote}\" This metaphor illuminates our question.",
            ],
            'skeptical': [
                f"{original_response}\n\n{author} warned us: \"{quote}\" Perhaps we should heed that caution.",
                f"{original_response}\n\nEven {author} recognized the paradox: \"{quote}\" The tension remains.",
            ],
            'collaborative': [
                f"{original_response}\n\n{author} united these ideas when they said, \"{quote}\" Let's build on that foundation together.",
                f"{original_response}\n\nI'm reminded of {author}'s wisdom: \"{quote}\" This connects to what we're exploring.",
            ],
            'assertive': [
                f"{original_response}\n\n{author} was right: \"{quote}\" This principle is decisive.",
                f"{original_response}\n\nConsider {author}'s definitive statement: \"{quote}\" The matter is clear.",
            ],
            'cautious': [
                f"{original_response}\n\n{author} suggested, perhaps wisely, \"{quote}\" We should consider this carefully.",
                f"{original_response}\n\nAs {author} noted, \"{quote}\" This might guide our thinking.",
            ]
        }
        
        # Select template
        template_list = templates.get(personality, templates['analytical'])
        template = random.choice(template_list)
        
        return template
    
    def get_statistics(self) -> Dict:
        """Get enrichment statistics"""
        stats = self.retriever.get_statistics()
        stats['quotes_placed'] = len(self.quotes_used_this_session)
        stats['session_quotes'] = self.quotes_used_this_session
        
        return stats
    
    async def process(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Process requests for philosophical quotes
        
        This method provides a generic interface for quote retrieval,
        though the main functionality is through enrich_response()
        """
        # Extract topic keywords from prompt
        topics = []
        common_philosophical_terms = [
            'truth', 'knowledge', 'wisdom', 'justice', 'virtue', 'ethics',
            'consciousness', 'reality', 'existence', 'meaning', 'freedom',
            'beauty', 'good', 'evil', 'mind', 'soul', 'death', 'life'
        ]
        
        prompt_lower = prompt.lower()
        for term in common_philosophical_terms:
            if term in prompt_lower:
                topics.append(term)
        
        # Fallback to generic philosophical topics
        if not topics:
            topics = ['wisdom', 'truth', 'philosophy']
        
        # Retrieve quotes
        quotes = self.retriever.retrieve(
            topics=topics[:3],  # Limit to top 3 topics
            top_k=1
        )
        
        if quotes:
            quote = quotes[0]
            return f"Here's a relevant philosophical quote:\n\n\"{quote['quote']}\"\n— {quote['author']}\n\nThis speaks to themes of {', '.join(quote['topics'][:2])}."
        else:
            return "I couldn't find a relevant philosophical quote for that topic."
    
    def reset_session(self):
        """Reset for new discussion session"""
        self.turns_since_last_quote = 0
        self.quotes_used_this_session.clear()
        self.retriever.reset_session()
        logger.info("📚 Quote enrichment session reset")