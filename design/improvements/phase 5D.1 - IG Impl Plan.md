
# Philosophical Gems Implementation Plan: Wisdom Anchors for Intellectual Gravitas

## 🎯 Overview

This system enriches discussions with **curated philosophical quotes** that are semantically relevant, voice-adapted to each speaker, and strategically placed to enhance intellectual depth and memorability.

### Success Criteria
✅ Curated corpus of 500-800 philosophical quotes  
✅ Semantic retrieval based on discussion topics  
✅ Voice adaptation using existing RAG style transfer  
✅ Strategic placement (opening/mid/closing)  
✅ Diversity tracking (authors, eras, traditions)  
✅ Natural integration without disruption  
✅ Measurable relevance and impact  

---

## Phase 1: Quote Corpus Creation

### 1.1 Design Quote Schema

**File**: `data/philosophical_quotes.jsonl` (new file)

```jsonl
{"id": "plato_republic_509d", "quote": "The Good is beyond being in dignity and power.", "author": "Plato", "source": "Republic 509d", "era": "ancient", "tradition": "western", "topics": ["truth", "good", "knowledge", "metaphysics"], "polarity": "affirmative", "tone": "contemplative", "word_count": 9}
{"id": "kant_critique_practical_01", "quote": "Two things fill the mind with ever new and increasing admiration: the starry heavens above me and the moral law within me.", "author": "Immanuel Kant", "source": "Critique of Practical Reason", "era": "modern", "tradition": "western", "topics": ["ethics", "awe", "law", "cosmos", "duty"], "polarity": "affirmative", "tone": "reverent", "word_count": 23}
{"id": "nietzsche_bgae_146", "quote": "He who fights with monsters should see to it that he himself does not become a monster.", "author": "Friedrich Nietzsche", "source": "Beyond Good and Evil §146", "era": "modern", "tradition": "western", "topics": ["ethics", "virtue", "struggle", "self", "danger"], "polarity": "cautionary", "tone": "warning", "word_count": 17}
{"id": "simone_weil_gravity_01", "quote": "Attention is the rarest and purest form of generosity.", "author": "Simone Weil", "source": "Gravity and Grace", "era": "contemporary", "tradition": "western", "topics": ["attention", "virtue", "care", "ethics"], "polarity": "affirmative", "tone": "contemplative", "word_count": 10}
{"id": "laozi_daodejing_01", "quote": "The Tao that can be told is not the eternal Tao.", "author": "Laozi", "source": "Tao Te Ching §1", "era": "ancient", "tradition": "eastern", "topics": ["truth", "language", "ineffable", "mystery"], "polarity": "paradoxical", "tone": "mystical", "word_count": 11}
{"id": "arendt_human_condition_01", "quote": "Action, the only activity that goes on directly between men without the intermediary of things or matter, corresponds to the human condition of plurality.", "author": "Hannah Arendt", "source": "The Human Condition", "era": "contemporary", "tradition": "western", "topics": ["action", "politics", "humanity", "plurality", "freedom"], "polarity": "affirmative", "tone": "analytical", "word_count": 23}
```

**Schema Fields:**
- `id`: Unique identifier (author_source_index)
- `quote`: The actual quote text (≤25 words)
- `author`: Philosopher name
- `source`: Book/work reference
- `era`: ancient | modern | contemporary
- `tradition`: western | eastern | african | indigenous
- `topics`: Array of thematic tags
- `polarity`: affirmative | skeptical | paradoxical | cautionary
- `tone`: contemplative | analytical | warning | reverent | mystical | defiant
- `word_count`: Length in words

---

### 1.2 Create Quote Corpus Builder

**File**: `scripts/build_quote_corpus.py` (new file)

