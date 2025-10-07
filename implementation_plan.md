# Talks: Implementation Instructions for Claude Code

## Project Overview

Build a multi-agent philosophical discussion system called **Talks** that uses game theory to orchestrate natural conversations between 2-N AI participants with distinct personalities, genders, and expertise areas.

---

## Phase 1: Project Setup & Foundation

### Step 1.1: Initialize Project Structure

Create a new Python project with this structure:

```
talks/
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── states/
│   │   ├── __init__.py
│   │   ├── participant_state.py
│   │   └── group_state.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── participant_agent.py
│   ├── game_theory/
│   │   ├── __init__.py
│   │   ├── payoff_calculator.py
│   │   └── turn_selector.py
│   ├── termination/
│   │   ├── __init__.py
│   │   ├── depth_manager.py
│   │   └── conversation_terminator.py
│   ├── orchestration/
│   │   ├── __init__.py
│   │   └── orchestrator.py
│   └── cli/
│       ├── __init__.py
│       └── client.py
├── configs/
│   ├── simple.yaml
│   └── academic_panel.yaml
└── tests/
    ├── __init__.py
    ├── test_game_theory.py
    └── test_agents.py
```

**Instructions**:
1. Create the directory structure above
2. Initialize with `poetry init` or `pip` setup
3. Add `.gitignore` with Python patterns

---

### Step 1.2: Set Up pyproject.toml

**File**: `pyproject.toml`

```toml
[tool.poetry]
name = "talks"
version = "0.1.0"
description = "Multi-agent philosophical discussion system with game theory"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
langchain = "^0.1.0"
langchain-ollama = "^0.1.0"
chromadb = "^0.4.22"
redis = "^5.0.0"
pydantic = "^2.5.0"
numpy = "^1.26.0"
pyyaml = "^6.0"
click = "^8.1.0"
rich = "^13.7.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.12.0"
ruff = "^0.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

**Instructions**:
1. Run `poetry install` or `pip install -e .`
2. Verify dependencies are installed

---

### Step 1.3: Docker Compose Infrastructure

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: talks-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=24h
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  chromadb:
    image: chromadb/chroma:latest
    container_name: talks-chromadb
    ports:
      - "8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - ANONYMIZED_TELEMETRY=FALSE
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: talks-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

volumes:
  ollama_data:
  chromadb_data:
  redis_data:
```

**Instructions**:
1. Run `docker-compose up -d`
2. Pull model: `docker exec talks-ollama ollama pull mistral` (or your preferred model)
3. Verify services: `docker-compose ps`

---

### Step 1.4: Environment Configuration

**File**: `.env.example`

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=mistral
LLM_TEMPERATURE=0.85

# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Discussion Settings
DEFAULT_DEPTH=3
MAX_ITERATIONS=30
SIMILARITY_THRESHOLD=0.85

# Logging
LOG_LEVEL=INFO
```

**Instructions**:
1. Copy to `.env`: `cp .env.example .env`
2. Adjust settings as needed

---

## Phase 2: Core Data Models

### Step 2.1: Participant State

**File**: `src/states/participant_state.py`

```python
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"


class PersonalityArchetype(Enum):
    ANALYTICAL = "analytical"
    COLLABORATIVE = "collaborative"
    ASSERTIVE = "assertive"
    CAUTIOUS = "cautious"
    CREATIVE = "creative"
    SKEPTICAL = "skeptical"


@dataclass
class ParticipantState:
    """State for each discussion participant"""
    
    # Identity
    participant_id: str
    name: str
    gender: Gender
    personality: PersonalityArchetype
    expertise_area: str
    core_beliefs: List[str] = field(default_factory=list)
    
    # Dynamic discussion state
    confidence_level: float = 0.7
    curiosity_level: float = 0.8
    engagement_level: float = 0.8
    
    # Social dynamics
    relationships: Dict[str, float] = field(default_factory=dict)
    respect_levels: Dict[str, float] = field(default_factory=dict)
    
    # Conversation tracking
    speaking_turns: int = 0
    words_spoken: int = 0
    questions_asked: int = 0
    positions_taken: List[str] = field(default_factory=list)
    agreements_made: List[str] = field(default_factory=list)
    challenges_made: List[str] = field(default_factory=list)
    
    # Topic exploration
    depth_explored: int = 1
    aspects_covered: Set[str] = field(default_factory=set)
    
    # Turn-taking state
    wants_to_speak: float = 0.5
    last_spoke_turn: int = -1
    was_addressed: bool = False
    
    def update_relationship(self, other_id: str, delta: float):
        """Update relationship with another participant"""
        current = self.relationships.get(other_id, 0.0)
        self.relationships[other_id] = max(-1.0, min(1.0, current + delta))
    
    def update_respect(self, other_id: str, delta: float):
        """Update respect for another participant"""
        current = self.respect_levels.get(other_id, 0.5)
        self.respect_levels[other_id] = max(0.0, min(1.0, current + delta))
    
    def get_pronouns(self) -> str:
        """Get pronouns based on gender"""
        return {
            Gender.MALE: "he/him",
            Gender.FEMALE: "she/her",
            Gender.NON_BINARY: "they/them"
        }[self.gender]
```

**Instructions**:
1. Implement the complete ParticipantState class
2. Add validation for ranges (0-1 for levels, etc.)
3. Add `__repr__` for debugging
4. Write unit tests for update methods

---

### Step 2.2: Group Discussion State

**File**: `src/states/group_state.py`

```python
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from src.states.participant_state import ParticipantState


