"""Agent for generating contextual consequence test prompts"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random

from ..utils.llm_client import LLMClient
from ..utils.text_processing import clean_llm_response


@dataclass
class ConsequenceTestContext:
    """Context for generating consequence tests"""
    tension: Tuple[str, str]
    current_claim: str
    discussion_summary: str
    turn_count: int
    previous_tests: List[str] = None
    
    def __post_init__(self):
        if self.previous_tests is None:
            self.previous_tests = []


class ConsequenceTestGenerator:
    """Generates contextual consequence test prompts to force progression"""
    
    # Template prompts for different philosophical domains
    CONSEQUENCE_TEMPLATES = {
        ("necessity", "contingency"): [
            "If {claim} is necessarily true, what follows for {domain}? Give one concrete implication or testable prediction.",
            "If {claim} is contingent rather than necessary, how would {domain} be different? Provide a specific consequence.",
            "What would we observe in {domain} if {claim} were necessarily false rather than necessarily true?"
        ],
        
        ("structure", "agency"): [
            "If {claim} about structure is correct, what does this mean for human {domain}? State one specific implication.",
            "If agency operates within the structure described by {claim}, what should we observe in {domain}?",
            "How would {domain} change if the structural constraints in {claim} were removed entirely?"
        ],
        
        ("objectivity", "subjectivity"): [
            "If {claim} represents objective truth, what follows for {domain}? Provide one testable consequence.",
            "If {claim} is merely subjective perspective, how should this affect {domain}? Give a specific prediction.",
            "What evidence in {domain} would distinguish between {claim} being objective vs subjective?"
        ],
        
        ("simulation", "reality"): [
            "If {claim} about simulation is true, what would we expect to observe in {domain}? State one prediction.",
            "If reality differs from simulation as {claim} suggests, how should {domain} reflect this difference?",
            "What test could distinguish simulated vs real aspects of {domain} given {claim}?"
        ],
        
        ("math", "ethics"): [
            "If the mathematical principle in {claim} is correct, what follows for {domain}? Give one ethical implication.",
            "How would {domain} change if the mathematical relationship in {claim} were violated?",
            "What ethical test could validate or refute the mathematical claim that {claim}?"
        ]
    }
    
    # Domain targets for consequence testing
    CONSEQUENCE_DOMAINS = [
        "free will", "moral responsibility", "knowledge", "consciousness", 
        "decision-making", "justice", "truth", "meaning", "identity",
        "existence", "causation", "time", "space", "language"
    ]
    
    # Fallback templates for unknown tensions
    GENERIC_TEMPLATES = [
        "If {claim} is true, what specific consequence follows for {domain}? Provide one testable prediction.",
        "How would {domain} be different if {claim} were false instead of true? Give a concrete example.",
        "What observable evidence in {domain} would support or refute {claim}?",
        "If we accept {claim}, what practical decision should we make regarding {domain}? State one specific action."
    ]
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the consequence test generator"""
        self.llm_client = llm_client or LLMClient()
    
    async def generate_test(self, context: ConsequenceTestContext) -> str:
        """Generate a consequence test prompt for the given context"""
        
        # Get appropriate template
        template = self._select_template(context.tension, context.previous_tests)
        
        # Select domain for testing
        domain = self._select_domain(context.tension, context.discussion_summary)
        
        # Extract or generate claim summary
        claim = self._extract_claim(context.current_claim)
        
        # Fill template
        test_prompt = template.format(claim=claim, domain=domain)
        
        # Enhance with LLM if available and needed
        if self.llm_client and len(context.previous_tests) > 0:
            test_prompt = await self._enhance_with_llm(test_prompt, context)
        
        return f"Consequence Test: {test_prompt}"
    
    def _select_template(self, tension: Tuple[str, str], previous_tests: List[str]) -> str:
        """Select appropriate template for the tension"""
        # Normalize tension order
        normalized_tension = tuple(sorted(tension))
        
        # Get templates for this tension
        templates = self.CONSEQUENCE_TEMPLATES.get(normalized_tension, self.GENERIC_TEMPLATES)
        
        # Avoid repeating similar templates
        available_templates = [t for t in templates 
                             if not any(self._templates_similar(t, prev) for prev in previous_tests)]
        
        if not available_templates:
            available_templates = templates  # Use any if all have been used
        
        return random.choice(available_templates)
    
    def _select_domain(self, tension: Tuple[str, str], discussion_summary: str) -> str:
        """Select appropriate domain for consequence testing"""
        
        # Domain preferences based on tension
        domain_preferences = {
            ("necessity", "contingency"): ["free will", "moral responsibility", "causation"],
            ("structure", "agency"): ["decision-making", "moral responsibility", "consciousness"],
            ("objectivity", "subjectivity"): ["knowledge", "truth", "consciousness"],
            ("simulation", "reality"): ["existence", "consciousness", "identity"],
            ("math", "ethics"): ["justice", "moral responsibility", "truth"]
        }
        
        normalized_tension = tuple(sorted(tension))
        preferred_domains = domain_preferences.get(normalized_tension, self.CONSEQUENCE_DOMAINS)
        
        # Check if discussion mentions any specific domains
        discussion_lower = discussion_summary.lower()
        mentioned_domains = [domain for domain in self.CONSEQUENCE_DOMAINS 
                           if domain.lower() in discussion_lower]
        
        if mentioned_domains:
            # Prefer domains already in discussion
            return random.choice(mentioned_domains)
        else:
            # Use preferred domains for this tension
            return random.choice(preferred_domains)
    
    def _extract_claim(self, current_claim: str) -> str:
        """Extract or simplify the current claim for testing"""
        # Simple extraction - could be enhanced with NLP
        claim = current_claim.strip()
        
        # Limit length for template clarity
        if len(claim) > 150:
            sentences = claim.split('. ')
            claim = sentences[0] + ('.' if not sentences[0].endswith('.') else '')
        
        return claim
    
    def _templates_similar(self, template1: str, template2: str) -> bool:
        """Check if two templates are similar to avoid repetition"""
        # Simple similarity check based on key phrases
        key_phrases1 = set(template1.lower().split())
        key_phrases2 = set(template2.lower().split())
        
        # Consider similar if they share >60% of words
        common = len(key_phrases1 & key_phrases2)
        total = len(key_phrases1 | key_phrases2)
        
        return common / total > 0.6 if total > 0 else False
    
    async def _enhance_with_llm(self, base_prompt: str, context: ConsequenceTestContext) -> str:
        """Enhance the test prompt using LLM for better context fit"""
        
        enhancement_prompt = f"""
You are helping improve a philosophical consequence test. The current discussion has explored {context.tension[0]} vs {context.tension[1]} for {context.turn_count} turns.

Discussion summary: {context.discussion_summary}

Current test prompt: {base_prompt}

Previous tests used: {'; '.join(context.previous_tests[-2:]) if context.previous_tests else 'None'}

Please improve this consequence test to:
1. Better fit the specific discussion context
2. Avoid repetition of previous tests
3. Force a concrete, testable prediction
4. Stay focused on one clear consequence

Respond with just the improved test prompt (without any prefix).
"""
        
        try:
            response = await self.llm_client.complete(enhancement_prompt)
            
            # Use comprehensive cleaning to remove reasoning blocks and format properly
            enhanced = clean_llm_response(response, is_quote=False)
            
            # The response should be the test prompt without prefix, so we don't need to check/add it
            # since we'll add the prefix at the end of generate_test()
            
            return enhanced
        except Exception:
            # Fallback to original prompt if LLM fails
            return base_prompt
    
    def generate_synthesis_prompt(self, tension: Tuple[str, str], failed_tests: List[str], 
                                discussion_summary: str) -> str:
        """Generate synthesis prompt when consequence tests fail"""
        
        synthesis_templates = [
            "Synthesis: The discussion of {tension_a} vs {tension_b} has reached an impasse. "
            "The key insight is {summary}. Consequence: {consequence}. "
            "Pivot: Let's examine this through {new_focus}.",
            
            "Voice of Reason: Both sides agree that {tension_a} and {tension_b} interact, "
            "but disagree on {disagreement}. If true, we should observe {prediction}. "
            "New focus: {new_focus}.",
            
            "Synthesis: The {tension_a}/{tension_b} tension reveals {insight}. "
            "Critical test: {test}. Moving to {new_focus} to explore implications."
        ]
        
        template = random.choice(synthesis_templates)
        
        # Extract key elements (simplified)
        tension_a, tension_b = tension
        summary = self._summarize_discussion(discussion_summary)
        consequence = self._generate_consequence(tension, discussion_summary)
        new_focus = self._select_pivot_focus(tension)
        
        return template.format(
            tension_a=tension_a,
            tension_b=tension_b,
            summary=summary,
            consequence=consequence,
            disagreement=f"the relationship between {tension_a} and {tension_b}",
            prediction=f"measurable differences in how {tension_a} affects outcomes",
            insight=f"that {tension_a} and {tension_b} are not simply opposed",
            test=f"whether {tension_a} can be separated from {tension_b} empirically",
            new_focus=new_focus
        )
    
    def _summarize_discussion(self, discussion_summary: str) -> str:
        """Create brief summary for synthesis"""
        # Simplified extraction
        if len(discussion_summary) > 100:
            return discussion_summary[:97] + "..."
        return discussion_summary
    
    def _generate_consequence(self, tension: Tuple[str, str], discussion_summary: str) -> str:
        """Generate consequence statement for synthesis"""
        tension_a, tension_b = tension
        return f"if {tension_a} and {tension_b} both operate, we need criteria to distinguish their effects"
    
    def _select_pivot_focus(self, current_tension: Tuple[str, str]) -> str:
        """Select new focus for pivoting away from current tension"""
        # Get all tensions and pick a different one
        all_tensions = list(self.CONSEQUENCE_TEMPLATES.keys()) + [
            ("determinism", "freedom"), ("universal", "particular"), 
            ("mind", "matter"), ("being", "becoming")
        ]
        
        # Remove current tension
        normalized_current = tuple(sorted(current_tension))
        other_tensions = [t for t in all_tensions if tuple(sorted(t)) != normalized_current]
        
        if other_tensions:
            new_tension = random.choice(other_tensions)
            return f"{new_tension[0]} vs {new_tension[1]}"
        else:
            return "a concrete application case"