```python
#!/usr/bin/env python3
"""Build philosophical quotes corpus from source files"""

import json
import re
from pathlib import Path
from typing import List, Dict

# Target: 500-800 quotes balanced across eras and traditions
QUOTE_SOURCES = {
    'ancient_western': [
        ('Plato', 'Republic', 50),
        ('Aristotle', 'Nicomachean Ethics', 40),
        ('Epictetus', 'Enchiridion', 30),
        ('Marcus Aurelius', 'Meditations', 40),
    ],
    'ancient_eastern': [
        ('Laozi', 'Tao Te Ching', 40),
        ('Confucius', 'Analects', 35),
        ('Zhuangzi', 'Zhuangzi', 30),
        ('Buddha', 'Dhammapada', 35),
    ],
    'modern': [
        ('Descartes', 'Meditations', 30),
        ('Spinoza', 'Ethics', 35),
        ('Kant', 'Critique of Pure Reason', 40),
        ('Hegel', 'Phenomenology of Spirit', 30),
        ('Nietzsche', 'Beyond Good and Evil', 45),
        ('Kierkegaard', 'Fear and Trembling', 25),
    ],
    'contemporary': [
        ('Simone Weil', 'Gravity and Grace', 40),
        ('Hannah Arendt', 'The Human Condition', 35),
        ('Jean-Paul Sartre', 'Being and Nothingness', 30),
        ('Albert Camus', 'The Myth of Sisyphus', 25),
        ('Michel Foucault', 'Discipline and Punish', 25),
        ('Judith Butler', 'Gender Trouble', 20),
    ]
}


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
    author_slug = author.lower().replace(' ', '_').replace('.', '')
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


def build_corpus():
    """Build the philosophical quotes corpus"""
    
    print("Building Philosophical Quotes Corpus...")
    print("=" * 60)
    
    quotes = []
    
    # This is a starter template - you would populate with actual quotes
    # For demonstration, here are some examples:
    
    sample_quotes = [
        create_quote_entry(
            "The unexamined life is not worth living.",
            "Socrates", "Apology", "ancient", "western",
            ["self-knowledge", "virtue", "philosophy", "life"],
            "affirmative", "contemplative", 1
        ),
        create_quote_entry(
            "I think, therefore I am.",
            "René Descartes", "Meditations", "modern", "western",
            ["consciousness", "existence", "certainty", "self"],
            "affirmative", "analytical", 1
        ),
        create_quote_entry(
            "Man is condemned to be free.",
            "Jean-Paul Sartre", "Existentialism is a Humanism", "contemporary", "western",
            ["freedom", "responsibility", "existence", "choice"],
            "paradoxical", "defiant", 1
        ),
        create_quote_entry(
            "The way that can be spoken of is not the constant way.",
            "Laozi", "Tao Te Ching", "ancient", "eastern",
            ["truth", "ineffable", "tao", "mystery"],
            "paradoxical", "mystical", 1
        ),
    ]
    
    quotes.extend(sample_quotes)
    
    # Save to JSONL
    output_path = Path("data/philosophical_quotes.jsonl")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        for quote in quotes:
            f.write(json.dumps(quote) + '\n')
    
    print(f"✅ Saved {len(quotes)} quotes to {output_path}")
    print(f"\nDistribution:")
    print(f"  Total: {len(quotes)}")
    # Add distribution stats here
    
    return quotes


if __name__ == "__main__":
    corpus = build_corpus()
```

---

## Phase 2: Quote Retrieval System

### 2.1 Create Quote Retriever

**File**: `src/retrieval/quote_retriever.py` (new file)