@dataclass
class GroupDiscussionState:
    """Global state for the entire group discussion"""
    
    # Topic
    topic: str
    target_depth: int
    
    # Participants
    participants: Dict[str, ParticipantState] = field(default_factory=dict)
    participant_order: List[str] = field(default_factory=list)
    
    # Discussion progress
    turn_number: int = 0
    exchanges: List[Dict] = field(default_factory=list)
    
    # Depth tracking (shared across all participants)
    aspects_explored: Set[str] = field(default_factory=set)
    max_depth_reached: int = 1
    
    # Group dynamics
    dominant_speaker: Optional[str] = None
    coalitions: List[Set[str]] = field(default_factory=list)
    active_disagreement: bool = False
    
    # Termination tracking
    convergence_level: float = 0.0
    novelty_score: float = 1.0
    
    def get_participant(self, participant_id: str) -> ParticipantState:
        """Get participant state by ID"""
        return self.participants[participant_id]
    
    def get_other_participants(self, participant_id: str) -> List[ParticipantState]:
        """Get all other participants"""
        return [p for pid, p in self.participants.items() if pid != participant_id]
    
    def get_recent_speakers(self, n: int = 3) -> List[str]:
        """Get last N speakers"""
        if not self.exchanges:
            return []
        return [e["speaker_id"] for e in self.exchanges[-n:]]
    
    def add_exchange(self, exchange: Dict):
        """Add exchange and update turn number"""
        self.exchanges.append(exchange)
        self.turn_number += 1
```

**Instructions**:
1. Implement GroupDiscussionState
2. Add methods for accessing participant data
3. Add method to serialize to JSON (for Redis storage)
4. Write tests for participant filtering

---

## Phase 3: Game Theory Engine

### Step 3.1: Dialogue Move Model

**File**: `src/game_theory/__init__.py`

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class DialogueMove:
    """A possible dialogue move by a participant"""
    move_type: str  # DEEPEN, CHALLENGE, SUPPORT, QUESTION, SYNTHESIZE, CONCLUDE
    target: Optional[str] = None  # participant_id or None for group
    intensity: float = 0.5  # 0-1


# Move types constant
MOVE_TYPES = [
    "DEEPEN",
    "CHALLENGE",
    "SUPPORT",
    "QUESTION",
    "SYNTHESIZE",
    "CONCLUDE"
]
```

---

### Step 3.2: Turn Selection Algorithm

**File**: `src/game_theory/turn_selector.py`

```python
import numpy as np
from typing import Dict
from src.states.participant_state import ParticipantState, PersonalityArchetype
from src.states.group_state import GroupDiscussionState


class TurnSelector:
    """Selects next speaker using game-theoretic urgency calculation"""
    
    def calculate_speaking_urgency(
        self,
        participant: ParticipantState,
        group_state: GroupDiscussionState
    ) -> float:
        """
        Calculate how much this participant wants to speak RIGHT NOW
        
        Returns: 0.0-1.0 urgency score
        """
        urgency = 0.0
        
        # Factor 1: Personality-based baseline (30%)
        personality_urgency = {
            PersonalityArchetype.ASSERTIVE: 0.7,
            PersonalityArchetype.COLLABORATIVE: 0.5,
            PersonalityArchetype.ANALYTICAL: 0.4,
            PersonalityArchetype.CREATIVE: 0.6,
            PersonalityArchetype.CAUTIOUS: 0.3,
            PersonalityArchetype.SKEPTICAL: 0.5
        }
        urgency += personality_urgency[participant.personality] * 0.3
        
        # Factor 2: Time since last spoke (20%)
        turns_since_spoke = group_state.turn_number - participant.last_spoke_turn
        if participant.last_spoke_turn == -1:
            time_factor = 0.5
        else:
            time_factor = min(1.0, turns_since_spoke / 5)
        urgency += time_factor * 0.2
        
        # Factor 3: Was just addressed (40%)
        if participant.was_addressed:
            urgency += 0.4
        
        # Factor 4: High confidence (10%)
        urgency += participant.confidence_level * 0.1
        
        # Factor 5: Engagement level (20%)
        urgency += participant.engagement_level * 0.2
        
        # Fairness adjustments
        if group_state.dominant_speaker == participant.participant_id:
            urgency *= 0.7
        
        # Balance turns
        if len(group_state.participants) > 0:
            avg_turns = np.mean([p.speaking_turns for p in group_state.participants.values()])
            if participant.speaking_turns < avg_turns * 0.5:
                urgency *= 1.3
        
        return min(1.0, urgency)
    
    def select_next_speaker(self, group_state: GroupDiscussionState) -> str:
        """
        Determine who speaks next using game theory
        
        Returns: participant_id of next speaker
        """
        urgency_scores = {}
        
        for pid, participant in group_state.participants.items():
            urgency = self.calculate_speaking_urgency(participant, group_state)
            urgency_scores[pid] = urgency
        
        # Add randomness (80% game theory, 20% random)
        randomized_scores = {
            pid: score * 0.8 + np.random.random() * 0.2
            for pid, score in urgency_scores.items()
        }
        
        next_speaker = max(randomized_scores.items(), key=lambda x: x[1])[0]
        
        return next_speaker
```

**Instructions**:
1. Implement TurnSelector class
2. Add logging to show urgency calculations
3. Write tests with mock participants
4. Verify fairness over many iterations

---

### Step 3.3: Move Payoff Calculator

**File**: `src/game_theory/payoff_calculator.py`

