import re
from typing import Set, Dict, List
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
            # Original patterns
            r'\bif\b.*\bthen\b',
            r'\btherefore\b',
            r'\bso that\b',
            r'\bentails\b',
            r'\bmeans that\b',
            r'\bimplies\b',
            r'\bconsequently\b',
            r'\bthus\b',
            r'\bhence\b',
            r'\bit follows that\b',
            # Enhanced patterns for consequence detection
            r'\bthis leads to\b',
            r'\bresults in\b',
            r'\bcauses\b',
            r'\bbecause of this\b',
            r'\bas a result\b',
            r'\bdue to\b',
            r'\bgiven that\b.*\bwe get\b',
            r'\bfrom this\b.*\bfollows\b',
            r'\bso we have\b',
            r'\bthis yields\b',
            r'\bthat would mean\b',
            r'\bwhich suggests\b',
            r'\bindicating that\b'
        ],
        EntailmentType.APPLICATION: [
            # Original patterns
            r'\bin practice\b',
            r'\bfor example\b',
            r'\bconsider\b.*\bcase\b',
            r'\btherefore we should\b',
            r'\bwe could apply\b',
            r'\bin the scenario\b',
            r'\bthis means\b.*\bshould\b',
            r'\bin real terms\b',
            r'\bpractically speaking\b',
            # Enhanced patterns
            r'\bwe ought to\b',
            r'\bone should\b',
            r'\bwe must\b',
            r'\bthis requires\b',
            r'\bwe need to\b',
            r'\bin concrete terms\b',
            r'\bspecifically\b',
            r'\bfor instance\b',
            r'\bin particular\b',
            r'\bapplying this\b',
            r'\bin the real world\b',
            r'\bthis translates to\b',
            r'\bin everyday terms\b',
            r'\bpolicy-wise\b',
            r'\bethically speaking\b'
        ],
        EntailmentType.COUNTEREXAMPLE: [
            # Original patterns
            r'\bunless\b',
            r'\bexcept when\b',
            r'\bcounterexample\b',
            r'\bnot if\b',
            r'\bhowever\b',
            r'\bbut consider\b',
            r'\bon the contrary\b',
            r'\bcontrary to\b',
            r'\bwhat if\b.*\binstead\b',
            # Enhanced patterns
            r'\bbut what about\b',
            r'\bwhat if\b',
            r'\bexcept that\b',
            r'\bhowever\b.*\bfails\b',
            r'\bbut this breaks down\b',
            r'\bunless we consider\b',
            r'\bthis fails when\b',
            r'\bthe problem with this\b',
            r'\bcounter to this\b',
            r'\bbut imagine\b',
            r'\balternatively\b',
            r'\bon the other hand\b',
            r'\bconversely\b',
            r'\bin contrast\b'
        ],
        EntailmentType.TEST: [
            # Original patterns
            r'\bwe could test\b',
            r'\bcriterion\b',
            r'\bmeasure\b',
            r'\bobservable\b',
            r'\beverify by\b',
            r'\bexperiment\b',
            r'\btest whether\b',
            r'\bto validate\b',
            r'\bproof would be\b',
            # Enhanced patterns for consequence tests
            r'\bwe could check\b',
            r'\bto determine\b',
            r'\blet\'s see if\b',
            r'\bwe can verify\b',
            r'\bto confirm\b',
            r'\bthis predicts\b',
            r'\bwe should observe\b',
            r'\bif true.*then we\'d see\b',
            r'\bevidence would be\b',
            r'\bindicator of this\b',
            r'\bfalsifiable by\b',
            r'\btestable prediction\b',
            r'\bempirical test\b',
            r'\boperational definition\b',
            r'\bmeasurable outcome\b',
            r'\bdetectable difference\b'
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
    
    def has_consequence_pattern(self, text: str) -> bool:
        """Check if text contains consequence-specific patterns"""
        consequence_patterns = [
            r'\bif\b.*\bthen\b',
            r'\bthis (leads to|results in|causes|means)\b',
            r'\b(therefore|thus|hence|so)\b',
            r'\bwe (should|must|ought to|need to)\b',
            r'\bthis (predicts|suggests|indicates)\b',
            r'\b(testable|observable|measurable)\b'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in consequence_patterns)
    
    def get_strongest_entailment(self, text: str) -> EntailmentType:
        """Get the strongest type of entailment detected (for prioritization)"""
        entailments = self.detect(text)
        if not entailments:
            return None
        
        # Priority order: TEST > APPLICATION > IMPLICATION > COUNTEREXAMPLE
        priority = [EntailmentType.TEST, EntailmentType.APPLICATION, 
                   EntailmentType.IMPLICATION, EntailmentType.COUNTEREXAMPLE]
        
        for ent_type in priority:
            if ent_type in entailments:
                return ent_type
        
        return list(entailments)[0]  # Fallback
    
    def explain_entailments(self, text: str) -> Dict[str, List[str]]:
        """Explain which patterns triggered entailment detection"""
        text_lower = text.lower()
        explanations = {}
        
        for ent_type, patterns in self.PATTERNS.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Extract the actual matched text for better explanation
                    match = re.search(pattern, text_lower)
                    if match:
                        matches.append(match.group())
            
            if matches:
                explanations[ent_type.value] = matches
        
        return explanations
    
    def validate_consequence_response(self, test_prompt: str, response: str) -> Dict[str, any]:
        """Validate if a response to a consequence test contains meaningful entailments"""
        entailments = self.detect(response)
        has_consequence = self.has_consequence_pattern(response)
        strongest = self.get_strongest_entailment(response)
        
        # Check if response actually addresses the test
        response_lower = response.lower()
        test_lower = test_prompt.lower()
        
        # Look for keywords from the test in the response
        test_keywords = re.findall(r'\b\w+\b', test_lower)
        common_keywords = [kw for kw in test_keywords if kw in response_lower and len(kw) > 3]
        addresses_test = len(common_keywords) > 0
        
        return {
            "has_entailments": len(entailments) > 0,
            "entailment_types": [e.value for e in entailments],
            "has_consequence_pattern": has_consequence,
            "strongest_entailment": strongest.value if strongest else None,
            "addresses_test": addresses_test,
            "common_keywords": common_keywords,
            "quality_score": len(entailments) + (2 if has_consequence else 0) + (1 if addresses_test else 0)
        }