```python
# src/retrieval/quote_retriever.py

import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Optional, Set
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


class QuoteRetriever:
    """
    Retrieves philosophically relevant quotes using hybrid keyword + semantic search
    """
    
    def __init__(self, corpus_path: str = "data/philosophical_quotes.jsonl"):
        """
        Initialize quote retriever
        
        Args:
            corpus_path: Path to JSONL corpus file
        """
        self.corpus_path = Path(corpus_path)
        self.quotes: List[Dict] = []
        self.quote_index: Dict[str, Dict] = {}  # id -> quote
        
        # Semantic search model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.quote_embeddings: Optional[np.ndarray] = None
        
        # Usage tracking
        self.used_quotes: Set[str] = set()
        self.last_authors: List[str] = []  # Track last N authors
        self.author_usage: Dict[str, int] = {}
        
        # Load corpus
        self._load_corpus()
        logger.info(f"📚 QuoteRetriever initialized with {len(self.quotes)} quotes")
    
    def _load_corpus(self):
        """Load quotes from JSONL file"""
        if not self.corpus_path.exists():
            logger.warning(f"Quote corpus not found: {self.corpus_path}")
            return
        
        with open(self.corpus_path, 'r') as f:
            for line in f:
                quote = json.loads(line.strip())
                self.quotes.append(quote)
                self.quote_index[quote['id']] = quote
        
        # Precompute embeddings for all quotes
        if self.quotes:
            quote_texts = [q['quote'] for q in self.quotes]
            self.quote_embeddings = self.embedding_model.encode(quote_texts)
            logger.info(f"📊 Precomputed embeddings for {len(quote_texts)} quotes")
    
    def retrieve(
        self,
        topics: List[str],
        current_tension: Optional[tuple] = None,
        exclude_authors: Optional[List[str]] = None,
        top_k: int = 3,
        diversity_weight: float = 0.3,
        relevance_threshold: float = 0.65
    ) -> List[Dict]:
        """
        Retrieve relevant quotes using hybrid search
        
        Args:
            topics: List of topic keywords from current discussion
            current_tension: Optional tension pair for targeted retrieval
            exclude_authors: Authors to exclude (avoid repetition)
            top_k: Number of quotes to return
            diversity_weight: Weight for diversity vs pure relevance (0-1)
            relevance_threshold: Minimum semantic similarity score
            
        Returns:
            List of quote dictionaries with relevance scores
        """
        if not self.quotes:
            logger.warning("No quotes available in corpus")
            return []
        
        # Build search query
        query = self._build_query(topics, current_tension)
        logger.debug(f"Quote search query: {query}")
        
        # Step 1: Keyword filtering
        keyword_candidates = self._keyword_filter(topics, current_tension)
        
        # Step 2: Semantic ranking
        ranked_quotes = self._semantic_rank(query, keyword_candidates, relevance_threshold)
        
        # Step 3: Diversity filtering
        diverse_quotes = self._apply_diversity(
            ranked_quotes,
            exclude_authors or self.last_authors[-3:],
            diversity_weight
        )
        
        # Return top K
        selected = diverse_quotes[:top_k]
        
        # Track usage
        for quote in selected:
            self.used_quotes.add(quote['id'])
            author = quote['author']
            self.last_authors.append(author)
            self.author_usage[author] = self.author_usage.get(author, 0) + 1
        
        # Trim last_authors to keep only recent
        if len(self.last_authors) > 10:
            self.last_authors = self.last_authors[-10:]
        
        logger.info(f"📖 Retrieved {len(selected)} quotes (relevance ≥ {relevance_threshold})")
        return selected
    
    def _build_query(self, topics: List[str], tension: Optional[tuple] = None) -> str:
        """Build search query from topics and tension"""
        query_parts = topics.copy()
        
        if tension:
            query_parts.extend(tension)
        
        return " ".join(query_parts)
    
    def _keyword_filter(
        self,
        topics: List[str],
        tension: Optional[tuple] = None
    ) -> List[Dict]:
        """Filter quotes by keyword match in topics"""
        candidates = []
        search_terms = set(t.lower() for t in topics)
        
        if tension:
            search_terms.update(t.lower() for t in tension)
        
        for quote in self.quotes:
            # Check if any search term matches quote topics
            quote_topics = set(t.lower() for t in quote['topics'])
            
            if search_terms & quote_topics:  # Intersection
                candidates.append(quote)
        
        # If too few, return all quotes
        if len(candidates) < 10:
            logger.debug(f"Only {len(candidates)} keyword matches, using full corpus")
            return self.quotes
        
        logger.debug(f"Keyword filter: {len(candidates)} candidates")
        return candidates
    
    def _semantic_rank(
        self,
        query: str,
        candidates: List[Dict],
        threshold: float
    ) -> List[Dict]:
        """Rank candidates by semantic similarity"""
        if not candidates:
            return []
        
        # Get query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Get candidate indices
        candidate_indices = [self.quotes.index(c) for c in candidates]
        candidate_embeddings = self.quote_embeddings[candidate_indices]
        
        # Compute cosine similarities
        similarities = np.dot(candidate_embeddings, query_embedding) / (
            np.linalg.norm(candidate_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Attach scores and filter by threshold
        ranked = []
        for idx, sim in enumerate(similarities):
            if sim >= threshold:
                quote = candidates[idx].copy()
                quote['relevance_score'] = float(sim)
                ranked.append(quote)
        
        # Sort by relevance
        ranked.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.debug(f"Semantic ranking: {len(ranked)} quotes above threshold")
        return ranked
    
    def _apply_diversity(
        self,
        quotes: List[Dict],
        exclude_authors: List[str],
        diversity_weight: float
    ) -> List[Dict]:
        """Apply diversity constraints to quote selection"""
        if not quotes:
            return []
        
        # Filter out recently used authors
        filtered = [
            q for q in quotes
            if q['author'] not in exclude_authors
        ]
        
        # If too few remain, allow some repetition
        if len(filtered) < 3:
            logger.debug("Relaxing author diversity constraint")
            filtered = quotes
        
        # Boost quotes from underused authors
        for quote in filtered:
            author = quote['author']
            usage_count = self.author_usage.get(author, 0)
            
            # Diversity bonus (inverse of usage frequency)
            diversity_bonus = 1.0 / (1.0 + usage_count)
            
            # Combine relevance and diversity
            quote['final_score'] = (
                quote['relevance_score'] * (1 - diversity_weight) +
                diversity_bonus * diversity_weight
            )
        
        # Re-sort by final score
        filtered.sort(key=lambda x: x['final_score'], reverse=True)
        
        return filtered
    
    def get_statistics(self) -> Dict:
        """Get usage statistics"""
        return {
            'total_quotes': len(self.quotes),
            'quotes_used': len(self.used_quotes),
            'unique_authors': len(set(q['author'] for q in self.quotes)),
            'author_distribution': self.author_usage,
            'recent_authors': self.last_authors[-5:]
        }
    
    def reset_session(self):
        """Reset tracking for new discussion session"""
        self.used_quotes.clear()
        self.last_authors.clear()
        self.author_usage.clear()
        logger.info("📚 Quote retriever session reset")
```