```python
import numpy as np
from typing import Dict, Tuple
from src.states.participant_state import ParticipantState, PersonalityArchetype
from src.states.group_state import GroupDiscussionState
from src.game_theory import DialogueMove


class PayoffCalculator:
    """Calculates utility payoffs for each possible dialogue move"""
    
    def calculate_move_payoffs(
        self,
        speaker: ParticipantState,
        group_state: GroupDiscussionState
    ) -> Dict[str, float]:
        """
        Calculate utility for each possible dialogue move
        
        Returns: Dict of move_type -> payoff score
        """
        payoffs = {}
        
        other_participants = group_state.get_other_participants(speaker.participant_id)
        recent_speakers = group_state.get_recent_speakers(n=2)
        
        # DEEPEN move payoff
        depth_gap = group_state.target_depth - speaker.depth_explored
        recent_deepening = any(
            e.get("move") == "DEEPEN" 
            for e in group_state.exchanges[-3:]
        )
        
        payoffs["DEEPEN"] = (
            depth_gap * 0.3 +
            speaker.curiosity_level * 0.4 +
            (0.3 if not recent_deepening else 0.1)
        )
        
        # CHALLENGE move payoff
        can_challenge = len(recent_speakers) > 0
        if can_challenge:
            last_speaker_id = recent_speakers[-1]
            last_speaker = group_state.get_participant(last_speaker_id)
            relationship = speaker.relationships.get(last_speaker_id, 0.0)
            
            payoffs["CHALLENGE"] = (
                (1.0 if speaker.personality == PersonalityArchetype.SKEPTICAL else 0.5) * 0.3 +
                last_speaker.confidence_level * 0.3 +
                max(0, -relationship) * 0.2 +
                (0.2 if speaker.confidence_level > 0.6 else 0.1)
            )
        else:
            payoffs["CHALLENGE"] = 0.0
        
        # SUPPORT move payoff
        if can_challenge:
            last_speaker_id = recent_speakers[-1]
            relationship = speaker.relationships.get(last_speaker_id, 0.0)
            respect = speaker.respect_levels.get(last_speaker_id, 0.5)
            
            payoffs["SUPPORT"] = (
                (1.0 if speaker.personality == PersonalityArchetype.COLLABORATIVE else 0.5) * 0.3 +
                max(0, relationship) * 0.4 +
                respect * 0.3
            )
        else:
            payoffs["SUPPORT"] = 0.0
        
        # QUESTION move payoff
        payoffs["QUESTION"] = (
            (1.0 if speaker.personality == PersonalityArchetype.ANALYTICAL else 0.6) * 0.4 +
            speaker.curiosity_level * 0.3 +
            (0.3 if speaker.questions_asked < 3 else 0.1)
        )
        
        # SYNTHESIZE move payoff
        num_recent_perspectives = len(set(recent_speakers))
        disagreement_level = 1.0 - group_state.convergence_level
        sweet_spot = abs(disagreement_level - 0.5) < 0.3
        
        payoffs["SYNTHESIZE"] = (
            (1.0 if speaker.personality in [PersonalityArchetype.CREATIVE, PersonalityArchetype.ANALYTICAL] else 0.5) * 0.3 +
            min(num_recent_perspectives / 3, 1.0) * 0.3 +
            (0.4 if sweet_spot else 0.2)
        )
        
        # CONCLUDE move payoff
        depth_reached = group_state.max_depth_reached >= group_state.target_depth
        aspects_sufficient = len(group_state.aspects_explored) >= group_state.target_depth * 3
        
        payoffs["CONCLUDE"] = (
            (0.4 if depth_reached else 0.0) +
            (0.3 if aspects_sufficient else 0.0) +
            (0.3 if group_state.novelty_score < 0.3 else 0.0)
        )
        
        return payoffs
    
    def recommend_move_and_target(
        self,
        speaker: ParticipantState,
        group_state: GroupDiscussionState
    ) -> Tuple[DialogueMove, float]:
        """
        Recommend both move type and target
        
        Returns: (DialogueMove, confidence)
        """
        payoffs = self.calculate_move_payoffs(speaker, group_state)
        
        best_move_type = max(payoffs.items(), key=lambda x: x[1])[0]
        confidence = payoffs[best_move_type]
        
        # Determine target
        target = None
        if best_move_type in ["CHALLENGE", "SUPPORT", "QUESTION"]:
            recent_speakers = group_state.get_recent_speakers(n=2)
            if recent_speakers:
                target = recent_speakers[-1]
        
        # Determine intensity
        intensity_map = {
            PersonalityArchetype.ASSERTIVE: 0.8,
            PersonalityArchetype.SKEPTICAL: 0.7,
            PersonalityArchetype.CAUTIOUS: 0.4,
            PersonalityArchetype.COLLABORATIVE: 0.5,
            PersonalityArchetype.ANALYTICAL: 0.6,
            PersonalityArchetype.CREATIVE: 0.7
        }
        intensity = intensity_map[speaker.personality]
        
        move = DialogueMove(
            move_type=best_move_type,
            target=target,
            intensity=intensity
        )
        
        return move, confidence
```

**Instructions**:
1. Implement PayoffCalculator
2. Add detailed logging of payoff calculations
3. Write tests for each move type
4. Verify payoffs make intuitive sense

---

## Phase 4: Participant Agent

### Step 4.1: Agent Implementation

**File**: `src/agents/participant_agent.py`

