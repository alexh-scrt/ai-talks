import re
from typing import Set
from enum import Enum


class EntailmentType(Enum):
    """Types of entailments that add substantive content"""
    IMPLICATION = "implication"
    APPLICATION = "application"
    COUNTEREXAMPLE = "counterexample"
    TEST = "test"


class EntailmentDetector:
    """Detects whether a text contains new entailments"""
    
    PATTERNS = {
        EntailmentType.IMPLICATION: [
            r'\bif\b.*\bthen\b',
            r'\btherefore\b',
            r'\bso that\b',
            r'\bentails\b',
            r'\bmeans that\b',
            r'\bimplies\b',
            r'\bconsequently\b',
            r'\bthus\b',
            r'\bhence\b',
            r'\bit follows that\b'
        ],
        EntailmentType.APPLICATION: [
            r'\bin practice\b',
            r'\bfor example\b',
            r'\bconsider\b.*\bcase\b',
            r'\btherefore we should\b',
            r'\bwe could apply\b',
            r'\bin the scenario\b',
            r'\bthis means\b.*\bshould\b',
            r'\bin real terms\b',
            r'\bpractically speaking\b'
        ],
        EntailmentType.COUNTEREXAMPLE: [
            r'\bunless\b',
            r'\bexcept when\b',
            r'\bcounterexample\b',
            r'\bnot if\b',
            r'\bhowever\b',
            r'\bbut consider\b',
            r'\bon the contrary\b',
            r'\bcontrary to\b',
            r'\bwhat if\b.*\binstead\b'
        ],
        EntailmentType.TEST: [
            r'\bwe could test\b',
            r'\bcriterion\b',
            r'\bmeasure\b',
            r'\bobservable\b',
            r'\beverify by\b',
            r'\bexperiment\b',
            r'\btest whether\b',
            r'\bto validate\b',
            r'\bproof would be\b'
        ]
    }
    
    def detect(self, text: str) -> Set[EntailmentType]:
        """Detect entailment types in text"""
        text_lower = text.lower()
        found = set()
        
        for ent_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    found.add(ent_type)
                    break
        
        return found
    
    def has_entailment(self, text: str) -> bool:
        """Check if text has any entailment"""
        return len(self.detect(text)) > 0
    
    def get_entailment_summary(self, text: str) -> str:
        """Get a human-readable summary of entailments found"""
        entailments = self.detect(text)
        if not entailments:
            return "No entailments detected"
        
        return f"Entailments: {', '.join(e.value for e in entailments)}"