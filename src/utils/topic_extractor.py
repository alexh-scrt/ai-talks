"""Topic extraction for philosophical concepts using hybrid keyword + embedding approach"""

import re
from typing import Set, List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class TopicLexicon:
    """Lexicon for a philosophical topic"""
    name: str
    keywords: Set[str]
    phrases: Set[str] = None
    
    def __post_init__(self):
        if self.phrases is None:
            self.phrases = set()


class TopicExtractor:
    """Extracts philosophical topics from text using keywords and semantic patterns"""
    
    # Core philosophical tensions from design document
    TENSIONS = [
        ("necessity", "contingency"),
        ("structure", "agency"),
        ("objectivity", "subjectivity"),
        ("simulation", "reality"),
        ("math", "ethics"),
        ("determinism", "freedom"),
        ("universal", "particular"),
        ("mind", "matter"),
        ("being", "becoming"),
        ("one", "many"),
        ("consciousness", "objectivity")
    ]
    
    # Keyword lexicons for fast topic detection
    LEXICONS = {
        "necessity": TopicLexicon(
            name="necessity",
            keywords={
                "necessity", "necessary", "must", "determinism", "fate", "lawbound",
                "inevitable", "required", "essential", "compulsory", "forced",
                "predetermined", "destined", "unavoidable", "fixed", "certain"
            },
            phrases={
                "has to be", "cannot be otherwise", "necessarily follows",
                "by logical necessity", "must be the case", "no other possibility"
            }
        ),
        
        "contingency": TopicLexicon(
            name="contingency",
            keywords={
                "contingent", "arbitrary", "accident", "chance", "could-have-been",
                "optional", "possible", "random", "uncertain", "variable",
                "circumstantial", "conditional", "dependent", "flexible", "open"
            },
            phrases={
                "could be otherwise", "might have been", "depends on",
                "by chance", "accidentally", "contingent upon", "optionally"
            }
        ),
        
        "structure": TopicLexicon(
            name="structure",
            keywords={
                "structure", "code", "law", "rule", "order", "grammar", "lattice",
                "system", "framework", "pattern", "organization", "hierarchy",
                "constraint", "limit", "boundary", "form", "architecture"
            },
            phrases={
                "structured by", "follows rules", "systematic order",
                "organizational pattern", "formal structure", "governed by laws"
            }
        ),
        
        "agency": TopicLexicon(
            name="agency",
            keywords={
                "agency", "choice", "will", "decide", "responsibility", "freedom",
                "autonomy", "control", "intention", "action", "deliberation",
                "volition", "self-determination", "liberty", "empowerment"
            },
            phrases={
                "free to choose", "act deliberately", "exercise agency",
                "take responsibility", "autonomous decision", "intentional action"
            }
        ),
        
        "objectivity": TopicLexicon(
            name="objectivity",
            keywords={
                "objectivity", "objective", "fact", "truth", "reality", "universal",
                "impartial", "neutral", "mind-independent", "absolute", "certain",
                "empirical", "measurable", "verifiable", "scientific", "evidence"
            },
            phrases={
                "objectively true", "mind-independent reality", "factual matter",
                "empirically verifiable", "universally valid", "scientific fact"
            }
        ),
        
        "subjectivity": TopicLexicon(
            name="subjectivity",
            keywords={
                "subjectivity", "subjective", "perspective", "opinion", "experience",
                "personal", "individual", "relative", "interpretation", "bias",
                "phenomenal", "consciousness", "qualia", "lived", "felt"
            },
            phrases={
                "from my perspective", "subjective experience", "personal view",
                "individually relative", "phenomenal consciousness", "lived experience"
            }
        ),
        
        "simulation": TopicLexicon(
            name="simulation",
            keywords={
                "simulation", "virtual", "artificial", "computational", "digital",
                "programmed", "encoded", "algorithmic", "synthetic", "modeled",
                "emulated", "simulated", "code-based", "matrix", "virtualized"
            },
            phrases={
                "simulated reality", "virtual world", "computational model",
                "digital simulation", "programmed environment", "artificial reality"
            }
        ),
        
        "reality": TopicLexicon(
            name="reality",
            keywords={
                "reality", "real", "actual", "physical", "material", "concrete",
                "substantive", "fundamental", "basic", "ground", "authentic",
                "genuine", "natural", "original", "base", "foundational"
            },
            phrases={
                "actual reality", "physical world", "material existence",
                "fundamental reality", "ground of being", "base level reality"
            }
        ),
        
        "math": TopicLexicon(
            name="math",
            keywords={
                "math", "mathematical", "logic", "formal", "proof", "theorem",
                "calculation", "quantitative", "numerical", "equation", "formula",
                "abstract", "precise", "rigorous", "analytical", "systematic"
            },
            phrases={
                "mathematical proof", "logical system", "formal analysis",
                "quantitative measure", "rigorous calculation", "systematic logic"
            }
        ),
        
        "ethics": TopicLexicon(
            name="ethics",
            keywords={
                "ethics", "moral", "ethical", "ought", "should", "right", "wrong",
                "good", "bad", "virtue", "duty", "obligation", "responsibility",
                "justice", "fairness", "value", "principle", "conscience"
            },
            phrases={
                "morally right", "ethical duty", "ought to do", "moral obligation",
                "ethically responsible", "right and wrong", "moral principle"
            }
        ),
        
        "consciousness": TopicLexicon(
            name="consciousness",
            keywords={
                "consciousness", "conscious", "awareness", "experience", "qualia",
                "subjective", "phenomenal", "sentience", "sentient", "mind",
                "mental", "cognitive", "perception", "feeling", "sensation"
            },
            phrases={
                "conscious experience", "subjective awareness", "phenomenal consciousness",
                "mental states", "first-person experience", "inner experience"
            }
        )
    }
    
    def __init__(self):
        """Initialize topic extractor"""
        # Compile regex patterns for efficiency
        self._keyword_patterns = {}
        self._phrase_patterns = {}
        
        for topic, lexicon in self.LEXICONS.items():
            # Create word boundary patterns for keywords
            keyword_pattern = r'\b(?:' + '|'.join(re.escape(kw) for kw in lexicon.keywords) + r')\b'
            self._keyword_patterns[topic] = re.compile(keyword_pattern, re.IGNORECASE)
            
            # Create phrase patterns
            if lexicon.phrases:
                phrase_pattern = r'(?:' + '|'.join(re.escape(phrase) for phrase in lexicon.phrases) + r')'
                self._phrase_patterns[topic] = re.compile(phrase_pattern, re.IGNORECASE)
    
    def extract_topics(self, text: str) -> Set[str]:
        """Extract topics from text using keyword matching"""
        text_lower = text.lower()
        found_topics = set()
        
        for topic, pattern in self._keyword_patterns.items():
            if pattern.search(text_lower):
                found_topics.add(topic)
        
        # Also check phrase patterns
        for topic, pattern in self._phrase_patterns.items():
            if pattern.search(text_lower):
                found_topics.add(topic)
        
        return found_topics
    
    def detect_tensions(self, text: str, recent_topics: List[Set[str]] = None, window: int = 2) -> Set[Tuple[str, str]]:
        """Detect active tensions in current text considering recent context"""
        current_topics = self.extract_topics(text)
        
        # Combine current topics with recent topics
        all_topics = current_topics.copy()
        if recent_topics:
            for recent in recent_topics[-window:]:
                all_topics.update(recent)
        
        # Find active tensions
        active_tensions = set()
        for tension_a, tension_b in self.TENSIONS:
            if tension_a in all_topics and tension_b in all_topics:
                # Normalize order for consistent representation
                normalized = tuple(sorted([tension_a, tension_b]))
                active_tensions.add(normalized)
        
        return active_tensions
    
    def get_tension_summary(self, text: str, recent_topics: List[Set[str]] = None) -> Dict[str, any]:
        """Get comprehensive tension analysis for text"""
        current_topics = self.extract_topics(text)
        active_tensions = self.detect_tensions(text, recent_topics)
        
        return {
            "current_topics": current_topics,
            "active_tensions": active_tensions,
            "tension_count": len(active_tensions),
            "topic_count": len(current_topics),
            "has_tensions": len(active_tensions) > 0
        }
    
    def get_topic_lexicon(self, topic: str) -> TopicLexicon:
        """Get lexicon for a specific topic"""
        return self.LEXICONS.get(topic)
    
    def get_all_tensions(self) -> List[Tuple[str, str]]:
        """Get all recognized philosophical tensions"""
        return self.TENSIONS.copy()
    
    def explain_detection(self, text: str) -> Dict[str, any]:
        """Explain what topics were detected and why"""
        explanations = {}
        
        for topic, lexicon in self.LEXICONS.items():
            matches = {"keywords": [], "phrases": []}
            
            # Check keyword matches
            for keyword in lexicon.keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                    matches["keywords"].append(keyword)
            
            # Check phrase matches
            for phrase in lexicon.phrases:
                if phrase.lower() in text.lower():
                    matches["phrases"].append(phrase)
            
            if matches["keywords"] or matches["phrases"]:
                explanations[topic] = matches
        
        return explanations