```python
import logging
from typing import List, Dict
from langchain_ollama import ChatOllama
from src.states.participant_state import ParticipantState, Gender
from src.states.group_state import GroupDiscussionState
from src.game_theory import DialogueMove
from src.game_theory.payoff_calculator import PayoffCalculator

logger = logging.getLogger(__name__)


class ParticipantAgent:
    """A single participant in a multi-person discussion"""
    
    def __init__(
        self,
        participant_id: str,
        name: str,
        gender: Gender,
        personality,
        expertise: str,
        session_id: str,
        llm_model: str = "mistral",
        llm_temperature: float = 0.85
    ):
        self.state = ParticipantState(
            participant_id=participant_id,
            name=name,
            gender=gender,
            personality=personality,
            expertise_area=expertise
        )
        
        self.llm = ChatOllama(
            model=llm_model,
            temperature=llm_temperature
        )
        
        self.payoff_calculator = PayoffCalculator()
        self.session_id = session_id
    
    async def generate_response(
        self,
        topic: str,
        group_state: GroupDiscussionState,
        recommended_move: DialogueMove
    ) -> str:
        """Generate philosophical response using game theory"""
        
        prompt = self._build_prompt(
            topic=topic,
            group_state=group_state,
            move=recommended_move
        )
        
        logger.info(f"{self.state.name} generating response for move: {recommended_move.move_type}")
        
        response = await self.llm.ainvoke(prompt)
        
        await self._update_state(response.content, recommended_move, group_state)
        
        return response.content
    
    def _build_prompt(
        self,
        topic: str,
        group_state: GroupDiscussionState,
        move: DialogueMove
    ) -> str:
        """Build context-aware prompt"""
        
        other_participants = group_state.get_other_participants(self.state.participant_id)
        recent_exchanges = group_state.exchanges[-5:]
        
        # Format participants
        participants_desc = "\n".join([
            f"- {p.name} ({p.get_pronouns()}): {p.personality.value}, expertise in {p.expertise_area}"
            for p in other_participants
        ])
        
        # Format recent exchanges
        exchanges_text = "\n\n".join([
            f"{e['speaker']}: {e['content']}"
            for e in recent_exchanges
        ])
        
        # Get move instructions
        move_instructions = self._get_move_instructions(move, group_state)
        
        # Relationship context
        relationships = self._format_relationships(other_participants)
        
        return f"""You are {self.state.name}, a {self.state.personality.value} thinker with expertise in {self.state.expertise_area}.
You use {self.state.get_pronouns()} pronouns.

DISCUSSION TOPIC: {topic}
TARGET DEPTH: Level {group_state.target_depth}/5

OTHER PARTICIPANTS:
{participants_desc}

YOUR RELATIONSHIPS:
{relationships}

RECENT EXCHANGES:
{exchanges_text}

YOUR TASK: {move_instructions}

Guidelines:
- Stay true to your {self.state.personality.value} personality
- Keep response to 2-4 sentences
- If addressing someone specific, use their name
- Maintain perspective from your {self.state.expertise_area} expertise
- Be natural, not expository

Respond as {self.state.name} would in this discussion."""
    
    def _get_move_instructions(
        self,
        move: DialogueMove,
        group_state: GroupDiscussionState
    ) -> str:
        """Get instructions for specific move"""
        
        target_name = None
        if move.target:
            target_state = group_state.get_participant(move.target)
            target_name = target_state.name
        
        instructions = {
            "DEEPEN": "Push the discussion deeper. Introduce a more nuanced aspect that hasn't been explored.",
            "CHALLENGE": f"Respectfully challenge {target_name}'s point. Present a counterargument." if target_name else "Challenge the prevailing view.",
            "SUPPORT": f"Build on {target_name}'s insight. Add supporting evidence." if target_name else "Support the emerging consensus.",
            "QUESTION": f"Ask {target_name} a clarifying question." if target_name else "Ask a question that advances understanding.",
            "SYNTHESIZE": "Find common ground between different viewpoints.",
            "CONCLUDE": "Summarize key insights and suggest we're reaching a conclusion."
        }
        
        return instructions[move.move_type]
    
    def _format_relationships(self, other_participants: List[ParticipantState]) -> str:
        """Format relationship context"""
        lines = []
        for p in other_participants:
            affinity = self.state.relationships.get(p.participant_id, 0.0)
            if affinity > 0.3:
                lines.append(f"- You respect {p.name}'s perspective")
            elif affinity < -0.3:
                lines.append(f"- You disagree with {p.name} on key points")
        return "\n".join(lines) if lines else "- No strong relationships yet"
    
    async def _update_state(
        self,
        response: str,
        move: DialogueMove,
        group_state: GroupDiscussionState
    ):
        """Update state after speaking"""
        
        self.state.speaking_turns += 1
        self.state.words_spoken += len(response.split())
        self.state.last_spoke_turn = group_state.turn_number
        
        # Update relationships
        if move.target:
            if move.move_type == "SUPPORT":
                self.state.update_relationship(move.target, +0.1)
                self.state.agreements_made.append(move.target)
            elif move.move_type == "CHALLENGE":
                self.state.update_relationship(move.target, -0.05)
                self.state.challenges_made.append(move.target)
        
        # Extract aspects (simple keyword extraction)
        aspects = self._extract_aspects(response)
        self.state.aspects_covered.update(aspects)
        
        # Update confidence/curiosity
        if move.move_type == "CHALLENGE":
            self.state.confidence_level = min(1.0, self.state.confidence_level + 0.1)
        elif move.move_type == "QUESTION":
            self.state.curiosity_level = min(1.0, self.state.curiosity_level + 0.1)
    
    def _extract_aspects(self, text: str) -> set:
        """Extract discussed aspects (simplified)"""
        # TODO: Implement proper keyword extraction
        # For now, return empty set
        return set()
```

**Instructions**:
1. Implement ParticipantAgent
2. Test prompt generation independently
3. Add proper aspect extraction using NLP
4. Write tests for state updates

---

## Phase 5: Orchestrator

### Step 5.1: Main Orchestrator

**File**: `src/orchestration/orchestrator.py`

