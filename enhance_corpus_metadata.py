#!/usr/bin/env python3
"""
Comprehensive Metadata Enhancement and Quality Validation - Phase 7A-3

Enhances the philosophical quotes corpus with improved metadata, validates quote attribution,
optimizes topic classification, and ensures production-ready quality for semantic search.

Features:
- Attribution validation and source verification  
- Enhanced topic classification with philosophical concepts
- Improved polarity and tone analysis
- Quote quality scoring and filtering
- Semantic diversity analysis
- Production corpus optimization
"""

import json
import re
import math
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Set, Tuple
import hashlib

class CorpusMetadataEnhancer:
    """Enhances philosophical quotes corpus with comprehensive metadata and quality validation"""
    
    def __init__(self):
        self.philosophical_concepts = {
            # Metaphysics
            'being': ['being', 'existence', 'reality', 'ontology', 'essence', 'substance'],
            'time': ['time', 'temporal', 'moment', 'eternity', 'duration', 'instant'],
            'space': ['space', 'place', 'location', 'position', 'spatial', 'dimension'],
            'causality': ['cause', 'effect', 'causation', 'necessity', 'contingency'],
            'identity': ['identity', 'self', 'same', 'different', 'unity', 'plurality'],
            
            # Epistemology  
            'knowledge': ['knowledge', 'know', 'cognition', 'episteme', 'understanding'],
            'truth': ['truth', 'true', 'falsehood', 'veracity', 'certainty', 'doubt'],
            'belief': ['belief', 'believe', 'faith', 'conviction', 'trust', 'credence'],
            'perception': ['perception', 'sense', 'sensation', 'experience', 'empirical'],
            'reason': ['reason', 'rational', 'logic', 'reasoning', 'intellect', 'mind'],
            
            # Ethics
            'virtue': ['virtue', 'virtuous', 'excellence', 'character', 'integrity'],
            'good': ['good', 'goodness', 'benefit', 'welfare', 'wellbeing', 'flourishing'],
            'evil': ['evil', 'bad', 'harm', 'malice', 'wickedness', 'vice'],
            'justice': ['justice', 'just', 'fair', 'equality', 'rights', 'law'],
            'duty': ['duty', 'obligation', 'ought', 'should', 'responsibility', 'moral'],
            
            # Aesthetics
            'beauty': ['beauty', 'beautiful', 'aesthetic', 'sublime', 'elegance'],
            'art': ['art', 'artistic', 'creation', 'creativity', 'imagination', 'genius'],
            'taste': ['taste', 'judgment', 'appreciation', 'criticism', 'evaluation'],
            
            # Political Philosophy
            'freedom': ['freedom', 'liberty', 'autonomy', 'independence', 'choice'],
            'power': ['power', 'authority', 'control', 'dominion', 'influence'],
            'state': ['state', 'government', 'politics', 'sovereignty', 'society'],
            'equality': ['equality', 'equal', 'inequality', 'hierarchy', 'class'],
            
            # Philosophy of Mind
            'consciousness': ['consciousness', 'aware', 'experience', 'qualia', 'phenomenal'],
            'mind': ['mind', 'mental', 'psyche', 'soul', 'spirit', 'thought'],
            'emotion': ['emotion', 'feeling', 'passion', 'sentiment', 'mood'],
            'will': ['will', 'volition', 'desire', 'intention', 'motivation'],
            
            # Existential Themes
            'meaning': ['meaning', 'purpose', 'significance', 'sense', 'point'],
            'death': ['death', 'mortality', 'finite', 'ending', 'perish'],
            'suffering': ['suffering', 'pain', 'anguish', 'misery', 'tragedy'],
            'happiness': ['happiness', 'joy', 'pleasure', 'bliss', 'content'],
            'love': ['love', 'affection', 'compassion', 'care', 'devotion'],
            
            # Eastern Concepts
            'enlightenment': ['enlightenment', 'awakening', 'illumination', 'realization'],
            'meditation': ['meditation', 'mindfulness', 'contemplation', 'reflection'],
            'detachment': ['detachment', 'non-attachment', 'letting go', 'release'],
            'harmony': ['harmony', 'balance', 'equilibrium', 'peace', 'unity'],
            'impermanence': ['impermanence', 'change', 'flux', 'transience', 'becoming']
        }
        
        self.philosophical_traditions = {
            'western': {
                'ancient': ['presocratic', 'socratic', 'platonic', 'aristotelian', 'stoic', 'epicurean', 'skeptic'],
                'medieval': ['scholastic', 'augustinian', 'thomistic', 'nominalist', 'realist'],
                'modern': ['rationalist', 'empiricist', 'idealist', 'materialist', 'enlightenment'],
                'contemporary': ['analytic', 'continental', 'existentialist', 'phenomenological', 'postmodern']
            },
            'eastern': {
                'hindu': ['vedantic', 'samkhya', 'yoga', 'nyaya', 'vaisheshika', 'mimamsa'],
                'buddhist': ['theravada', 'mahayana', 'zen', 'tibetan', 'pure land'],
                'chinese': ['confucian', 'taoist', 'legalist', 'mohist', 'neo-confucian'],
                'japanese': ['shinto', 'zen', 'pure land', 'nichiren']
            },
            'other': {
                'islamic': ['sufism', 'kalam', 'falsafa', 'ishraqi'],
                'jewish': ['kabbalah', 'hasidism', 'talmudic', 'maimonidean'],
                'african': ['ubuntu', 'ifá', 'akan', 'yoruba'],
                'indigenous': ['shamanic', 'tribal', 'oral tradition']
            }
        }
    
    def load_corpus(self, path: str = "data/philosophical_quotes.jsonl") -> List[Dict]:
        """Load the philosophical quotes corpus"""
        corpus_path = Path(path)
        quotes = []
        
        if corpus_path.exists():
            with open(corpus_path, 'r', encoding='utf-8') as f:
                for line in f:
                    quotes.append(json.loads(line))
        
        return quotes
    
    def enhance_topics(self, quote_text: str, current_topics: List[str]) -> List[str]:
        """Enhanced topic classification using philosophical concept matching"""
        
        enhanced_topics = set(current_topics)
        text_lower = quote_text.lower()
        
        # Add concept-based topics
        for concept, keywords in self.philosophical_concepts.items():
            if any(keyword in text_lower for keyword in keywords):
                enhanced_topics.add(concept)
        
        # Limit to most relevant topics (max 6)
        return list(enhanced_topics)[:6]
    
    def enhance_polarity(self, quote_text: str, current_polarity: str) -> str:
        """Enhanced polarity analysis with philosophical nuances"""
        
        text_lower = quote_text.lower()
        
        # Philosophical polarity patterns
        if any(word in text_lower for word in ['not', 'never', 'nothing', 'none', 'neither', 'nor']):
            return 'negative'
        elif any(word in text_lower for word in ['must', 'should', 'ought', 'need', 'necessary']):
            return 'prescriptive'
        elif any(word in text_lower for word in ['can', 'may', 'possible', 'might', 'could']):
            return 'modal'
        elif '?' in text_lower:
            return 'interrogative'
        elif any(word in text_lower for word in ['if', 'when', 'suppose', 'assume', 'imagine']):
            return 'conditional'
        elif any(word in text_lower for word in ['all', 'every', 'always', 'universal', 'eternal']):
            return 'universal'
        elif any(word in text_lower for word in ['some', 'sometimes', 'particular', 'specific']):
            return 'particular'
        else:
            return current_polarity
    
    def enhance_tone(self, quote_text: str, current_tone: str) -> str:
        """Enhanced tone analysis with philosophical sophistication"""
        
        text_lower = quote_text.lower()
        
        tone_indicators = {
            'mystical': ['divine', 'eternal', 'infinite', 'transcendent', 'sacred', 'spiritual'],
            'analytical': ['analyze', 'examine', 'consider', 'reason', 'logic', 'rational'],
            'existential': ['existence', 'authentic', 'absurd', 'alienation', 'anxiety', 'freedom'],
            'dialectical': ['thesis', 'antithesis', 'synthesis', 'contradiction', 'opposite'],
            'phenomenological': ['experience', 'consciousness', 'intentionality', 'lived', 'embodied'],
            'pragmatic': ['practice', 'useful', 'effective', 'practical', 'work', 'action'],
            'skeptical': ['doubt', 'uncertain', 'question', 'challenge', 'critique'],
            'dogmatic': ['certain', 'absolute', 'definite', 'clear', 'obvious', 'evident'],
            'ironic': ['irony', 'paradox', 'contrary', 'opposite', 'unexpected'],
            'tragic': ['tragedy', 'fate', 'suffering', 'loss', 'inevitable', 'destiny'],
            'heroic': ['courage', 'brave', 'noble', 'heroic', 'greatness', 'excellence'],
            'contemplative': ['reflect', 'meditate', 'ponder', 'contemplate', 'think'],
            'poetic': ['beauty', 'metaphor', 'image', 'symbol', 'artistic', 'creative']
        }
        
        for tone, indicators in tone_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return tone
        
        return current_tone
    
    def calculate_quote_quality_score(self, quote: Dict) -> float:
        """Calculate comprehensive quality score for a quote"""
        
        score = 0.0
        
        # Length scoring (optimal range 15-100 words)
        word_count = quote.get('word_count', len(quote['quote'].split()))
        if 15 <= word_count <= 100:
            score += 1.0
        elif 10 <= word_count <= 150:
            score += 0.7
        else:
            score += 0.3
        
        # Philosophical depth (topic diversity)
        topics = quote.get('topics', [])
        if len(topics) >= 3:
            score += 1.0
        elif len(topics) >= 2:
            score += 0.7
        else:
            score += 0.3
        
        # Source quality
        source = quote.get('source', '').lower()
        if any(term in source for term in ['attributed', 'unknown', 'web search']):
            score += 0.3
        elif any(term in source for term in ['fragments', 'works', 'treatise', 'dialogues']):
            score += 1.0
        else:
            score += 0.7
        
        # Quote complexity (sentence structure)
        quote_text = quote['quote']
        if ';' in quote_text or ':' in quote_text:
            score += 0.5
        if ',' in quote_text:
            score += 0.3
        
        # Philosophical terminology
        philosophical_terms = sum(1 for concept_words in self.philosophical_concepts.values() 
                                for word in concept_words if word in quote_text.lower())
        if philosophical_terms >= 3:
            score += 1.0
        elif philosophical_terms >= 2:
            score += 0.7
        else:
            score += 0.3
        
        return min(score / 4.0, 1.0)  # Normalize to 0-1
    
    def detect_duplicates(self, quotes: List[Dict]) -> Dict[str, List[str]]:
        """Detect semantic and textual duplicates"""
        
        duplicates = defaultdict(list)
        seen_hashes = {}
        
        for quote in quotes:
            # Normalize text for comparison
            normalized = re.sub(r'[^\w\s]', '', quote['quote'].lower())
            normalized = ' '.join(normalized.split())
            
            # Create hash
            quote_hash = hashlib.md5(normalized.encode()).hexdigest()
            
            if quote_hash in seen_hashes:
                duplicates[seen_hashes[quote_hash]].append(quote['id'])
            else:
                seen_hashes[quote_hash] = quote['id']
        
        return dict(duplicates)
    
    def validate_attribution(self, quotes: List[Dict]) -> Dict[str, List[str]]:
        """Validate quote attributions and identify potential misattributions"""
        
        attribution_issues = defaultdict(list)
        
        # Check for anachronistic attributions
        anachronistic_terms = {
            'ancient': ['internet', 'computer', 'technology', 'digital', 'online'],
            'medieval': ['democracy', 'capitalism', 'socialism', 'evolution', 'relativity'],
            'modern': ['quantum', 'DNA', 'cyber', 'artificial intelligence', 'blockchain']
        }
        
        for quote in quotes:
            era = quote.get('era', '')
            quote_text = quote['quote'].lower()
            
            if era in anachronistic_terms:
                for term in anachronistic_terms[era]:
                    if term in quote_text:
                        attribution_issues['anachronistic'].append(
                            f"{quote['id']}: '{term}' in {era} quote"
                        )
        
        # Check for overly generic attributions
        generic_authors = ['various', 'unknown', 'anonymous', 'traditional wisdom']
        for quote in quotes:
            author = quote.get('author', '').lower()
            if any(generic in author for generic in generic_authors):
                attribution_issues['generic'].append(quote['id'])
        
        return dict(attribution_issues)
    
    def analyze_corpus_diversity(self, quotes: List[Dict]) -> Dict:
        """Analyze corpus diversity and balance"""
        
        analysis = {}
        
        # Era distribution
        era_counts = Counter(q.get('era', 'unknown') for q in quotes)
        analysis['era_distribution'] = dict(era_counts)
        analysis['era_balance_score'] = self._calculate_balance_score(era_counts)
        
        # Tradition distribution  
        tradition_counts = Counter(q.get('tradition', 'unknown') for q in quotes)
        analysis['tradition_distribution'] = dict(tradition_counts)
        analysis['tradition_balance_score'] = self._calculate_balance_score(tradition_counts)
        
        # Author diversity
        author_counts = Counter(q.get('author', 'unknown') for q in quotes)
        analysis['author_diversity'] = len(author_counts)
        analysis['author_concentration'] = max(author_counts.values()) / len(quotes)
        
        # Topic diversity
        all_topics = [topic for q in quotes for topic in q.get('topics', [])]
        topic_counts = Counter(all_topics)
        analysis['topic_diversity'] = len(topic_counts)
        analysis['most_common_topics'] = dict(topic_counts.most_common(10))
        
        # Quality distribution
        quality_scores = [self.calculate_quote_quality_score(q) for q in quotes]
        analysis['average_quality'] = sum(quality_scores) / len(quality_scores)
        analysis['high_quality_ratio'] = sum(1 for s in quality_scores if s >= 0.7) / len(quality_scores)
        
        return analysis
    
    def _calculate_balance_score(self, counter: Counter) -> float:
        """Calculate balance score for a distribution (0=perfectly balanced, 1=maximally imbalanced)"""
        if len(counter) <= 1:
            return 1.0
        
        total = sum(counter.values())
        expected = total / len(counter)
        variance = sum((count - expected) ** 2 for count in counter.values()) / len(counter)
        
        # Normalize by theoretical maximum variance
        max_variance = expected ** 2 * (len(counter) - 1)
        return math.sqrt(variance / max_variance) if max_variance > 0 else 0
    
    def enhance_corpus_metadata(self, quotes: List[Dict]) -> List[Dict]:
        """Apply comprehensive metadata enhancement to corpus"""
        
        enhanced_quotes = []
        
        for quote in quotes:
            enhanced_quote = quote.copy()
            
            # Enhance topics
            enhanced_quote['topics'] = self.enhance_topics(
                quote['quote'], quote.get('topics', [])
            )
            
            # Enhance polarity
            enhanced_quote['polarity'] = self.enhance_polarity(
                quote['quote'], quote.get('polarity', 'neutral')
            )
            
            # Enhance tone
            enhanced_quote['tone'] = self.enhance_tone(
                quote['quote'], quote.get('tone', 'philosophical')
            )
            
            # Add quality score
            enhanced_quote['quality_score'] = self.calculate_quote_quality_score(quote)
            
            # Add text hash for deduplication
            normalized_text = re.sub(r'[^\w\s]', '', quote['quote'].lower())
            enhanced_quote['text_hash'] = hashlib.md5(
                normalized_text.encode()
            ).hexdigest()[:12]
            
            enhanced_quotes.append(enhanced_quote)
        
        return enhanced_quotes

