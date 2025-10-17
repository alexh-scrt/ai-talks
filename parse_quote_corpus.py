#!/usr/bin/env python3
"""
Quote Corpus Parser with Aggressive Duplicate Elimination

Parses quote files q0.json - q15.json, applies author filtering,
eliminates duplicates, and creates a unified philosophical quote corpus.
"""

import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuoteCorpusParser:
    """Parses and filters quote corpus with aggressive duplicate elimination"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        
        # Author field filtering rules
        self.included_fields = {
            'philosophy', 'physics', 'mathematics', 'biology', 'chemistry', 
            'astronomy', 'literature', 'political philosophy', 'computer science',
            'science', 'philosophy of science', 'political theory', 'ethics',
            'theology', 'history', 'economics', 'psychology', 'cognitive science',
            'existentialism', 'stoicism', 'buddhism', 'taoism', 'confucianism',
            'rationalism', 'empiricism', 'idealism', 'pragmatism', 'phenomenology',
            'analytical philosophy', 'continental philosophy', 'ancient philosophy',
            'medieval philosophy', 'modern philosophy', 'contemporary philosophy'
        }
        
        self.excluded_fields = {
            'music', 'hip-hop', 'rap', 'entertainment', 'activism', 'liberal activism',
            'social activism', 'art' # standalone art, but art/science is ok
        }
        
        # Duplicate tracking
        self.seen_quotes: Set[str] = set()  # Normalized quote text hashes
        self.seen_combinations: Set[str] = set()  # Author+quote combinations
        self.similar_quotes: List[Tuple[str, str, float]] = []  # For fuzzy matching
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'field_filtered': 0,
            'exact_duplicates': 0,
            'fuzzy_duplicates': 0,
            'final_count': 0,
            'authors_count': 0,
            'field_distribution': defaultdict(int)
        }
    
    def normalize_quote_text(self, text: str) -> str:
        """Normalize quote text for duplicate detection"""
        # Remove quotes, normalize whitespace, lowercase
        normalized = re.sub(r'^["\'„"'']|["\'""'']$', '', text.strip())
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = normalized.lower().strip()
        return normalized
    
    def get_text_hash(self, text: str) -> str:
        """Get hash of normalized text for exact duplicate detection"""
        normalized = self.normalize_quote_text(text)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two quotes (0-1)"""
        norm1 = self.normalize_quote_text(text1)
        norm2 = self.normalize_quote_text(text2)
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def is_field_included(self, field: str) -> bool:
        """Check if author field should be included"""
        field_lower = field.lower()
        
        # Check for exclusions first
        for excluded in self.excluded_fields:
            if excluded in field_lower:
                # Exception: allow art combined with science/philosophy
                if 'art' in excluded and ('science' in field_lower or 'philosophy' in field_lower):
                    continue
                return False
        
        # Check for inclusions
        for included in self.included_fields:
            if included in field_lower:
                return True
        
        # Default: include if it looks academic/intellectual
        academic_indicators = ['theory', 'studies', 'research', 'scholar', 'academic']
        return any(indicator in field_lower for indicator in academic_indicators)
    
    def is_fuzzy_duplicate(self, quote_text: str, threshold: float = 0.95) -> bool:
        """Check if quote is too similar to existing quotes"""
        normalized = self.normalize_quote_text(quote_text)
        
        # Quick check against recent quotes (performance optimization)
        recent_quotes = list(self.similar_quotes)[-1000:]  # Check last 1000
        
        for existing_text, _, _ in recent_quotes:
            similarity = self.similarity_score(normalized, existing_text)
            if similarity >= threshold:
                self.similar_quotes.append((normalized, existing_text, similarity))
                return True
        
        self.similar_quotes.append((normalized, "", 0.0))
        return False
    
    def generate_quote_id(self, author: str, index: int) -> str:
        """Generate standardized quote ID"""
        author_slug = re.sub(r'[^a-zA-Z0-9]', '_', author.lower())
        author_slug = re.sub(r'_+', '_', author_slug).strip('_')
        return f"{author_slug}::{index:03d}"
    
    def classify_author_metadata(self, author: str, field: str) -> Dict[str, str]:
        """Classify author by era and tradition for metadata"""
        author_lower = author.lower()
        field_lower = field.lower()
        
        # Era classification
        era = 'contemporary'  # default
        if any(name in author_lower for name in ['aristotle', 'plato', 'socrates', 'confucius', 'buddha', 'lao']):
            era = 'ancient'
        elif any(name in author_lower for name in ['descartes', 'kant', 'hume', 'spinoza', 'locke']):
            era = 'modern'
        elif any(name in author_lower for name in ['nietzsche', 'sartre', 'wittgenstein', 'russell']):
            era = 'contemporary'
        
        # Tradition classification
        tradition = 'western'  # default
        if any(indicator in field_lower for indicator in ['buddhism', 'taoism', 'confucianism', 'zen']):
            tradition = 'eastern'
        elif any(indicator in field_lower for indicator in ['islamic', 'sufism', 'jewish']):
            tradition = 'other'
        
        return {'era': era, 'tradition': tradition}
    
    def extract_topics_from_meaning(self, meaning: str) -> List[str]:
        """Extract philosophical topics from quote meaning"""
        topic_keywords = {
            'knowledge': ['knowledge', 'know', 'learn', 'understand', 'wisdom'],
            'truth': ['truth', 'true', 'reality', 'real'],
            'existence': ['existence', 'being', 'life', 'death'],
            'consciousness': ['consciousness', 'mind', 'thought', 'awareness'],
            'virtue': ['virtue', 'good', 'moral', 'ethics', 'right'],
            'freedom': ['freedom', 'liberty', 'choice', 'free'],
            'time': ['time', 'temporal', 'moment', 'present'],
            'change': ['change', 'transform', 'become'],
            'justice': ['justice', 'fair', 'equal'],
            'meaning': ['meaning', 'purpose', 'significance']
        }
        
        meaning_lower = meaning.lower()
        topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in meaning_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:3]  # Limit to 3 most relevant topics
    
    def parse_file(self, file_path: Path) -> List[Dict]:
        """Parse a single quote file"""
        logger.info(f"📚 Parsing {file_path.name}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        quotes = data.get('quotes', [])
        parsed_quotes = []
        author_counters = defaultdict(int)
        
        for quote_data in quotes:
            self.stats['total_processed'] += 1
            
            # Extract fields
            author = quote_data.get('author', 'Unknown')
            field = quote_data.get('field', '')
            quote_text = quote_data.get('quote', '')
            meaning = quote_data.get('meaning', '')
            
            # Field filtering
            if not self.is_field_included(field):
                self.stats['field_filtered'] += 1
                continue
            
            # Exact duplicate check
            quote_hash = self.get_text_hash(quote_text)
            if quote_hash in self.seen_quotes:
                self.stats['exact_duplicates'] += 1
                continue
            
            # Author+quote combination check
            combination = f"{author.lower()}||{self.normalize_quote_text(quote_text)}"
            if combination in self.seen_combinations:
                self.stats['exact_duplicates'] += 1
                continue
            
            # Fuzzy duplicate check
            if self.is_fuzzy_duplicate(quote_text):
                self.stats['fuzzy_duplicates'] += 1
                continue
            
            # Generate ID and metadata
            author_counters[author] += 1
            quote_id = self.generate_quote_id(author, author_counters[author])
            
            metadata = self.classify_author_metadata(author, field)
            topics = self.extract_topics_from_meaning(meaning)
            
            # Create standardized quote entry
            parsed_quote = {
                'id': quote_id,
                'quote': quote_text.strip(),
                'author': author.strip(),
                'field': field.strip(),
                'meaning': meaning.strip(),
                'era': metadata['era'],
                'tradition': metadata['tradition'],
                'topics': topics,
                'word_count': len(quote_text.split()),
                'source': f"corpus_{file_path.stem}"
            }
            
            # Track for duplicates
            self.seen_quotes.add(quote_hash)
            self.seen_combinations.add(combination)
            
            # Update statistics
            self.stats['field_distribution'][field] += 1
            
            parsed_quotes.append(parsed_quote)
        
        logger.info(f"   Extracted {len(parsed_quotes)} unique quotes from {len(quotes)} total")
        return parsed_quotes
    
    def parse_all_files(self) -> List[Dict]:
        """Parse all quote files and return deduplicated corpus"""
        logger.info("🔍 Starting quote corpus parsing with aggressive deduplication...")
        
        all_quotes = []
        quote_files = sorted(self.data_dir.glob("q*.json"))
        
        logger.info(f"📊 Found {len(quote_files)} quote files to process")
        
        for file_path in quote_files:
            try:
                quotes = self.parse_file(file_path)
                all_quotes.extend(quotes)
            except Exception as e:
                logger.error(f"❌ Error parsing {file_path}: {e}")
                continue
        
        # Final statistics
        self.stats['final_count'] = len(all_quotes)
        self.stats['authors_count'] = len(set(q['author'] for q in all_quotes))
        
        return all_quotes
    
    def save_corpus(self, quotes: List[Dict], output_path: str = "enhanced_philosophical_quotes.jsonl"):
        """Save deduplicated corpus to JSONL file"""
        output_file = Path(output_path)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for quote in quotes:
                f.write(json.dumps(quote, ensure_ascii=False) + '\n')
        
        logger.info(f"💾 Saved {len(quotes)} quotes to {output_file}")
    
    def print_statistics(self):
        """Print parsing and deduplication statistics"""
        print("\n📊 QUOTE CORPUS PARSING RESULTS")
        print("=" * 50)
        print(f"📚 Total quotes processed: {self.stats['total_processed']:,}")
        print(f"🚫 Filtered by field: {self.stats['field_filtered']:,}")
        print(f"🔍 Exact duplicates removed: {self.stats['exact_duplicates']:,}")
        print(f"📝 Fuzzy duplicates removed: {self.stats['fuzzy_duplicates']:,}")
        print(f"✅ Final unique quotes: {self.stats['final_count']:,}")
        print(f"👥 Unique authors: {self.stats['authors_count']:,}")
        
        print(f"\n📈 TOP AUTHOR FIELDS:")
        sorted_fields = sorted(self.stats['field_distribution'].items(), 
                              key=lambda x: x[1], reverse=True)
        for field, count in sorted_fields[:15]:
            print(f"   {field}: {count}")
        
        # Deduplication efficiency
        if self.stats['total_processed'] > 0:
            efficiency = (self.stats['exact_duplicates'] + self.stats['fuzzy_duplicates']) / self.stats['total_processed']
            print(f"\n🎯 Deduplication efficiency: {efficiency:.1%} duplicates removed")


def main():
    """Parse quote corpus with aggressive duplicate elimination"""
    print("🧠 Quote Corpus Parser with Aggressive Deduplication")
    print("=" * 60)
    
    parser = QuoteCorpusParser()
    
    # Parse all files
    quotes = parser.parse_all_files()
    
    # Save results
    parser.save_corpus(quotes, "enhanced_philosophical_quotes.jsonl")
    
    # Print statistics
    parser.print_statistics()
    
    print(f"\n✅ Quote corpus parsing complete!")
    print(f"📚 Enhanced corpus ready for knowledge graph creation")
    
    return quotes


if __name__ == "__main__":
    corpus = main()