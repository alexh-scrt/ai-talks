"""
Decision Rule Injector - Boost Agency scoring by injecting agent-specific decision rules

This module implements the Phase 6A Decision Rule Injection enhancement to ensure
each agent has decision language in their recent turns, boosting Agency scoring
from ~0.09 to target range 0.45-0.65.
"""

import re
import logging
from typing import List, Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class DecisionRuleInjector:
    """
    Tracks agents lacking decision rules and injects agent-specific templates
    
    Monitors which agents lack decision language in recent turns and injects
    appropriate decision rules matching each agent's philosophical voice.
    """
    
    # Agent-specific decision rule templates from design specification
    DECISION_RULES = {
        "simone": [
            "Therefore we should act under ambiguity by choosing the option that preserves agency even without proof.",
            "Therefore we should make commitments that remain authentic to our situation even when certainty eludes us.",
            "Therefore we should embrace the absurd and choose meaning-making despite metaphysical uncertainty."
        ],
        "aristotle": [
            "Therefore we should cultivate courage as the mean when evidence is undecidable.",
            "Therefore we should pursue practical wisdom through deliberation when theoretical knowledge fails.",
            "Therefore we should act according to virtue even when outcomes remain uncertain."
        ],
        "descartes": [
            "Therefore we should suspend assent but proceed with provisional maxims.",
            "Therefore we should distinguish clear reasoning from uncertain premises in our decisions.",
            "Therefore we should maintain methodical doubt while adopting practical rules for action."
        ],
        "hypatia": [
            "Therefore we should privilege mathematically coherent policies when metaphysics is uncertain.",
            "Therefore we should apply geometric reasoning to ethical choices where proof is unavailable.",
            "Therefore we should seek logical consistency in our principles even when ultimate truth remains hidden."
        ],
        "lao": [
            "Therefore we should avoid forcing outcomes and favor low-regret actions that accord with the flow.",
            "Therefore we should act through non-action, letting patterns emerge rather than imposing structure.",
            "Therefore we should follow the natural way, choosing simplicity over artificial complexity."
        ]
    }
    
    # Patterns that indicate existing decision language
    DECISION_LANGUAGE_PATTERNS = [
        r'\b(therefore|thus|hence)\s+we\s+(should|must|shall|will|choose|decide)\b',
        r'\bI\s+(decide|will|choose|commit|refuse)\b',
        r'\bwe\s+(should|must|will)\s+\w+',
        r'\bdecision\s+rule\b',
        r'\bmaxim\b',
        r'\bcommitment\b',
        r'\bact\s+under\s+ambiguity\b',
        r'\bproceed\s+with\b',
        r'\bchoose\s+\w+\s+despite\b'
    ]
    
    def __init__(self, window_size: int = 8):
        """
        Initialize decision rule injector
        
        Args:
            window_size: Number of recent turns to analyze for decision language
        """
        self.window_size = window_size
        self.rules_used = defaultdict(int)  # Track rule rotation per agent
        
        # Compile patterns for efficiency
        self.decision_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DECISION_LANGUAGE_PATTERNS]
        
        logger.info(f"🎯 Decision Rule Injector initialized (window={window_size})")
    
    def _has_decision_language(self, content: str) -> bool:
        """
        Check if content contains decision language
        
        Args:
            content: Text to analyze for decision patterns
            
        Returns:
            True if decision language detected
        """
        for pattern in self.decision_patterns:
            if pattern.search(content):
                return True
        return False
    
    def needs_decision_rule(self, agent: str, recent_turns: List[Dict]) -> bool:
        """
        Check if agent lacks decision rule in recent window
        
        Args:
            agent: Agent name to check (case-insensitive)
            recent_turns: List of recent turn dictionaries with 'speaker' and 'content'
            
        Returns:
            True if agent needs a decision rule injected
        """
        agent_lower = agent.lower()
        
        # Get agent's turns from the window
        window_turns = recent_turns[-self.window_size:] if len(recent_turns) > self.window_size else recent_turns
        agent_turns = [turn for turn in window_turns if turn.get('speaker', '').lower() == agent_lower]
        
        # Check if any of agent's recent turns have decision language
        for turn in agent_turns:
            content = turn.get('content', '')
            if self._has_decision_language(content):
                logger.debug(f"Agent {agent} has decision language in recent turns")
                return False
        
        logger.debug(f"Agent {agent} lacks decision language in last {len(agent_turns)} turns")
        return True
    
    def get_agent_rule(self, agent: str) -> Optional[str]:
        """
        Get next decision rule for specified agent
        
        Args:
            agent: Agent name (case-insensitive)
            
        Returns:
            Decision rule text or None if agent not recognized
        """
        agent_key = agent.lower()
        
        if agent_key not in self.DECISION_RULES:
            logger.warning(f"No decision rules available for agent: {agent}")
            return None
        
        # Get next rule variant for this agent (rotating through options)
        rule_idx = self.rules_used[agent_key] % len(self.DECISION_RULES[agent_key])
        rule = self.DECISION_RULES[agent_key][rule_idx]
        self.rules_used[agent_key] += 1
        
        logger.debug(f"Selected rule variant {rule_idx} for {agent}")
        return rule
    
    def inject_rule(self, agent: str, content: str) -> str:
        """
        Inject decision rule at end of agent's turn
        
        Args:
            agent: Agent name
            content: Original turn content
            
        Returns:
            Enhanced content with decision rule appended
        """
        rule = self.get_agent_rule(agent)
        if not rule:
            logger.warning(f"Cannot inject rule for unknown agent: {agent}")
            return content
        
        # Append rule with proper formatting
        enhanced = f"{content.strip()} {rule}"
        
        # Add invisible tag for metrics detection
        enhanced += " <!-- decision_rule -->"
        
        logger.info(f"💭 Injected decision rule for {agent}")
        return enhanced
    
    def check_agent_coverage(self, recent_turns: List[Dict]) -> List[str]:
        """
        Check which agents need decision rules in recent window
        
        Args:
            recent_turns: List of recent turn dictionaries
            
        Returns:
            List of agent names needing decision rules
        """
        # Get unique agents from recent turns
        agents_in_window = set()
        window_turns = recent_turns[-self.window_size:] if len(recent_turns) > self.window_size else recent_turns
        
        for turn in window_turns:
            agent = turn.get('speaker', '').lower()
            if agent:
                agents_in_window.add(agent)
        
        # Check which agents need rules
        agents_needing_rules = []
        for agent in agents_in_window:
            if self.needs_decision_rule(agent, recent_turns):
                agents_needing_rules.append(agent)
        
        logger.debug(f"Agents needing rules: {agents_needing_rules}")
        return agents_needing_rules
    
    def get_statistics(self) -> Dict:
        """Get injection statistics"""
        return {
            'window_size': self.window_size,
            'rules_injected': dict(self.rules_used),
            'total_injections': sum(self.rules_used.values()),
            'agents_with_rules': len(self.rules_used)
        }
    
    def reset_session(self):
        """Reset for new discussion session"""
        self.rules_used.clear()
        logger.info("🔄 Decision rule injector reset for new session")