```python
import logging
import uuid
from typing import List, Dict
from src.states.group_state import GroupDiscussionState
from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype
from src.agents.participant_agent import ParticipantAgent
from src.game_theory.turn_selector import TurnSelector
from src.game_theory.payoff_calculator import PayoffCalculator

logger = logging.getLogger(__name__)


class MultiAgentDiscussionOrchestrator:
    """Orchestrates discussion among N participants"""
    
    def __init__(
        self,
        topic: str,
        target_depth: int,
        participants_config: List[Dict]
    ):
        self.session_id = f"talks_{uuid.uuid4().hex[:8]}"
        self.topic = topic
        self.target_depth = target_depth
        
        # Initialize participants
        self.participants = {}
        for config in participants_config:
            agent = ParticipantAgent(
                participant_id=config["name"].lower(),
                name=config["name"],
                gender=Gender(config["gender"]),
                personality=PersonalityArchetype(config["personality"]),
                expertise=config["expertise"],
                session_id=self.session_id
            )
            self.participants[agent.state.participant_id] = agent
        
        # Initialize group state
        self.group_state = GroupDiscussionState(
            topic=topic,
            target_depth=target_depth,
            participants={pid: agent.state for pid, agent in self.participants.items()},
            participant_order=list(self.participants.keys())
        )
        
        # Game theory components
        self.turn_selector = TurnSelector()
        self.payoff_calculator = PayoffCalculator()
    
    async def run_discussion(self) -> List[Dict]:
        """Main discussion loop"""
        
        logger.info(f"🎭 Starting {len(self.participants)}-person discussion")
        logger.info(f"📖 Topic: {self.topic}")
        logger.info(f"📊 Target Depth: {self.target_depth}")
        
        max_iterations = 30  # TODO: Make configurable
        
        while self.group_state.turn_number < max_iterations:
            # Select next speaker
            next_speaker_id = self.turn_selector.select_next_speaker(self.group_state)
            speaker = self.participants[next_speaker_id]
            
            logger.info(f"\n--- Turn {self.group_state.turn_number + 1}: {speaker.state.name} ---")
            
            # Calculate recommended move
            recommended_move, confidence = self.payoff_calculator.recommend_move_and_target(
                speaker.state,
                self.group_state
            )
            
            logger.info(f"Move: {recommended_move.move_type} (confidence: {confidence:.2f})")
            if recommended_move.target:
                target_name = self.group_state.get_participant(recommended_move.target).name
                logger.info(f"Addressing: {target_name}")
            
            # Generate response
            response = await speaker.generate_response(
                topic=self.topic,
                group_state=self.group_state,
                recommended_move=recommended_move
            )
            
            # Record exchange
            exchange = {
                "turn": self.group_state.turn_number,
                "speaker": speaker.state.name,
                "speaker_id": next_speaker_id,
                "content": response,
                "move": recommended_move.move_type,
                "target": recommended_move.target,
                "personality": speaker.state.personality.value
            }
            self.group_state.add_exchange(exchange)
            
            # Update group-level metrics
            await self._update_group_state(response, speaker.state)
            
            # Update addressing flags
            self._update_addressing(recommended_move)
            
            # Check basic termination (for now)
            if self._should_terminate_basic():
                logger.info("\n✅ Discussion complete")
                break
        
        return self.group_state.exchanges
    
    async def _update_group_state(self, response: str, speaker: ParticipantState):
        """Update group-level state after each turn"""
        
        # Update aspects explored
        self.group_state.aspects_explored.update(speaker.aspects_covered)
        
        # Update max depth
        self.group_state.max_depth_reached = max(
            p.depth_explored for p in self.group_state.participants.values()
        )
        
        # Update dominant speaker
        max_turns = max(p.speaking_turns for p in self.group_state.participants.values())
        for pid, p in self.group_state.participants.items():
            if p.speaking_turns == max_turns:
                self.group_state.dominant_speaker = pid
                break
    
    def _update_addressing(self, move):
        """Mark if any participant was addressed"""
        # Reset all
        for p in self.group_state.participants.values():
            p.was_addressed = False
        
        # Mark target
        if move.target:
            self.group_state.participants[move.target].was_addressed = True
    
    def _should_terminate_basic(self) -> bool:
        """Basic termination check (will be enhanced in Phase 6)"""
        # Check if multiple participants want to conclude
        conclude_count = sum(
            1 for e in self.group_state.exchanges[-len(self.participants):]
            if e.get("move") == "CONCLUDE"
        )
        
        return conclude_count >= len(self.participants) * 0.5
```

**Instructions**:
1. Implement the complete orchestrator
2. Add detailed logging at each step
3. Test with 2 participants first
4. Verify turn-taking fairness

---

## Phase 6: Termination System

### Step 6.1: Depth Manager

**File**: `src/termination/depth_manager.py`

```python
from typing import Set


class DepthManager:
    """Determines if current depth level is sufficiently explored"""
    
    def __init__(self, target_depth: int):
        self.target_depth = target_depth
        self.aspects_required = {
            1: 2,  # Surface
            2: 3,  # Principles
            3: 4,  # Applications
            4: 4,  # Challenges
            5: 5   # Philosophy
        }
    
    def is_depth_explored(
        self,
        aspects_covered: Set[str],
        exchange_count: int
    ) -> bool:
        """
        Check if current depth is sufficiently explored
        
        Criteria:
        - Minimum number of aspects covered
        - Minimum number of exchanges
        """
        min_aspects = self.aspects_required[self.target_depth]
        min_exchanges = self.target_depth * 3
        
        return (
            len(aspects_covered) >= min_aspects and
            exchange_count >= min_exchanges
        )
    
    def get_progress(
        self,
        aspects_covered: Set[str],
        exchange_count: int
    ) -> float:
        """
        Calculate progress toward depth goal (0.0 to 1.0)
        """
        min_aspects = self.aspects_required[self.target_depth]
        min_exchanges = self.target_depth * 3
        
        aspect_progress = min(1.0, len(aspects_covered) / min_aspects)
        exchange_progress = min(1.0, exchange_count / min_exchanges)
        
        return (aspect_progress + exchange_progress) / 2
```

**Instructions**:
1. Implement DepthManager
2. Add progress tracking method
3. Write tests for each depth level
4. Verify thresholds are reasonable

---

### Step 6.2: Conversation Terminator

**File**: `src/termination/conversation_terminator.py`