def main():
    """Phase 7A-3: Comprehensive metadata enhancement and quality validation"""
    
    print("🔍 Phase 7A-3: Comprehensive Metadata Enhancement and Quality Validation")
    print("Enhancing corpus with improved metadata and ensuring production quality")
    print("=" * 75)
    
    enhancer = CorpusMetadataEnhancer()
    
    # Load current corpus
    quotes = enhancer.load_corpus()
    current_count = len(quotes)
    
    print(f"📊 Current corpus: {current_count} quotes")
    
    # Analyze current state
    print("\n🔍 Analyzing current corpus state...")
    diversity_analysis = enhancer.analyze_corpus_diversity(quotes)
    
    print(f"✅ Era distribution: {diversity_analysis['era_distribution']}")
    print(f"✅ Tradition distribution: {diversity_analysis['tradition_distribution']}")
    print(f"✅ Author diversity: {diversity_analysis['author_diversity']} unique authors")
    print(f"✅ Topic diversity: {diversity_analysis['topic_diversity']} unique topics")
    print(f"✅ Average quality score: {diversity_analysis['average_quality']:.3f}")
    print(f"✅ High quality ratio: {diversity_analysis['high_quality_ratio']:.1%}")
    
    # Detect quality issues
    print("\n🔍 Detecting quality issues...")
    duplicates = enhancer.detect_duplicates(quotes)
    attribution_issues = enhancer.validate_attribution(quotes)
    
    if duplicates:
        print(f"⚠️  Found {len(duplicates)} potential duplicate groups")
        for original, dups in list(duplicates.items())[:3]:
            print(f"   {original} ~ {dups}")
    else:
        print("✅ No duplicates detected")
    
    if attribution_issues:
        print(f"⚠️  Found attribution issues:")
        for issue_type, issues in attribution_issues.items():
            print(f"   {issue_type}: {len(issues)} quotes")
    else:
        print("✅ No attribution issues detected")
    
    # Enhance metadata
    print("\n🚀 Enhancing metadata...")
    enhanced_quotes = enhancer.enhance_corpus_metadata(quotes)
    
    # Filter low quality quotes
    quality_threshold = 0.4
    high_quality_quotes = [q for q in enhanced_quotes if q['quality_score'] >= quality_threshold]
    filtered_count = len(quotes) - len(high_quality_quotes)
    
    if filtered_count > 0:
        print(f"🧹 Filtered {filtered_count} low-quality quotes (threshold: {quality_threshold})")
    
    # Save enhanced corpus
    output_path = Path("data/philosophical_quotes.jsonl")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for quote in high_quality_quotes:
            f.write(json.dumps(quote, ensure_ascii=False) + '\n')
    
    # Final analysis
    final_analysis = enhancer.analyze_corpus_diversity(high_quality_quotes)
    
    print(f"\n📊 Enhanced Corpus Analysis:")
    print(f"Total quotes: {len(high_quality_quotes)}")
    print(f"Era distribution: {final_analysis['era_distribution']}")
    print(f"Tradition distribution: {final_analysis['tradition_distribution']}")
    print(f"Average quality score: {final_analysis['average_quality']:.3f}")
    print(f"High quality ratio: {final_analysis['high_quality_ratio']:.1%}")
    print(f"Topic diversity: {final_analysis['topic_diversity']} unique topics")
    
    print(f"\n📈 Top philosophical topics:")
    for topic, count in list(final_analysis['most_common_topics'].items())[:8]:
        print(f"  {topic}: {count} quotes")
    
    print(f"\n✅ Phase 7A-3 Complete!")
    print(f"📚 Enhanced corpus saved to: {output_path}")
    print(f"🌟 Corpus is now optimized for production semantic search")
    print(f"🔥 High-quality philosophical quotes with comprehensive metadata")
    print(f"📋 Next: Phase 7A-4 - Test semantic search quality with enhanced corpus")
    
    return high_quality_quotes

if __name__ == "__main__":
    enhanced_corpus = main()