def test_decision_injector():
    """Test function for decision rule injection functionality"""
    
    # Test data - 8 turns without decision language
    test_turns = [
        {'speaker': 'simone', 'content': 'Consciousness is fascinating.'},
        {'speaker': 'aristotle', 'content': 'Indeed, quite intriguing.'},
        {'speaker': 'simone', 'content': 'The nature of awareness puzzles me.'},
        {'speaker': 'descartes', 'content': 'I find it mysterious as well.'},
        {'speaker': 'hypatia', 'content': 'Mathematics might help here.'},
        {'speaker': 'lao', 'content': 'Or perhaps simplicity is key.'},
        {'speaker': 'simone', 'content': 'These are difficult questions.'},
        {'speaker': 'aristotle', 'content': 'Philosophy often is challenging.'}
    ]
    
    # Test injection
    injector = DecisionRuleInjector(window_size=8)
    
    print("Testing decision rule injection...")
    print(f"Window size: {injector.window_size}")
    
    # Check which agents need rules
    agents_needing_rules = injector.check_agent_coverage(test_turns)
    print(f"Agents needing rules: {agents_needing_rules}")
    
    # Test specific agent checks
    for agent in ['simone', 'aristotle', 'descartes']:
        needs_rule = injector.needs_decision_rule(agent, test_turns)
        print(f"{agent} needs rule: {needs_rule}")
        
        if needs_rule:
            # Inject rule
            original = f"Uncertainty is inevitable in {agent}'s view."
            enhanced = injector.inject_rule(agent, original)
            print(f"\nOriginal: {original}")
            print(f"Enhanced: {enhanced}")
    
    # Test statistics
    stats = injector.get_statistics()
    print(f"\nStatistics: {stats}")
    
    return injector


if __name__ == "__main__":
    # Run test when executed directly
    test_decision_injector()