```python
import logging
from typing import Tuple, List
from src.termination.depth_manager import DepthManager
from src.states.group_state import GroupDiscussionState

logger = logging.getLogger(__name__)


class ConversationTerminator:
    """
    Determines when dialogue has sufficiently explored the topic
    
    Uses multiple signals:
    1. Depth coverage
    2. Convergence
    3. Novelty exhaustion
    4. Explicit readiness
    """
    
    def __init__(self, target_depth: int):
        self.target_depth = target_depth
        self.depth_manager = DepthManager(target_depth)
        self.exchange_history: List[str] = []
    
    async def should_terminate(
        self,
        group_state: GroupDiscussionState,
        exchange_count: int,
        last_exchange: str
    ) -> Tuple[bool, str]:
        """
        Comprehensive termination check
        
        Returns: (should_stop, reason)
        """
        
        # Criterion 1: Depth exploration complete
        depth_complete = self.depth_manager.is_depth_explored(
            group_state.aspects_explored,
            exchange_count
        )
        
        if not depth_complete:
            progress = self.depth_manager.get_progress(
                group_state.aspects_explored,
                exchange_count
            )
            logger.debug(f"Depth progress: {progress:.0%}")
            return False, "Depth not sufficiently explored"
        
        # Criterion 2: Convergence (if depth complete)
        if group_state.convergence_level > 0.8 and exchange_count > self.target_depth * 3:
            return True, "High convergence achieved"
        
        # Criterion 3: Multiple conclude votes
        recent_concludes = sum(
            1 for e in group_state.exchanges[-len(group_state.participants):]
            if e.get("move") == "CONCLUDE"
        )
        
        threshold = len(group_state.participants) * 0.7
        if recent_concludes >= threshold:
            return True, "Group consensus to conclude"
        
        # Criterion 4: Maximum exchanges (safety)
        max_exchanges = self.target_depth * 10
        if exchange_count >= max_exchanges:
            return True, "Maximum exchanges reached"
        
        return False, "Continue dialogue"
```

**Instructions**:
1. Implement ConversationTerminator
2. Add novelty checking (ChromaDB integration) in Phase 7
3. Write tests for each criterion
4. Log termination checks for debugging

---

## Phase 7: CLI Interface

### Step 7.1: CLI Client

**File**: `src/cli/client.py`

```python
import asyncio
import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from src.orchestration.orchestrator import MultiAgentDiscussionOrchestrator

console = Console()


@click.command()
@click.option("--topic", "-t", required=True, help="Discussion topic")
@click.option("--depth", "-d", default=3, type=int, help="Depth level (1-5)")
@click.option("--participants", "-p", default=2, type=int, help="Number of participants")
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file path")
def main(topic: str, depth: int, participants: int, config: str):
    """Talks: Multi-Agent Philosophical Discussion System"""
    
    console.print(Panel.fit(
        "[bold cyan]🎭 Talks: Multi-Agent Discussion System[/bold cyan]",
        border_style="cyan"
    ))
    
    # Load config or use defaults
    if config:
        with open(config) as f:
            config_data = yaml.safe_load(f)
        participants_config = config_data["participants"]
    else:
        participants_config = get_default_participants(participants)
    
    console.print(f"\n[bold]Topic:[/bold] {topic}")
    console.print(f"[bold]Depth:[/bold] {depth}/5")
    console.print(f"[bold]Participants:[/bold] {len(participants_config)}\n")
    
    # Display participants
    for p in participants_config:
        console.print(
            f"  • {p['name']} ({p['gender']}) - "
            f"{p['personality']} - {p['expertise']}"
        )
    
    console.print("\n" + "─" * 60 + "\n")
    
    # Run discussion
    asyncio.run(run_discussion(topic, depth, participants_config))


async def run_discussion(topic: str, depth: int, participants_config: list):
    """Run the discussion and display results"""
    
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic=topic,
        target_depth=depth,
        participants_config=participants_config
    )
    
    exchanges = await orchestrator.run_discussion()
    
    # Display exchanges
    for exchange in exchanges:
        speaker = exchange["speaker"]
        content = exchange["content"]
        move = exchange["move"]
        turn = exchange["turn"]
        
        console.print(f"\n[bold cyan]Turn {turn + 1}: {speaker}[/bold cyan] [dim]({move})[/dim]")
        console.print(Panel(content, border_style="cyan", padding=(1, 2)))
    
    # Display summary
    console.print("\n" + "─" * 60)
    console.print(f"\n[bold green]✅ Discussion Complete[/bold green]")
    console.print(f"Total Exchanges: {len(exchanges)}")
    console.print(f"Aspects Explored: {len(orchestrator.group_state.aspects_explored)}")
    console.print(f"Max Depth Reached: {orchestrator.group_state.max_depth_reached}/{depth}")


def get_default_participants(count: int) -> list:
    """Get default participant configurations"""
    
    defaults = [
        {
            "name": "Sophia",
            "gender": "female",
            "personality": "collaborative",
            "expertise": "ethics"
        },
        {
            "name": "Marcus",
            "gender": "male",
            "personality": "skeptical",
            "expertise": "logic"
        },
        {
            "name": "Aisha",
            "gender": "female",
            "personality": "analytical",
            "expertise": "science"
        },
        {
            "name": "James",
            "gender": "male",
            "personality": "creative",
            "expertise": "philosophy"
        },
        {
            "name": "Elena",
            "gender": "female",
            "personality": "assertive",
            "expertise": "psychology"
        }
    ]
    
    return defaults[:count]


if __name__ == "__main__":
    main()
```

**Instructions**:
1. Implement CLI with rich formatting
2. Test with different depth levels
3. Add progress indicators during discussion
4. Handle errors gracefully

---

### Step 7.2: Main Entry Point

**File**: `src/main.py`

```python
#!/usr/bin/env python3
"""
Talks: Multi-Agent Philosophical Discussion System
"""

import sys
from src.cli.client import main

if __name__ == "__main__":
    sys.exit(main())
```

**File**: `pyproject.toml` (add scripts section)

```toml
[tool.poetry.scripts]
talks = "src.main:main"
```

**Instructions**:
1. Make main.py executable
2. Test CLI: `poetry run talks --topic "What is consciousness?" --depth 3`
3. Verify all options work

---

## Phase 8: Configuration Files

### Step 8.1: Simple Config

**File**: `configs/simple.yaml`

```yaml
topic: "What is the meaning of life?"
depth: 2

participants:
  - name: Sophia
    gender: female
    personality: collaborative
    expertise: existentialism
    
  - name: Marcus
    gender: male
    personality: skeptical
    expertise: logic
```