---

## Phase 3: Quote Enrichment Agent

### 3.1 Create Quote Enrichment Agent

**File**: `src/agents/quote_enrichment_agent.py` (new file)

```python
# src/agents/quote_enrichment_agent.py

import logging
import random
from typing import Optional, Dict, List, Tuple
from src.agents.base_agent import BaseAgent
from src.retrieval.quote_retriever import QuoteRetriever
from src.states.participant_state import ParticipantState

logger = logging.getLogger(__name__)


QUOTE_ADAPTATION_SYSTEM_PROMPT = """You are a philosophical dialogue writer specializing in voice adaptation.

Your task is to take a philosophical quote and rewrite it in a specific character's voice while:
1. Preserving the core meaning and wisdom
2. Maintaining the original author's attribution
3. Adapting the phrasing to match the speaker's personality and style

The adaptation should feel natural, as if the speaker is invoking the quote but expressing it in their own words.

CRITICAL RULES:
- Keep the essence and meaning intact
- Always attribute to original author
- Match the speaker's personality and rhetorical style
- Make it conversational, not academic
- Aim for approximately the same length
- Do NOT add commentary - just the adapted quote
"""


class QuoteEnrichmentAgent(BaseAgent):
    """
    Enriches discussion with strategically placed philosophical quotes.
    
    Responsibilities:
    1. Retrieve relevant quotes based on discussion context
    2. Adapt quotes to speaker's voice
    3. Determine optimal placement timing
    4. Track diversity and impact
    """
    
    # Placement strategies
    PLACEMENT_MODES = {
        'opening': 6,      # Place every 6-8 turns
        'mid': 8,          # During active discussion
        'closing': 12      # Before major syntheses
    }
    
    def __init__(
        self,
        quote_interval: int = 8,
        enable_voice_adaptation: bool = True,
        session_id: Optional[str] = None
    ):
        """
        Initialize quote enrichment agent
        
        Args:
            quote_interval: Turns between quote placements
            enable_voice_adaptation: Whether to adapt quotes to speaker voice
            session_id: Session identifier
        """
        super().__init__(
            agent_id="quote_enrichment",
            web_search=False,
            model="qwen3:32b",
            session_id=session_id,
            llm_params={"temperature": 0.7}
        )
        
        self.quote_interval = quote_interval
        self.enable_voice_adaptation = enable_voice_adaptation
        self.retriever = QuoteRetriever()
        
        # Tracking
        self.turns_since_last_quote = 0
        self.quotes_used_this_session: List[Dict] = []
        
        logger.info(f"📚 QuoteEnrichmentAgent initialized (interval={quote_interval})")
    
    def should_enrich(self, turn_number: int, phase: str = 'mid') -> bool:
        """
        Determine if current turn should include a quote
        
        Args:
            turn_number: Current turn number
            phase: Discussion phase (opening/mid/closing)
            
        Returns:
            True if quote should be added
        """
        # Don't quote on first turn
        if turn_number == 0:
            return False
        
        # Check interval
        if self.turns_since_last_quote < self.quote_interval:
            self.turns_since_last_quote += 1
            return False
        
        # Reset counter and allow quote
        self.turns_since_last_quote = 0
        return True
    
    async def enrich_response(
        self,
        response: str,
        speaker: ParticipantState,
        discussion_topics: List[str],
        current_tension: Optional[Tuple[str, str]] = None,
        discussion_context: str = ""
    ) -> str:
        """
        Add a philosophical quote to the response
        
        Args:
            response: Original response text
            speaker: The speaking agent
            discussion_topics: Current discussion topics
            current_tension: Optional philosophical tension
            discussion_context: Recent discussion for context
            
        Returns:
            Enhanced response with quote
        """
        logger.info(f"📖 Enriching {speaker.name}'s response with quote")
        
        # Retrieve relevant quotes
        quotes = self.retriever.retrieve(
            topics=discussion_topics,
            current_tension=current_tension,
            exclude_authors=[speaker.name],  # Don't quote themselves
            top_k=3,
            relevance_threshold=0.65
        )
        
        if not quotes:
            logger.warning("No relevant quotes found")
            return response
        
        # Select best quote
        selected_quote = quotes[0]
        logger.info(f"📚 Selected quote from {selected_quote['author']}")
        
        # Adapt to speaker's voice if enabled
        if self.enable_voice_adaptation:
            adapted_quote = await self._adapt_quote_to_voice(
                quote=selected_quote,
                speaker=speaker,
                context=discussion_context
            )
        else:
            adapted_quote = selected_quote['quote']
        
        # Format the enriched response
        enriched = self._format_quote_placement(
            original_response=response,
            quote=adapted_quote,
            author=selected_quote['author'],
            speaker=speaker
        )
        
        # Track usage
        self.quotes_used_this_session.append({
            'quote_id': selected_quote['id'],
            'author': selected_quote['author'],
            'speaker': speaker.name,
            'turn': len(self.quotes_used_this_session),
            'relevance_score': selected_quote.get('relevance_score', 0.0)
        })
        
        return enriched
    
    async def _adapt_quote_to_voice(
        self,
        quote: Dict,
        speaker: ParticipantState,
        context: str
    ) -> str:
        """
        Adapt philosophical quote to speaker's voice
        
        Uses similar voice adaptation logic to RAG style transfer
        """
        prompt = f"""Speaker: {speaker.name}
Personality: {speaker.personality.value}
Expertise: {speaker.expertise}

Original Quote: "{quote['quote']}" — {quote['author']}

Recent Discussion Context:
{context[-300:]}

Adapt this quote to how {speaker.name} would naturally express it in conversation.
Maintain the core wisdom and attribute to {quote['author']}, but phrase it in {speaker.name}'s voice.

Adapted quote:"""
        
        adapted = await self.generate_with_llm(
            prompt=prompt,
            system_prompt=QUOTE_ADAPTATION_SYSTEM_PROMPT
        )
        
        # Clean up response
        adapted = adapted.strip().strip('"').strip("'")
        
        logger.debug(f"Adapted quote: {adapted[:80]}...")
        return adapted
    
    def _format_quote_placement(
        self,
        original_response: str,
        quote: str,
        author: str,
        speaker: ParticipantState
    ) -> str:
        """
        Format how the quote is integrated into the response
        
        Different styles based on personality
        """
        personality = speaker.personality.value
        
        # Template variations by personality
        templates = {
            'analytical': [
                f"{original_response}\n\nAs {author} observed, \"{quote}\" This analytical lens helps us see the structure beneath.",
                f"{original_response}\n\n{author} formalized this insight: \"{quote}\" The principle still holds.",
            ],
            'creative': [
                f"{original_response}\n\n{author} painted it beautifully: \"{quote}\" Can you see the resonance?",
                f"{original_response}\n\nImagine {author}'s words: \"{quote}\" This metaphor illuminates our question.",
            ],
            'skeptical': [
                f"{original_response}\n\n{author} warned us: \"{quote}\" Perhaps we should heed that caution.",
                f"{original_response}\n\nEven {author} recognized the paradox: \"{quote}\" The tension remains.",
            ],
            'collaborative': [
                f"{original_response}\n\n{author} united these ideas when they said, \"{quote}\" Let's build on that foundation together.",
                f"{original_response}\n\nI'm reminded of {author}'s wisdom: \"{quote}\" This connects to what we're exploring.",
            ],
            'assertive': [
                f"{original_response}\n\n{author} was right: \"{quote}\" This principle is decisive.",
                f"{original_response}\n\nConsider {author}'s definitive statement: \"{quote}\" The matter is clear.",
            ],
            'cautious': [
                f"{original_response}\n\n{author} suggested, perhaps wisely, \"{quote}\" We should consider this carefully.",
                f"{original_response}\n\nAs {author} noted, \"{quote}\" This might guide our thinking.",
            ]
        }
        
        # Select template
        template_list = templates.get(personality, templates['analytical'])
        template = random.choice(template_list)
        
        return template
    
    def get_statistics(self) -> Dict:
        """Get enrichment statistics"""
        stats = self.retriever.get_statistics()
        stats['quotes_placed'] = len(self.quotes_used_this_session)
        stats['session_quotes'] = self.quotes_used_this_session
        
        return stats
    
    def reset_session(self):
        """Reset for new discussion session"""
        self.turns_since_last_quote = 0
        self.quotes_used_this_session.clear()
        self.retriever.reset_session()
        logger.info("📚 Quote enrichment session reset")
```

