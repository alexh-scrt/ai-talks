#!/usr/bin/env python3
"""
BrainyQuote Web Scraper for Philosophical Quotes

Scrapes philosophical quotes from BrainyQuote.com to expand the corpus.
Focuses on philosophy categories and famous philosophers.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Set
import hashlib

class BrainyQuoteScraper:
    """Scrapes philosophical quotes from BrainyQuote.com"""
    
    def __init__(self):
        self.base_url = "https://www.brainyquote.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Load existing quotes to avoid duplicates
        self.existing_quotes = self._load_existing_quotes()
        self.existing_quote_texts = {q['quote'].lower().strip() for q in self.existing_quotes}
        
        # Philosopher categories to scrape
        self.philosopher_searches = [
            'aristotle', 'plato', 'socrates', 'confucius', 'buddha', 'lao-tzu',
            'descartes', 'kant', 'nietzsche', 'hegel', 'spinoza', 'locke',
            'hume', 'rousseau', 'voltaire', 'mill', 'bentham', 'schopenhauer',
            'kierkegaard', 'sartre', 'camus', 'wittgenstein', 'russell',
            'gandhi', 'dalai-lama', 'rumi', 'marcus-aurelius', 'seneca',
            'epictetus', 'epicurus', 'diogenes', 'heraclitus', 'parmenides'
        ]
        
        self.topic_searches = [
            'philosophy', 'wisdom', 'truth', 'knowledge', 'existence',
            'consciousness', 'ethics', 'morality', 'virtue', 'justice',
            'freedom', 'reality', 'meaning', 'purpose', 'enlightenment'
        ]
    
    def _load_existing_quotes(self) -> List[Dict]:
        """Load existing quotes to avoid duplicates"""
        corpus_path = Path("data/philosophical_quotes.jsonl")
        quotes = []
        
        if corpus_path.exists():
            with open(corpus_path, 'r', encoding='utf-8') as f:
                for line in f:
                    quotes.append(json.loads(line))
        
        return quotes
    
    def scrape_author_quotes(self, author_slug: str, max_pages: int = 3) -> List[Dict]:
        """Scrape quotes from an author's page"""
        
        quotes = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/authors/{author_slug}?page={page}"
            
            try:
                print(f"   Scraping {author_slug} page {page}...")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find quote containers
                quote_containers = soup.find_all('div', class_='grid-item')
                
                if not quote_containers:
                    break  # No more quotes
                
                for container in quote_containers:
                    quote_data = self._extract_quote_from_container(container, author_slug)
                    if quote_data and self._is_philosophical_quote(quote_data['quote']):
                        quotes.append(quote_data)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"   Error scraping {author_slug} page {page}: {e}")
                break
        
        return quotes
    
    def scrape_topic_quotes(self, topic: str, max_pages: int = 2) -> List[Dict]:
        """Scrape quotes from a topic page"""
        
        quotes = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/topics/{topic}?page={page}"
            
            try:
                print(f"   Scraping {topic} topic page {page}...")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find quote containers
                quote_containers = soup.find_all('div', class_='grid-item')
                
                if not quote_containers:
                    break
                
                for container in quote_containers:
                    quote_data = self._extract_quote_from_container(container, topic)
                    if quote_data and self._is_philosophical_quote(quote_data['quote']):
                        quotes.append(quote_data)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"   Error scraping {topic} topic page {page}: {e}")
                break
        
        return quotes
    
    def _extract_quote_from_container(self, container, source_context: str) -> Dict:
        """Extract quote data from a quote container"""
        
        try:
            # Find quote text
            quote_element = container.find('a', title=True)
            if not quote_element:
                return None
            
            quote_text = quote_element.get('title', '').strip()
            if not quote_text:
                return None
            
            # Clean quote text
            quote_text = re.sub(r'^"|"$', '', quote_text)  # Remove surrounding quotes
            quote_text = re.sub(r'\s+', ' ', quote_text).strip()
            
            # Check for duplicates
            if quote_text.lower().strip() in self.existing_quote_texts:
                return None
            
            # Find author
            author_element = container.find('a', href=re.compile(r'/authors/'))
            author = author_element.text.strip() if author_element else "Unknown"
            
            # Generate quote ID
            author_slug = re.sub(r'[^a-zA-Z0-9]', '_', author.lower())
            quote_id = f"brainy_{author_slug}_{len(self.existing_quotes) + 1:03d}"
            
            # Determine era and tradition based on author
            era, tradition = self._classify_author(author)
            
            # Extract topics
            topics = self._extract_topics_from_text(quote_text)
            
            quote_data = {
                "id": quote_id,
                "quote": quote_text,
                "author": author,
                "source": "BrainyQuote",
                "era": era,
                "tradition": tradition,
                "topics": topics,
                "polarity": self._determine_polarity(quote_text),
                "tone": self._determine_tone(quote_text),
                "word_count": len(quote_text.split())
            }
            
            return quote_data
            
        except Exception as e:
            print(f"   Error extracting quote: {e}")
            return None
    
    def _is_philosophical_quote(self, text: str) -> bool:
        """Check if a quote is philosophical in nature"""
        
        if len(text) < 15 or len(text) > 300:
            return False
        
        # Philosophical keywords
        philosophical_terms = [
            'truth', 'wisdom', 'knowledge', 'reality', 'existence', 'being',
            'consciousness', 'mind', 'soul', 'spirit', 'philosophy', 'think',
            'reason', 'logic', 'understand', 'meaning', 'purpose', 'virtue',
            'good', 'evil', 'right', 'wrong', 'justice', 'freedom', 'liberty',
            'nature', 'universe', 'god', 'divine', 'eternal', 'life', 'death',
            'time', 'change', 'experience', 'perception', 'belief', 'faith',
            'doubt', 'certainty', 'question', 'answer', 'self', 'identity'
        ]
        
        text_lower = text.lower()
        philosophical_count = sum(1 for term in philosophical_terms if term in text_lower)
        
        return philosophical_count >= 2
    
    def _classify_author(self, author: str) -> tuple:
        """Classify author by era and tradition"""
        
        # Ancient philosophers
        ancient_western = [
            'aristotle', 'plato', 'socrates', 'marcus aurelius', 'seneca',
            'epictetus', 'epicurus', 'diogenes', 'heraclitus', 'parmenides',
            'democritus', 'pythagoras', 'thales', 'anaximander', 'cicero'
        ]
        
        ancient_eastern = [
            'confucius', 'buddha', 'lao tzu', 'mencius', 'zhuangzi',
            'nagarjuna', 'shankara', 'patanjali'
        ]
        
        # Modern philosophers
        modern_western = [
            'descartes', 'kant', 'hegel', 'spinoza', 'locke', 'hume',
            'rousseau', 'voltaire', 'mill', 'bentham', 'schopenhauer',
            'kierkegaard', 'fichte', 'schelling'
        ]
        
        # Contemporary philosophers
        contemporary_western = [
            'nietzsche', 'sartre', 'camus', 'wittgenstein', 'russell',
            'heidegger', 'husserl', 'dewey', 'james', 'peirce'
        ]
        
        contemporary_eastern = [
            'gandhi', 'dalai lama', 'krishnamurti', 'suzuki', 'nishida'
        ]
        
        # Other traditions
        other_traditions = [
            'rumi', 'hafez', 'ibn sina', 'al-ghazali', 'maimonides',
            'aquinas', 'augustine', 'mandela'
        ]
        
        author_lower = author.lower()
        
        if any(name in author_lower for name in ancient_western):
            return 'ancient', 'western'
        elif any(name in author_lower for name in ancient_eastern):
            return 'ancient', 'eastern'
        elif any(name in author_lower for name in modern_western):
            return 'modern', 'western'
        elif any(name in author_lower for name in contemporary_western):
            return 'contemporary', 'western'
        elif any(name in author_lower for name in contemporary_eastern):
            return 'contemporary', 'eastern'
        elif any(name in author_lower for name in other_traditions):
            return 'ancient', 'other'
        else:
            return 'contemporary', 'western'  # Default
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract philosophical topics from quote text"""
        
        topic_keywords = {
            'knowledge': ['know', 'knowledge', 'learn', 'understand', 'wisdom'],
            'truth': ['truth', 'true', 'reality', 'real', 'fact'],
            'existence': ['exist', 'being', 'life', 'live', 'death'],
            'consciousness': ['mind', 'consciousness', 'thought', 'think', 'aware'],
            'virtue': ['virtue', 'good', 'goodness', 'right', 'moral'],
            'freedom': ['free', 'freedom', 'liberty', 'choice'],
            'love': ['love', 'compassion', 'kindness', 'care'],
            'time': ['time', 'moment', 'present', 'future', 'past'],
            'change': ['change', 'transform', 'become', 'grow'],
            'happiness': ['happy', 'happiness', 'joy', 'pleasure'],
            'suffering': ['suffer', 'pain', 'sadness', 'grief'],
            'courage': ['courage', 'brave', 'strength', 'bold'],
            'wisdom': ['wise', 'wisdom', 'sage', 'prudent'],
            'justice': ['justice', 'fair', 'equal', 'right'],
            'peace': ['peace', 'calm', 'serenity', 'tranquil']
        }
        
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:4]  # Limit to 4 topics
    
    def _determine_polarity(self, text: str) -> str:
        """Determine quote polarity"""
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['not', 'never', 'no ', 'cannot']):
            return 'negative'
        elif any(word in text_lower for word in ['must', 'should', 'ought']):
            return 'prescriptive'
        elif '?' in text:
            return 'questioning'
        else:
            return 'affirmative'
    
    def _determine_tone(self, text: str) -> str:
        """Determine quote tone"""
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['inspire', 'hope', 'courage']):
            return 'inspirational'
        elif any(word in text_lower for word in ['think', 'consider', 'reflect']):
            return 'contemplative'
        elif any(word in text_lower for word in ['wise', 'wisdom', 'prudent']):
            return 'wise'
        else:
            return 'philosophical'

def main():
    """Scrape philosophical quotes from BrainyQuote"""
    
    print("🌐 BrainyQuote Philosophical Quotes Scraper")
    print("Expanding corpus with high-quality quotes from BrainyQuote.com")
    print("=" * 60)
    
    scraper = BrainyQuoteScraper()
    
    current_count = len(scraper.existing_quotes)
    print(f"📊 Current corpus: {current_count} quotes")
    
    all_new_quotes = []
    
    # Scrape philosopher pages
    print(f"\n🧠 Scraping {len(scraper.philosopher_searches)} philosopher pages...")
    for i, philosopher in enumerate(scraper.philosopher_searches):
        print(f"📚 Scraping {philosopher} ({i+1}/{len(scraper.philosopher_searches)})...")
        
        try:
            quotes = scraper.scrape_author_quotes(philosopher, max_pages=2)
            unique_quotes = []
            
            for quote in quotes:
                quote_text = quote['quote'].lower().strip()
                if quote_text not in scraper.existing_quote_texts:
                    unique_quotes.append(quote)
                    scraper.existing_quote_texts.add(quote_text)
            
            print(f"   Found {len(unique_quotes)} new unique quotes")
            all_new_quotes.extend(unique_quotes)
            
        except Exception as e:
            print(f"   Error scraping {philosopher}: {e}")
        
        # Rate limiting
        time.sleep(2)
    
    # Scrape topic pages
    print(f"\n📖 Scraping {len(scraper.topic_searches)} topic pages...")
    for i, topic in enumerate(scraper.topic_searches):
        print(f"🏷️  Scraping {topic} ({i+1}/{len(scraper.topic_searches)})...")
        
        try:
            quotes = scraper.scrape_topic_quotes(topic, max_pages=1)
            unique_quotes = []
            
            for quote in quotes:
                quote_text = quote['quote'].lower().strip()
                if quote_text not in scraper.existing_quote_texts:
                    unique_quotes.append(quote)
                    scraper.existing_quote_texts.add(quote_text)
            
            print(f"   Found {len(unique_quotes)} new unique quotes")
            all_new_quotes.extend(unique_quotes)
            
        except Exception as e:
            print(f"   Error scraping {topic}: {e}")
        
        # Rate limiting
        time.sleep(2)
    
    # Combine and save
    final_corpus = scraper.existing_quotes + all_new_quotes
    
    # Remove duplicates by text
    seen_texts = set()
    deduplicated_corpus = []
    
    for quote in final_corpus:
        quote_text = quote['quote'].lower().strip()
        if quote_text not in seen_texts:
            deduplicated_corpus.append(quote)
            seen_texts.add(quote_text)
    
    # Save enhanced corpus
    output_path = Path("data/philosophical_quotes.jsonl")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for quote in deduplicated_corpus:
            f.write(json.dumps(quote, ensure_ascii=False) + '\n')
    
    # Analyze results
    era_counts = Counter(q['era'] for q in deduplicated_corpus)
    tradition_counts = Counter(q['tradition'] for q in deduplicated_corpus)
    
    print(f"\n📊 Scraping Results:")
    print(f"New quotes scraped: {len(all_new_quotes)}")
    print(f"Final corpus size: {len(deduplicated_corpus)}")
    print(f"Net quotes added: {len(deduplicated_corpus) - current_count}")
    
    print(f"\n📈 Final Distribution:")
    print(f"Era: {dict(era_counts)}")
    print(f"Tradition: {dict(tradition_counts)}")
    
    print(f"\n✅ BrainyQuote scraping complete!")
    print(f"📚 Enhanced corpus saved to: {output_path}")
    print(f"🌟 Corpus ready for semantic search testing")
    
    if len(deduplicated_corpus) >= 1500:
        print(f"🎉 MILESTONE: Corpus now contains {len(deduplicated_corpus)} quotes!")
        print(f"🚀 Excellent foundation for production semantic search")
    
    return deduplicated_corpus

if __name__ == "__main__":
    corpus = main()