---

### Step 8.2: Academic Panel Config

**File**: `configs/academic_panel.yaml`

```yaml
topic: "Should AI systems have rights?"
depth: 4

participants:
  - name: Dr. Elena Rodriguez
    gender: female
    personality: analytical
    expertise: cognitive_science
    
  - name: Prof. James Chen
    gender: male
    personality: assertive
    expertise: machine_learning
    
  - name: Dr. Aisha Okonkwo
    gender: female
    personality: cautious
    expertise: ai_safety
    
  - name: Dr. Marcus Williams
    gender: male
    personality: creative
    expertise: philosophy_of_mind
```

**Instructions**:
1. Create both config files
2. Test loading with `--config` flag
3. Add validation for required fields

---

## Phase 9: Testing

### Step 9.1: Game Theory Tests

**File**: `tests/test_game_theory.py`

```python
import pytest
from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype
from src.states.group_state import GroupDiscussionState
from src.game_theory.turn_selector import TurnSelector
from src.game_theory.payoff_calculator import PayoffCalculator


def test_speaking_urgency_addressed():
    """Participant who was addressed should have high urgency"""
    
    participant = ParticipantState(
        participant_id="test",
        name="Test",
        gender=Gender.FEMALE,
        personality=PersonalityArchetype.COLLABORATIVE,
        expertise_area="test",
        was_addressed=True
    )
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=3,
        participants={"test": participant}
    )
    
    selector = TurnSelector()
    urgency = selector.calculate_speaking_urgency(participant, group_state)
    
    assert urgency > 0.4  # Should be high due to was_addressed


def test_move_payoff_deepen():
    """DEEPEN payoff should be high when depth gap exists"""
    
    participant = ParticipantState(
        participant_id="test",
        name="Test",
        gender=Gender.MALE,
        personality=PersonalityArchetype.ANALYTICAL,
        expertise_area="test",
        depth_explored=1,
        curiosity_level=0.9
    )
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=5,
        participants={"test": participant}
    )
    
    calculator = PayoffCalculator()
    payoffs = calculator.calculate_move_payoffs(participant, group_state)
    
    assert payoffs["DEEPEN"] > 0.5  # Should be high


def test_turn_selection_fairness():
    """Turn selection should eventually balance across participants"""
    
    participants = {
        "p1": ParticipantState(
            participant_id="p1",
            name="P1",
            gender=Gender.FEMALE,
            personality=PersonalityArchetype.ASSERTIVE,
            expertise_area="test",
            speaking_turns=10  # Has spoken a lot
        ),
        "p2": ParticipantState(
            participant_id="p2",
            name="P2",
            gender=Gender.MALE,
            personality=PersonalityArchetype.CAUTIOUS,
            expertise_area="test",
            speaking_turns=1  # Hasn't spoken much
        )
    }
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=3,
        participants=participants,
        dominant_speaker="p1"
    )
    
    selector = TurnSelector()
    
    # Run multiple selections
    selections = []
    for _ in range(100):
        selections.append(selector.select_next_speaker(group_state))
    
    # P2 should be selected more often
    p2_count = selections.count("p2")
    assert p2_count > 40  # At least 40% of the time
```

**Instructions**:
1. Write comprehensive tests for game theory
2. Test edge cases (1 participant, all same personality, etc.)
3. Run tests: `pytest tests/test_game_theory.py`

---

### Step 9.2: Agent Tests

**File**: `tests/test_agents.py`

```python
import pytest
from src.agents.participant_agent import ParticipantAgent
from src.states.participant_state import Gender, PersonalityArchetype
from src.states.group_state import GroupDiscussionState
from src.game_theory import DialogueMove


@pytest.mark.asyncio
async def test_agent_state_update():
    """Agent should update state after speaking"""
    
    agent = ParticipantAgent(
        participant_id="test",
        name="Test",
        gender=Gender.FEMALE,
        personality=PersonalityArchetype.COLLABORATIVE,
        expertise="test",
        session_id="test_session"
    )
    
    initial_turns = agent.state.speaking_turns
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=3
    )
    
    move = DialogueMove(move_type="DEEPEN")
    
    await agent._update_state("test response", move, group_state)
    
    assert agent.state.speaking_turns == initial_turns + 1


@pytest.mark.asyncio
async def test_agent_relationship_update():
    """Agent should update relationships based on moves"""
    
    agent = ParticipantAgent(
        participant_id="agent1",
        name="Agent1",
        gender=Gender.MALE,
        personality=PersonalityArchetype.SKEPTICAL,
        expertise="test",
        session_id="test_session"
    )
    
    group_state = GroupDiscussionState(
        topic="test",
        target_depth=3
    )
    
    # Support move should increase relationship
    move = DialogueMove(move_type="SUPPORT", target="agent2")
    await agent._update_state("I agree", move, group_state)
    
    assert agent.state.relationships.get("agent2", 0) > 0
```

**Instructions**:
1. Write tests for agent behavior
2. Mock LLM responses for testing
3. Test relationship dynamics
4. Run: `pytest tests/test_agents.py`

---

## Phase 10: Documentation

### Step 10.1: README

**File**: `README.md`

```markdown
# Talks: Multi-Agent Philosophical Discussion System

🎭 An AI-powered system that orchestrates rich philosophical discussions using game theory and emergent social dynamics.

## Features

- **Game-Theoretic Turn-Taking**: Mathematical model determines who speaks next
- **Depth-Aware Exploration**: Configure conversation depth (1-5 levels)
- **Personality Diversity**: 6 distinct personality archetypes
- **Gender Representation**: Male, female, and non-binary participants
- **Emergent Dynamics**: Relationships and coalitions form naturally
- **Smart Termination**: Multi-criteria conversation completion

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/talks.git
cd talks

# Install dependencies
poetry install

# Start infrastructure
docker-compose up -d

# Pull LLM model
docker exec talks-ollama ollama pull mistral
```

