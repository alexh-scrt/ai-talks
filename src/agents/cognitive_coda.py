# src/agents/cognitive_coda.py

import logging
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
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
        session_id: Optional[str] = None,
        enable_mathematical_model: bool = True
    ):
        """
        Initialize the cognitive coda agent.
        
        Args:
            name: Agent name
            model: Ollama model to use
            temperature: Higher for creativity (0.6-0.8 recommended)
            session_id: Optional session ID for tracking
            enable_mathematical_model: Whether to enable S-A-D mathematical analysis
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
        
        # Add signal extraction and meaning model
        self.enable_math_model = enable_mathematical_model
        self.signal_extractor = None
        self.meaning_model = None
        
        if enable_mathematical_model:
            try:
                from src.analysis.signal_extractors import SignalExtractor
                from src.analysis.meaning_model import MeaningModel
                self.signal_extractor = SignalExtractor()
                self.meaning_model = MeaningModel()
                logger.info("📊 Mathematical meaning model enabled")
            except ImportError as e:
                logger.warning(f"Mathematical model dependencies not available: {e}")
                self.enable_math_model = False
        
        logger.info(f"🧠 CognitiveCodaAgent initialized: {name} (math_model: {self.enable_math_model})")
    
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
        
        if self.enable_math_model and self.signal_extractor and exchanges:
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
    
    def _compute_signals(self, exchanges: List[Dict], window: int) -> Dict:
        """Compute S-A-D signals from exchanges with enhanced agency extraction"""
        # Use enhanced agency computation from Phase 6A
        agency_result = self.signal_extractor.compute_agency_score(exchanges, window_size=window)
        
        # Get other signals using the existing method
        aggregate_signals = self.signal_extractor.compute_aggregate_signals(
            exchanges=exchanges,
            window=window
        )
        
        # Replace A with enhanced agency result
        aggregate_signals['A'] = agency_result['A']
        
        # Add agency sub-components to components
        aggregate_signals['components'].update({
            'A_ought': agency_result['A_ought'],
            'A_decis': agency_result['A_decis'],
            'A_conseq': agency_result['A_conseq'],
            'A_stance': agency_result['A_stance']
        })
        
        return aggregate_signals

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
            'equation': self.meaning_model.get_equation_string(),
            'numbers': self.meaning_model.format_numbers(S, A, D, M),
            'parameters': self.meaning_model.get_parameters_dict(),
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

    async def process(self, **kwargs) -> str:
        """
        Required implementation of abstract process method from BaseAgent.
        This method allows the agent to be used in standardized workflows.
        """
        episode_summary = kwargs.get('episode_summary', '')
        topic = kwargs.get('topic', '')
        exchanges = kwargs.get('exchanges', None)
        
        result = await self.generate_coda(episode_summary, topic, exchanges)
        
        output = f"Cognitive Coda: {result['coda']}\n\nReasoning: {result['reasoning']}"
        
        # Add enhanced mathematical model with sub-scores if present
        if 'mathematical_model' in result:
            math_model = result['mathematical_model']
            components = math_model.get('components', {})
            signals = math_model.get('signals', {})
            
            output += f"\n\n### Mathematical Model\n"
            output += f"**Equation:** {math_model['equation']}\n\n"
            
            # Enhanced display with sub-scores from Phase 6A design
            output += f"**Current Values:**\n"
            A = signals.get('A', 0)
            S = signals.get('S', 0)
            D = signals.get('D', 0)
            M = math_model.get('M', 0)
            
            output += f"- **Agency (A)**: {A:.3f}\n"
            
            # Add Agency sub-component breakdown
            if 'A_ought' in components:
                output += f"  - A_ought: {components['A_ought']:.3f}\n"
            if 'A_decis' in components:
                output += f"  - A_decis: {components['A_decis']:.3f}\n"
            if 'A_conseq' in components:
                output += f"  - A_conseq: {components['A_conseq']:.3f}\n"
            if 'A_stance' in components:
                output += f"  - A_stance: {components['A_stance']:.3f}\n"
                
            output += f"- **Structure (S)**: {S:.3f}\n"
            output += f"- **Dependence (D)**: {D:.3f}\n"
            output += f"- **Meaning (M)**: {M:.3f}\n\n"
            
            # Add parameters
            params = math_model.get('parameters', {})
            if params:
                output += f"**Parameters:** "
                param_strs = []
                for key, value in params.items():
                    param_strs.append(f"{key}={value}")
                output += ", ".join(param_strs) + "\n\n"
            
            # Add interpretation and maxim
            output += f"**Interpretation:** {math_model['verbal_axiom']}\n"
            output += f"**Maxim:** {math_model['maxim']}"
            
            # Add Next Action recommendations from Phase 6A design
            if 'recommendations' in result and result['recommendations']:
                output += f"\n\n**Next:** {'; '.join(result['recommendations'])}"
            elif A < 0.45:
                output += f"\n\n**Next:** Increase agency commitments (A < 0.45)"
            else:
                output += f"\n\n**Status:** All metrics within target ranges ✓"
        
        return output