---

## Phase 4: Integration with Orchestrator

### 4.1 Modify Orchestrator

**File**: `src/orchestration/orchestrator.py` (modify)

Add imports:
```python
from src.agents.quote_enrichment_agent import QuoteEnrichmentAgent
```

Add to `__init__`:
```python
def __init__(
    self,
    # ... existing params ...
    enable_quote_enrichment: Optional[bool] = None,
    quote_interval: int = 8,
    enable_quote_voice_adaptation: bool = True
):
    # ... existing init ...
    
    # Quote enrichment
    config = TalksConfig()
    if enable_quote_enrichment is None:
        enable_quote_enrichment = config.get('quotes.enabled', True)
    
    self.enable_quote_enrichment = enable_quote_enrichment
    self.quote_agent = None
    
    if enable_quote_enrichment:
        self.quote_agent = QuoteEnrichmentAgent(
            quote_interval=quote_interval,
            enable_voice_adaptation=enable_quote_voice_adaptation,
            session_id=self.session_id
        )
        logger.info(f"📚 Quote enrichment enabled (interval={quote_interval})")
```

Modify `run_discussion` loop to add quotes:
```python
async def run_discussion(self, max_iterations: int = 48) -> List[Dict]:
    """Main discussion loop with quote enrichment"""
    
    # ... existing setup ...
    
    while self.group_state.turn_number < max_iterations:
        
        # ... existing turn generation ...
        
        # Generate response
        response = await speaker.generate_response(
            group_state=self.group_state,
            recommended_move=recommended_move,
            recent_exchanges=self.group_state.exchanges[-5:]
        )
        
        # 🆕 QUOTE ENRICHMENT
        if self.enable_quote_enrichment and self.quote_agent:
            if self.quote_agent.should_enrich(
                turn_number=self.group_state.turn_number,
                phase='mid'
            ):
                # Extract current topics
                from src.analysis.topic_extractor import TopicExtractor
                topic_extractor = TopicExtractor(use_embeddings=False)
                topics = list(topic_extractor.extract_topics(response))
                
                # Get current tension if available
                current_tension = self.group_state.current_tension
                
                # Build discussion context
                recent_context = "\n".join([
                    f"{e['speaker']}: {e['content'][:200]}"
                    for e in self.group_state.exchanges[-3:]
                ])
                
                # Enrich with quote
                response = await self.quote_agent.enrich_response(
                    response=response,
                    speaker=speaker.state,
                    discussion_topics=topics,
                    current_tension=current_tension,
                    discussion_context=recent_context
                )
                
                logger.info(f"📖 Quote added to {speaker.state.name}'s response")
        
        # ... rest of existing exchange recording ...
    
    # Log quote statistics
    if self.enable_quote_enrichment and self.quote_agent:
        quote_stats = self.quote_agent.get_statistics()
        logger.info(f"📚 Quote Statistics: {quote_stats}")
    
    # ... existing closing logic ...
```