### Basic Usage

```bash
# Simple 2-person dialogue
talks --topic "What is consciousness?" --depth 3 --participants 2

# Use config file
talks --config configs/academic_panel.yaml

# Deep philosophical exploration
talks --topic "Ethics of AI" --depth 5 --participants 4
```

## Configuration

Create YAML configs to customize participants:

```yaml
topic: "Your question here"
depth: 3

participants:
  - name: Sophia
    gender: female
    personality: collaborative
    expertise: ethics
```

### Personality Types

- **Analytical**: Methodical, asks probing questions
- **Collaborative**: Seeks consensus, builds bridges
- **Assertive**: Confident, dominates discussion
- **Cautious**: Careful claims, hedges statements
- **Creative**: Novel perspectives, metaphorical
- **Skeptical**: Challenges assumptions, devil's advocate

## Architecture

See [DESIGN.md](DESIGN.md) for detailed architecture documentation.

## Development

```bash
# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/
```

## License

MIT License - see LICENSE file for details
```

**Instructions**:
1. Create comprehensive README
2. Add badges (tests, coverage, etc.)
3. Include screenshots/examples
4. Keep updated with new features

---

## Phase 11: Final Integration & Polish

### Step 11.1: Logging Setup

**File**: `src/__init__.py`

```python
import logging
import sys

def setup_logging(level=logging.INFO):
    """Configure logging for the application"""
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce verbosity of external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

setup_logging()
```

---

### Step 11.2: Error Handling

Add try-except blocks in orchestrator:

```python
async def run_discussion(self) -> List[Dict]:
    """Main discussion loop with error handling"""
    
    try:
        # ... existing code ...
        
        while self.group_state.turn_number < max_iterations:
            try:
                # ... turn logic ...
                
            except Exception as e:
                logger.error(f"Error in turn {self.group_state.turn_number}: {e}")
                # Skip this turn and continue
                continue
        
        return self.group_state.exchanges
        
    except Exception as e:
        logger.error(f"Fatal error in discussion: {e}")
        raise
```

---

## Testing Checklist

### Phase 1 Tests
- [ ] Project structure created correctly
- [ ] Dependencies install without errors
- [ ] Docker services start successfully
- [ ] Ollama model pulled and working

### Phase 2 Tests
- [ ] ParticipantState can be created
- [ ] Relationships update correctly
- [ ] GroupDiscussionState tracks participants
- [ ] States can be serialized to JSON

### Phase 3 Tests
- [ ] Speaking urgency calculations are reasonable
- [ ] Turn selection is fair over many iterations
- [ ] Move payoffs make intuitive sense
- [ ] Personalities affect payoff calculations

### Phase 4 Tests
- [ ] Agent generates responses (mock LLM)
- [ ] Prompts include all required context
- [ ] State updates after speaking
- [ ] Relationships change based on moves

### Phase 5 Tests
- [ ] Orchestrator initializes correctly
- [ ] Discussion runs for 2 participants
- [ ] Turn-taking alternates appropriately
- [ ] Exchanges are recorded properly

### Phase 6 Tests
- [ ] Depth manager tracks progress
- [ ] Termination criteria work independently
- [ ] Discussion ends appropriately
- [ ] Different depths produce different lengths

### Phase 7 Tests
- [ ] CLI accepts all arguments
- [ ] Config files load correctly
- [ ] Output is formatted nicely
- [ ] Errors are handled gracefully

### Phase 8-11 Tests
- [ ] All configs work
- [ ] Tests pass: `pytest`
- [ ] Code formatted: `black src/`
- [ ] Documentation complete

---

## Deployment Checklist

- [ ] All tests passing
- [ ] Documentation complete
- [ ] Example configs provided
- [ ] Docker compose working
- [ ] README has clear instructions
- [ ] License file added
- [ ] .gitignore configured
- [ ] Environment variables documented

---

## Next Steps After Implementation

1. **Enhanced Termination**: Add ChromaDB-based novelty detection
2. **Convergence Metrics**: Implement position similarity using embeddings
3. **Coalition Detection**: Identify aligned participants
4. **Web API**: FastAPI endpoints for programmatic access
5. **Visualization**: Network graphs of relationships
6. **Memory**: Long-term memory across sessions
7. **Debate Mode**: Competitive discussions
8. **Creative Writing**: Character dialogue generation

---

## Common Issues & Solutions

### Issue: Ollama connection refused
**Solution**: Ensure Docker is running: `docker-compose up -d`

### Issue: Model not found
**Solution**: Pull model: `docker exec talks-ollama ollama pull mistral`

### Issue: Turn selection not fair
**Solution**: Check speaking_turns in state, verify fairness adjustment multipliers

### Issue: Discussion too short/long
**Solution**: Adjust depth thresholds in DepthManager or max_iterations

### Issue: Personalities not distinct
**Solution**: Increase LLM temperature, enhance personality descriptions in prompts

---

## Performance Optimization

### For Faster Responses
- Use smaller LLM model (e.g., mistral vs mixtral)
- Reduce temperature slightly
- Cache frequent computations
- Use async/await properly

### For Better Quality
- Increase temperature for variety
- Enhance prompt engineering
- Add more personality traits
- Use larger model (mixtral, gpt-oss:120b)

---

## Congratulations! 🎉

You've now implemented **Talks**, a sophisticated multi-agent discussion system!

### What You've Built

✅ Game-theoretic turn-taking  
✅ Multi-agent orchestration  
✅ Personality-driven dialogue  
✅ Depth-aware exploration  
✅ Smart termination criteria  
✅ Rich CLI interface  

### Test It Out

```bash
poetry run talks \
  --topic "What makes something morally right?" \
  --depth 4 \
  --participants 3
```

Enjoy watching AI agents engage in genuine philosophical discourse! 🎭