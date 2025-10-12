# src/agents/dialectical_synthesizer.py

import logging
from typing import List, Dict, Tuple, Optional
from src.agents.base_agent import BaseAgent
from src.utils.text_processing import strip_reasoning

logger = logging.getLogger(__name__)


class DialecticalSynthesizerAgent(BaseAgent):
    """
    Performs Hegelian synthesis of discussion tensions.
    
    This agent analyzes recent exchanges and generates periodic syntheses
    that elevate the discourse by finding higher-order truths that reconcile
    opposing viewpoints.
    """
    
    def __init__(
        self,
        name: str = "The Synthesizer",
        synthesis_style: str = "hegelian",
        session_id: Optional[str] = None
    ):
        """
        Initialize the synthesizer agent.
        
        Args:
            name: Display name for the synthesizer
            synthesis_style: One of 'hegelian', 'socratic', 'pragmatic'
            session_id: Session identifier for logging
        """
        super().__init__(
            agent_id="synthesizer",
            web_search=False,  # Pure reasoning, no external search needed
            model="qwen3:32b",
            session_id=session_id,
            llm_params={"temperature": 0.7}
        )
        self.name = name
        self.synthesis_style = synthesis_style
        
        logger.info(f"Initialized {name} with {synthesis_style} style")
    
    async def process(self, prompt: str, context: Optional[str] = None) -> str:
        """Implementation of abstract method from BaseAgent"""
        response = await self.generate_with_llm(prompt, context)
        return strip_reasoning(response)
    
    async def synthesize_segment(
        self,
        exchanges: List[Dict],
        turn_window: int = 6,
        topic: str = ""
    ) -> Optional[str]:
        """
        Generate synthesis from recent discussion segment.
        
        Args:
            exchanges: Full exchange history
            turn_window: How many recent turns to analyze
            topic: Discussion topic for context
            
        Returns:
            Synthesis text, or None if insufficient data
        """
        if len(exchanges) < 3:
            logger.debug("Insufficient exchanges for synthesis (need at least 3)")
            return None
        
        # Get recent exchanges
        recent = exchanges[-turn_window:]
        
        # Identify key tensions
        tensions = self._identify_tensions(recent)
        
        # Extract participant perspectives
        perspectives = self._extract_perspectives(recent)
        
        # Build synthesis prompt based on style
        prompt = self._build_synthesis_prompt(
            tensions=tensions,
            perspectives=perspectives,
            topic=topic
        )
        
        logger.info(f"🔄 {self.name} generating {self.synthesis_style} synthesis...")
        
        # Generate synthesis
        response = await self.generate_with_llm(prompt)
        synthesis = strip_reasoning(response)
        
        logger.debug(f"Generated synthesis: {synthesis[:100]}...")
        
        return synthesis
    
    def _identify_tensions(self, exchanges: List[Dict]) -> List[Dict]:
        """
        Identify dialectical tensions (thesis/antithesis pairs).
        
        Returns list of tension dictionaries with structure:
        {
            'thesis_speaker': str,
            'thesis_content': str,
            'antithesis_speaker': str,
            'antithesis_content': str,
            'move_type': str
        }
        """
        tensions = []
        
        for i, exchange in enumerate(exchanges):
            move = exchange.get("move", "")
            
            # CHALLENGE moves create explicit tensions
            if move == "CHALLENGE" and i > 0:
                tensions.append({
                    'thesis_speaker': exchanges[i-1]['speaker'],
                    'thesis_content': exchanges[i-1]['content'],
                    'antithesis_speaker': exchange['speaker'],
                    'antithesis_content': exchange['content'],
                    'move_type': 'challenge'
                })
            
            # Look for implicit tensions in SUPPORT moves
            # (supporting a different perspective than immediate predecessor)
            elif move == "SUPPORT" and i > 1:
                target = exchange.get('target')
                previous_speaker_id = exchanges[i-1].get('speaker_id')
                
                # If supporting someone other than the immediate previous speaker
                if target and target != previous_speaker_id:
                    tensions.append({
                        'thesis_speaker': exchanges[i-2]['speaker'] if i >= 2 else 'Unknown',
                        'thesis_content': exchanges[i-2]['content'] if i >= 2 else '',
                        'antithesis_speaker': exchange['speaker'],
                        'antithesis_content': exchange['content'],
                        'move_type': 'support_divergence'
                    })
        
        logger.debug(f"Identified {len(tensions)} tensions")
        return tensions
    
    def _extract_perspectives(self, exchanges: List[Dict]) -> List[Dict]:
        """
        Extract distinct perspectives from exchanges.
        
        Returns list of perspective dictionaries:
        {
            'speaker': str,
            'stance': str (content summary),
            'move': str
        }
        """
        perspectives = []
        
        for exchange in exchanges:
            # Truncate long content for prompt efficiency
            content = exchange['content']
            stance = content[:200] + "..." if len(content) > 200 else content
            
            perspectives.append({
                'speaker': exchange['speaker'],
                'stance': stance,
                'move': exchange.get('move', 'UNKNOWN')
            })
        
        return perspectives
    
    def _build_synthesis_prompt(
        self,
        tensions: List[Dict],
        perspectives: List[Dict],
        topic: str
    ) -> str:
        """Build synthesis prompt based on synthesis style"""
        
        if self.synthesis_style == "hegelian":
            return self._build_hegelian_prompt(tensions, perspectives, topic)
        elif self.synthesis_style == "socratic":
            return self._build_socratic_prompt(tensions, perspectives, topic)
        elif self.synthesis_style == "pragmatic":
            return self._build_pragmatic_prompt(tensions, perspectives, topic)
        else:
            # Default to hegelian
            logger.warning(f"Unknown style {self.synthesis_style}, defaulting to hegelian")
            return self._build_hegelian_prompt(tensions, perspectives, topic)
    
    def _build_hegelian_prompt(
        self,
        tensions: List[Dict],
        perspectives: List[Dict],
        topic: str
    ) -> str:
        """Hegelian dialectic: thesis → antithesis → synthesis"""
        
        tensions_text = self._format_tensions(tensions)
        perspectives_text = self._format_perspectives(perspectives)
        
        return f"""You are {self.name}, a philosophical synthesizer in the Hegelian tradition.

**Discussion Topic:** {topic}

**Recent Dialectical Tensions:**
{tensions_text}

**Full Range of Perspectives:**
{perspectives_text}

**Your Task: Hegelian Synthesis**

Apply the dialectical method:
1. **Identify the fundamental opposition** - What is the core thesis/antithesis pair?
2. **Find the hidden unity** - What deeper truth reconciles these opposing views?
3. **Elevate the discourse** - Reframe the question at a higher level of abstraction

**Guidelines:**
- Be profound, not merely conciliatory
- Show how both sides contain partial truths
- Reveal the higher-order question they're really asking
- Keep it to 3-4 sentences
- Use natural, conversational language
- Don't just summarize—transform the understanding

**Your Synthesis:**"""
    
    def _build_socratic_prompt(
        self,
        tensions: List[Dict],
        perspectives: List[Dict],
        topic: str
    ) -> str:
        """Socratic method: expose assumptions, pose deeper questions"""
        
        tensions_text = self._format_tensions(tensions)
        
        return f"""You are {self.name}, a philosophical facilitator in the Socratic tradition.

**Discussion Topic:** {topic}

**Recent Discussion:**
{tensions_text}

**Your Task: Socratic Intervention**

Rather than providing answers, deepen the inquiry:
1. **Expose hidden assumptions** - What are both sides taking for granted?
2. **Pose a penetrating question** - What question would force them to examine their foundations?
3. **Redirect the inquiry** - What should they really be asking?

Keep it to 2-3 sentences. Be provocative, not conclusive.

**Your Intervention:**"""
    
    def _build_pragmatic_prompt(
        self,
        tensions: List[Dict],
        perspectives: List[Dict],
        topic: str
    ) -> str:
        """Pragmatic synthesis: what practical difference does it make?"""
        
        perspectives_text = self._format_perspectives(perspectives)
        
        return f"""You are {self.name}, a pragmatic synthesizer.

**Discussion Topic:** {topic}

**Various Perspectives:**
{perspectives_text}

**Your Task: Pragmatic Synthesis**

Cut through abstraction to practical implications:
1. **What's at stake?** - What practical difference do these views make?
2. **Where's the agreement?** - What do all parties already accept?
3. **What's the productive next question?** - Where should the inquiry go?

Keep it grounded and actionable. 3-4 sentences.

**Your Synthesis:**"""
    
    def _format_tensions(self, tensions: List[Dict]) -> str:
        """Format tensions for prompt"""
        if not tensions:
            return "No explicit tensions identified yet."
        
        result = []
        for i, t in enumerate(tensions, 1):
            result.append(f"\nTension {i} ({t['move_type']}):")
            
            # Truncate for readability
            thesis = t['thesis_content'][:150] + "..." if len(t['thesis_content']) > 150 else t['thesis_content']
            antithesis = t['antithesis_content'][:150] + "..." if len(t['antithesis_content']) > 150 else t['antithesis_content']
            
            result.append(f"  {t['thesis_speaker']}: \"{thesis}\"")
            result.append(f"  {t['antithesis_speaker']}: \"{antithesis}\"")
        
        return "\n".join(result)
    
    def _format_perspectives(self, perspectives: List[Dict]) -> str:
        """Format perspectives for prompt"""
        result = []
        for p in perspectives:
            result.append(f"- {p['speaker']} ({p['move']}): \"{p['stance']}\"")
        return "\n".join(result)