---

## Phase 5: Configuration & CLI

### 5.1 Update Configuration

**File**: `talks.yml` (add section)

```yaml
# Philosophical Quotes Enrichment
quotes:
  enabled: true
  interval: 8  # Add quote every N turns
  voice_adaptation: true  # Adapt quotes to speaker voice
  corpus_path: "data/philosophical_quotes.jsonl"
  
  # Retrieval settings
  retrieval:
    top_k: 3
    relevance_threshold: 0.65
    diversity_weight: 0.3  # Balance relevance vs diversity (0-1)
  
  # Balance targets (for corpus curation)
  balance:
    era:
      ancient: 0.35
      modern: 0.35
      contemporary: 0.30
    tradition:
      western: 0.60
      eastern: 0.30
      other: 0.10
```

### 5.2 Add Config Properties

**File**: `src/config/talks_config.py` (add)

```python
@property
def quote_enrichment_enabled(self) -> bool:
    """Check if quote enrichment is enabled"""
    return self.get('quotes.enabled', True)

@property
def quote_interval(self) -> int:
    """Get quote placement interval"""
    return self.get('quotes.interval', 8)

@property
def quote_voice_adaptation(self) -> bool:
    """Check if voice adaptation for quotes is enabled"""
    return self.get('quotes.voice_adaptation', True)
```

