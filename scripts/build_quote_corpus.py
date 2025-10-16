#!/usr/bin/env python3
"""Build philosophical quotes corpus from curated data"""

import json
import re
from pathlib import Path
from typing import List, Dict


def create_quote_entry(
    quote_text: str,
    author: str,
    source: str,
    era: str,
    tradition: str,
    topics: List[str],
    polarity: str,
    tone: str,
    index: int
) -> Dict:
    """Create a standardized quote entry"""
    
    # Clean quote text
    clean_quote = quote_text.strip().strip('"').strip("'")
    word_count = len(clean_quote.split())
    
    # Validate length
    if word_count > 25:
        raise ValueError(f"Quote too long ({word_count} words): {clean_quote[:50]}...")
    
    # Generate ID
    author_slug = author.lower().replace(' ', '_').replace('.', '').replace('-', '_')
    source_slug = re.sub(r'[^a-z0-9]', '_', source.lower())
    quote_id = f"{author_slug}_{source_slug}_{index:02d}"
    
    return {
        'id': quote_id,
        'quote': clean_quote,
        'author': author,
        'source': source,
        'era': era,
        'tradition': tradition,
        'topics': topics,
        'polarity': polarity,
        'tone': tone,
        'word_count': word_count
    }


def build_starter_corpus():
    """Build initial philosophical quotes corpus for testing and demonstration"""
    
    print("Building Philosophical Quotes Corpus...")
    print("=" * 60)
    
    quotes = []
    
    # Ancient Western Philosophers
    ancient_western = [
        # Socrates/Plato
        ("The unexamined life is not worth living.", "Socrates", "Apology", 
         ["self-knowledge", "virtue", "philosophy", "life"], "affirmative", "contemplative"),
        ("The Good is beyond being in dignity and power.", "Plato", "Republic", 
         ["truth", "good", "knowledge", "metaphysics"], "affirmative", "mystical"),
        ("The cave allegory reveals our journey from shadows to light.", "Plato", "Republic", 
         ["truth", "knowledge", "education", "reality"], "affirmative", "metaphorical"),
        
        # Aristotle
        ("We are what we repeatedly do. Excellence is not an act, but a habit.", "Aristotle", "Nicomachean Ethics", 
         ["virtue", "excellence", "character", "habit"], "affirmative", "analytical"),
        ("The whole is greater than the sum of its parts.", "Aristotle", "Metaphysics", 
         ["unity", "wholeness", "emergence", "structure"], "affirmative", "analytical"),
        
        # Stoics
        ("You have power over your mind, not outside events.", "Marcus Aurelius", "Meditations", 
         ["control", "mind", "freedom", "stoicism"], "affirmative", "contemplative"),
        ("It's not what happens to you, but how you react that matters.", "Epictetus", "Enchiridion", 
         ["response", "choice", "wisdom", "control"], "affirmative", "practical"),
        
        # Heraclitus
        ("No man ever steps in the same river twice.", "Heraclitus", "Fragments", 
         ["change", "time", "identity", "flux"], "paradoxical", "poetic"),
    ]
    
    # Ancient Eastern Philosophers
    ancient_eastern = [
        # Laozi
        ("The way that can be spoken of is not the constant way.", "Laozi", "Tao Te Ching", 
         ["truth", "ineffable", "tao", "mystery"], "paradoxical", "mystical"),
        ("A journey of a thousand miles begins with a single step.", "Laozi", "Tao Te Ching", 
         ["action", "beginning", "progress", "journey"], "affirmative", "practical"),
        
        # Confucius
        ("I know that I know nothing.", "Confucius", "Analects", 
         ["humility", "knowledge", "wisdom", "learning"], "cautionary", "contemplative"),
        ("The man who moves a mountain begins by carrying away small stones.", "Confucius", "Analects", 
         ["persistence", "action", "gradual", "achievement"], "affirmative", "practical"),
        
        # Buddha
        ("All suffering comes from attachment.", "Buddha", "Four Noble Truths", 
         ["suffering", "attachment", "liberation", "desire"], "cautionary", "contemplative"),
        ("The mind is everything. What you think you become.", "Buddha", "Dhammapada", 
         ["mind", "thought", "transformation", "consciousness"], "affirmative", "contemplative"),
        
        # Zhuangzi
        ("The perfect man uses his mind like a mirror.", "Zhuangzi", "Zhuangzi", 
         ["mind", "clarity", "reflection", "perfection"], "affirmative", "poetic"),
    ]
    
    # Modern Western Philosophers  
    modern_western = [
        # Descartes
        ("I think, therefore I am.", "René Descartes", "Meditations", 
         ["consciousness", "existence", "certainty", "self"], "affirmative", "analytical"),
        ("Doubt is the origin of wisdom.", "René Descartes", "Principles of Philosophy", 
         ["doubt", "wisdom", "knowledge", "method"], "affirmative", "analytical"),
        
        # Spinoza
        ("The free man thinks least of all of death.", "Baruch Spinoza", "Ethics", 
         ["freedom", "death", "life", "wisdom"], "affirmative", "contemplative"),
        ("Peace is not the absence of war but a virtue born of strength.", "Baruch Spinoza", "Ethics", 
         ["peace", "virtue", "strength", "conflict"], "affirmative", "analytical"),
        
        # Kant
        ("Two things fill the mind with ever new and increasing admiration: the starry heavens above me and the moral law within me.", "Immanuel Kant", "Critique of Practical Reason", 
         ["ethics", "awe", "law", "cosmos", "duty"], "affirmative", "reverent"),
        ("Act only according to maxims you could will to be universal laws.", "Immanuel Kant", "Groundwork for Metaphysics", 
         ["ethics", "duty", "universal", "action"], "affirmative", "analytical"),
        
        # Hegel
        ("The owl of Minerva flies only at dusk.", "Georg Wilhelm Friedrich Hegel", "Philosophy of Right", 
         ["wisdom", "understanding", "time", "knowledge"], "metaphorical", "poetic"),
        ("Nothing great in the world has been accomplished without passion.", "Georg Wilhelm Friedrich Hegel", "Philosophy of History", 
         ["passion", "greatness", "achievement", "emotion"], "affirmative", "inspiring"),
        
        # Nietzsche
        ("He who fights with monsters should see to it that he himself does not become a monster.", "Friedrich Nietzsche", "Beyond Good and Evil", 
         ["ethics", "virtue", "struggle", "self", "danger"], "cautionary", "warning"),
        ("What does not kill me makes me stronger.", "Friedrich Nietzsche", "Twilight of the Idols", 
         ["strength", "adversity", "growth", "resilience"], "affirmative", "defiant"),
        ("God is dead, and we have killed him.", "Friedrich Nietzsche", "The Gay Science", 
         ["god", "death", "modernity", "responsibility"], "paradoxical", "shocking"),
        
        # Kierkegaard
        ("Life can only be understood backwards but must be lived forwards.", "Søren Kierkegaard", "Journals", 
         ["life", "understanding", "time", "existence"], "paradoxical", "contemplative"),
        ("The most painful state of being is remembering the future.", "Søren Kierkegaard", "Either/Or", 
         ["time", "memory", "future", "pain"], "paradoxical", "melancholic"),
    ]
    
    # Contemporary Western Philosophers
    contemporary_western = [
        # Existentialists
        ("Man is condemned to be free.", "Jean-Paul Sartre", "Existentialism is a Humanism", 
         ["freedom", "responsibility", "existence", "choice"], "paradoxical", "defiant"),
        ("Hell is other people.", "Jean-Paul Sartre", "No Exit", 
         ["others", "hell", "existence", "relations"], "paradoxical", "dark"),
        ("The absurd is the confrontation between human need and the unreasonable silence of the world.", "Albert Camus", "The Myth of Sisyphus", 
         ["absurd", "meaning", "world", "silence"], "paradoxical", "contemplative"),
        ("There is only one really serious philosophical problem: suicide.", "Albert Camus", "The Myth of Sisyphus", 
         ["suicide", "philosophy", "meaning", "life"], "cautionary", "stark"),
        
        # Simone Weil
        ("Attention is the rarest and purest form of generosity.", "Simone Weil", "Gravity and Grace", 
         ["attention", "virtue", "care", "ethics"], "affirmative", "contemplative"),
        ("We must prefer real hell to an imaginary paradise.", "Simone Weil", "Gravity and Grace", 
         ["truth", "reality", "honesty", "preference"], "cautionary", "stark"),
        
        # Hannah Arendt
        ("The sad truth is that most evil is done by people who never make up their minds to be good or evil.", "Hannah Arendt", "The Life of the Mind", 
         ["evil", "choice", "responsibility", "banality"], "cautionary", "analytical"),
        ("Power corresponds to the human ability not just to act but to act in concert.", "Hannah Arendt", "The Human Condition", 
         ["power", "action", "plurality", "cooperation"], "affirmative", "analytical"),
        
        # Wittgenstein
        ("The limits of my language mean the limits of my world.", "Ludwig Wittgenstein", "Tractus Logico-Philosophicus", 
         ["language", "world", "limits", "meaning"], "analytical", "contemplative"),
        ("Whereof one cannot speak, thereof one must be silent.", "Ludwig Wittgenstein", "Tractus Logico-Philosophicus", 
         ["silence", "speech", "limits", "mystery"], "paradoxical", "mystical"),
        
        # Recent thinkers
        ("We are not thinking machines, we are feeling machines that think.", "Antonio Damasio", "Descartes' Error", 
         ["emotion", "thought", "mind", "consciousness"], "affirmative", "scientific"),
        ("The self is not something ready-made, but something in continuous formation.", "John Dewey", "Experience and Nature", 
         ["self", "formation", "process", "identity"], "affirmative", "pragmatic"),
    ]
    
    # Build corpus with proper indexing
    era_groups = [
        ("ancient", "western", ancient_western),
        ("ancient", "eastern", ancient_eastern),
        ("modern", "western", modern_western),
        ("contemporary", "western", contemporary_western)
    ]
    
    for era, tradition, quote_list in era_groups:
        for i, (quote_text, author, source, topics, polarity, tone) in enumerate(quote_list, 1):
            try:
                quote_entry = create_quote_entry(
                    quote_text=quote_text,
                    author=author,
                    source=source,
                    era=era,
                    tradition=tradition,
                    topics=topics,
                    polarity=polarity,
                    tone=tone,
                    index=i
                )
                quotes.append(quote_entry)
            except ValueError as e:
                print(f"⚠️ Skipping quote: {e}")
    
    # Save to JSONL
    output_path = Path("data/philosophical_quotes.jsonl")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        for quote in quotes:
            f.write(json.dumps(quote) + '\n')
    
    print(f"✅ Saved {len(quotes)} quotes to {output_path}")
    
    # Distribution analysis
    era_counts = {}
    tradition_counts = {}
    author_counts = {}
    
    for quote in quotes:
        era_counts[quote['era']] = era_counts.get(quote['era'], 0) + 1
        tradition_counts[quote['tradition']] = tradition_counts.get(quote['tradition'], 0) + 1
        author_counts[quote['author']] = author_counts.get(quote['author'], 0) + 1
    
    print(f"\n📊 Distribution:")
    print(f"  Total quotes: {len(quotes)}")
    print(f"  By era: {era_counts}")
    print(f"  By tradition: {tradition_counts}")
    print(f"  Unique authors: {len(author_counts)}")
    print(f"  Average quotes per author: {len(quotes) / len(author_counts):.1f}")
    
    # Show sample quotes
    print(f"\n📚 Sample quotes:")
    for i, quote in enumerate(quotes[:3]):
        print(f"  {i+1}. \"{quote['quote']}\" — {quote['author']}")
        print(f"     Topics: {', '.join(quote['topics'][:3])}")
        print(f"     Era: {quote['era']}, Tradition: {quote['tradition']}")
    
    return quotes


if __name__ == "__main__":
    corpus = build_starter_corpus()
    print(f"\n🎉 Philosophical quotes corpus ready with {len(corpus)} entries!")