### 5.3 Update CLI

**File**: `src/cli/client.py` (modify)

```python
@click.option("--no-quotes", is_flag=True, help="Disable philosophical quote enrichment")
@click.option("--quote-interval", default=8, help="Turns between quotes (default: 8)")
def main(..., no_quotes, quote_interval):
    # ... in orchestrator creation ...
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        ...,
        enable_quote_enrichment=not no_quotes,
        quote_interval=quote_interval
    )
```

---

## Phase 6: Testing

### 6.1 Create Test Script

**File**: `test_quote_enrichment.py` (new file)

```python
#!/usr/bin/env python3
"""Test philosophical quote enrichment system"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.retrieval.quote_retriever import QuoteRetriever
from src.agents.quote_enrichment_agent import QuoteEnrichmentAgent
from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype


async def test_quote_retrieval():
    """Test basic quote retrieval"""
    
    print("\n" + "="*60)
    print("TEST 1: Quote Retrieval")
    print("="*60 + "\n")
    
    retriever = QuoteRetriever()
    
    # Test retrieval with topics
    quotes = retriever.retrieve(
        topics=["truth", "knowledge", "certainty"],
        current_tension=("necessity", "contingency"),
        top_k=3
    )
    
    print(f"Retrieved {len(quotes)} quotes:")
    for i, quote in enumerate(quotes, 1):
        print(f"\n{i}. {quote['author']} ({quote['era']}, {quote['tradition']})")
        print(f"   \"{quote['quote']}\"")
        print(f"   Relevance: {quote.get('relevance_score', 0):.3f}")
        print(f"   Topics: {', '.join(quote['topics'][:5])}")
    
    assert len(quotes) > 0, "Should retrieve at least one quote"
    print("\n✅ Quote retrieval test passed")


async def test_voice_adaptation():
    """Test quote voice adaptation"""
    
    print("\n" + "="*60)
    print("TEST 2: Voice Adaptation")
    print("="*60 + "\n")
    
    enrichment_agent = QuoteEnrichmentAgent()
    
    # Create test speaker
    speaker = ParticipantState(
        participant_id="test_speaker",
        name="Sophia",
        gender=Gender.FEMALE,
        personality=PersonalityArchetype.CREATIVE,
        expertise="philosophy"
    )
    
    # Test quote
    test_quote = {
        'id': 'test_01',
        'quote': 'The unexamined life is not worth living.',
        'author': 'Socrates',
        'topics': ['self-knowledge', 'philosophy']
    }
    
    adapted = await enrichment_agent._adapt_quote_to_voice(
        quote=test_quote,
        speaker=speaker,
        context="We've been discussing consciousness and self-awareness."
    )
    
    print(f"Original: \"{test_quote['quote']}\"")
    print(f"\nAdapted for {speaker.name} ({speaker.personality.value}):")
    print(f"\"{adapted}\"")
    
    assert len(adapted) > 10, "Adapted quote should have substance"
    print("\n✅ Voice adaptation test passed")


async def test_full_enrichment():
    """Test full enrichment flow"""
    
    print("\n" + "="*60)
    print("TEST 3: Full Enrichment Flow")
    print("="*60 + "\n")
    
    enrichment_agent = QuoteEnrichmentAgent(quote_interval=2)
    
    speaker = ParticipantState(
        participant_id="test_speaker",
        name="Marcus",
        gender=Gender.MALE,
        personality=PersonalityArchetype.ANALYTICAL,
        expertise="logic"
    )
    
    # Original response
    original = "Consciousness seems to require both unity and diversity of experience."
    
    # Enrich
    enriched = await enrichment_agent.enrich_response(
        response=original,
        speaker=speaker,
        discussion_topics=["consciousness", "experience", "unity"],
        current_tension=("structure", "agency"),
        discussion_context="We're exploring how consciousness emerges."
    )
    
    print(f"Original response:\n{original}\n")
    print(f"Enriched response:\n{enriched}")
    
    assert len(enriched) > len(original), "Enriched should be longer"
    assert "consciousness" in enriched.lower(), "Should preserve topic"
    
    print("\n✅ Full enrichment test passed")


async def test_diversity_tracking():
    """Test author diversity enforcement"""
    
    print("\n" + "="*60)
    print("TEST 4: Diversity Tracking")
    print("="*60 + "\n")
    
    retriever = QuoteRetriever()
    
    # Retrieve multiple times
    for i in range(5):
        quotes = retriever.retrieve(
            topics=["ethics", "virtue"],
            top_k=2
        )
        
        if quotes:
            print(f"\nRetrieval {i+1}:")
            for q in quotes:
                print(f"  - {q['author']}: \"{q['quote'][:50]}...\"")
    
    # Check statistics
    stats = retriever.get_statistics()
    print(f"\nDiversity Statistics:")
    print(f"  Total quotes: {stats['total_quotes']}")
    print(f"  Quotes used: {stats['quotes_used']}")
    print(f"  Unique authors: {stats['unique_authors']}")
    print(f"  Recent authors: {stats['recent_authors']}")
    
    # Verify diversity
    recent_authors = stats['recent_authors']
    unique_recent = len(set(recent_authors))
    
    print(f"\n  Unique in recent 5: {unique_recent}/{len(recent_authors)}")
    assert unique_recent >= 3, "Should have good author diversity"
    
    print("\n✅ Diversity tracking test passed")


async def main():
    """Run all tests"""
    await test_quote_retrieval()
    await test_voice_adaptation()
    await test_full_enrichment()
    await test_diversity_tracking()
    
    print("\n" + "="*60)
    print("🎉 ALL QUOTE ENRICHMENT TESTS PASSED")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Summary of Implementation

### New Components Created

| File                                   | Purpose                          |
| -------------------------------------- | -------------------------------- |
| `data/philosophical_quotes.jsonl`      | Curated corpus of 500-800 quotes |
| `scripts/build_quote_corpus.py`        | Corpus building utility          |
| `src/retrieval/quote_retriever.py`     | Hybrid retrieval with diversity  |
| `src/agents/quote_enrichment_agent.py` | Strategic quote placement        |
| `test_quote_enrichment.py`             | Comprehensive testing            |

### Modified Components

| File                                | Changes                      |
| ----------------------------------- | ---------------------------- |
| `src/orchestration/orchestrator.py` | Integration with quote agent |
| `talks.yml`                         | Quote configuration section  |
| `src/cli/client.py`                 | CLI options for quotes       |

### Key Features

✅ **Semantic retrieval** - Finds relevant quotes using embeddings  
✅ **Voice adaptation** - Quotes adapted to speaker personality  
✅ **Diversity enforcement** - Balanced authors, eras, traditions  
✅ **Strategic placement** - Optimal timing (every ~8 turns)  
✅ **Usage tracking** - Prevents repetition  
✅ **Configurable** - Easy to tune or disable  

### Usage Examples

```bash
# Normal run with quotes
poetry run talks --topic "The nature of consciousness" --depth 3

# Disable quotes
poetry run talks --topic "AI ethics" --depth 2 --no-quotes

# Adjust quote frequency
poetry run talks --topic "Free will" --depth 3 --quote-interval 12

# Test quote system
python test_quote_enrichment.py
```

### Quote Corpus Building

To build your initial corpus:

```bash
# 1. Create data directory
mkdir -p data

# 2. Run corpus builder (you'll need to add actual quotes)
python scripts/build_quote_corpus.py

# 3. Verify corpus
cat data/philosophical_quotes.jsonl | jq '.' | head -20
```

### Integration with Existing Features

This quote enrichment works seamlessly with:
- **RAG Style Transfer** - Quotes are voice-adapted like search results
- **Progression Control** - Quotes placed during natural flow, not forced
- **Dialectical Synthesis** - Can reference quotes in syntheses
- **Cognitive Coda** - Final codas can echo session quotes

The philosophical gems system transforms discussions from mere exchanges into **quotable wisdom**, giving audiences memorable anchors while maintaining natural conversational flow.