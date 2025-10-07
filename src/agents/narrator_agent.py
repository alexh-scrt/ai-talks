import logging
from typing import List, Dict, Optional
from src.agents.base_agent import BaseAgent
from src.states.participant_state import ParticipantState
from src.utils.text_processing import strip_reasoning

logger = logging.getLogger(__name__)


class NarratorAgent(BaseAgent):
    """Narrator agent for introducing AI Talks discussions"""
    
    def __init__(
        self,
        name: str = "Michael Lee",
        model: Optional[str] = None,
        session_id: Optional[str] = None,
        web_search: bool = True
    ):
        super().__init__(
            agent_id="narrator",
            web_search=web_search,
            model=model,
            session_id=session_id,
            llm_params={"temperature": 0.7}
        )
        self.name = name
    
    async def process(self, prompt: str, context: Optional[str] = None) -> str:
        """Implementation of abstract method from BaseAgent"""
        response = await self.generate_with_llm(prompt, context)
        return strip_reasoning(response)
    
    async def introduce_show(self) -> str:
        """Welcome introduction to AI Talks"""
        prompt = f"""You are {self.name}, the host of AI Talks - a show where AI participants engage in deep philosophical and intellectual discussions.

Generate a brief, engaging welcome introduction (2-3 sentences). Be warm, professional, and set an intellectual tone. Don't mention specific topics yet.

IMPORTANT: Avoid pop culture references. Keep the tone timeless and academic.

Example style: "Welcome to AI Talks, where artificial minds explore the deepest questions of our time. I'm your host, {self.name}, and today we have an extraordinary discussion lined up for you."

Your introduction:"""
        
        response = await self.generate_with_llm(prompt)
        return strip_reasoning(response)
    
    async def introduce_topic(self, topic: str) -> str:
        """Introduce and provide context for the discussion topic"""
        prompt = f"""You are {self.name}, the host of AI Talks. You have ALREADY welcomed the audience and introduced yourself.

The topic for today's discussion is: "{topic}"

Create an engaging introduction for this topic that:
1. States the topic clearly (start with "Today we're exploring..." or similar)
2. Comments on why this topic is interesting, relevant, or controversial
3. Provides 1-2 hooks to capture the audience's attention
4. Sets up anticipation for the discussion

IMPORTANT: 
- DO NOT say "Welcome to AI Talks" or "I'm Michael Lee" - you already did that.
- Avoid pop culture references (movies, TV shows, celebrities)
- Focus on timeless philosophical and scientific concepts

Keep it to 3-4 sentences. Be engaging and thought-provoking.

Your topic introduction:"""
        
        response = await self.generate_with_llm(prompt)
        return strip_reasoning(response)
    
    async def introduce_participants(self, participants: List[ParticipantState]) -> str:
        """Introduce each participant with their expertise"""
        participant_intros = []
        for p in participants:
            participant_intros.append(
                f"- {p.name} ({p.get_pronouns()}): {p.personality.value} thinker, expertise in {p.expertise_area}"
            )
        
        participants_text = "\n".join(participant_intros)
        
        prompt = f"""You are {self.name}, the host of AI Talks. You have ALREADY welcomed the audience and introduced the topic.

Today's participants are:
{participants_text}

Create an engaging introduction of these participants that:
1. Introduces each by name with a brief description of their expertise
2. Highlights what unique perspective each brings
3. Builds anticipation for their discussion

IMPORTANT: 
- DO NOT say "Welcome to AI Talks" or "I'm Michael Lee" - you already did that.
- Start with something like "Joining us today..." or "Our panel features..." or "Let me introduce our participants..."
- Avoid pop culture comparisons when describing participants
- Focus on their intellectual contributions and expertise

Keep it to 4-5 sentences total. Make each participant sound distinguished and interesting.

Your participant introductions:"""
        
        response = await self.generate_with_llm(prompt)
        return strip_reasoning(response)
    
    async def prompt_discussion_start(self, topic: str, first_speaker: str) -> str:
        """Transition from introduction to the actual discussion"""
        prompt = f"""You are {self.name}, the host of AI Talks. You have ALREADY welcomed everyone, introduced the topic, and introduced the participants.

The topic is: "{topic}"
The first speaker will be: {first_speaker}

Create a brief transition (1-2 sentences) that:
1. Signals the start of the discussion
2. Naturally hands off to the first speaker by name
3. Maintains the energy and anticipation

IMPORTANT: 
- Keep it short and direct. No need to re-introduce anything.
- Maintain intellectual tone without pop culture references

Example: "Let's dive right in. {first_speaker}, what's your take on this?"

Your transition:"""
        
        response = await self.generate_with_llm(prompt)
        return strip_reasoning(response)
    
    async def generate_full_introduction(
        self,
        topic: str,
        participants: List[ParticipantState],
        first_speaker: str
    ) -> List[Dict[str, str]]:
        """Generate the complete introduction sequence"""
        introduction_segments = []
        
        # Welcome
        welcome = await self.introduce_show()
        introduction_segments.append({
            "type": "welcome",
            "content": welcome,
            "speaker": self.name
        })
        
        # Topic introduction
        topic_intro = await self.introduce_topic(topic)
        introduction_segments.append({
            "type": "topic_intro",
            "content": topic_intro,
            "speaker": self.name
        })
        
        # Participant introductions
        participant_intro = await self.introduce_participants(participants)
        introduction_segments.append({
            "type": "participant_intro",
            "content": participant_intro,
            "speaker": self.name
        })
        
        # Transition to discussion
        transition = await self.prompt_discussion_start(topic, first_speaker)
        introduction_segments.append({
            "type": "transition",
            "content": transition,
            "speaker": self.name
        })
        
        return introduction_segments
    
    async def summarize_discussion(
        self,
        topic: str,
        exchanges: List[Dict[str, str]],
        participants: List[ParticipantState]
    ) -> str:
        """Generate a summary of the discussion"""
        
        # Extract key exchanges
        key_points = []
        for exchange in exchanges[-10:]:  # Focus on recent exchanges
            if exchange.get("move") in ["DEEPEN", "SYNTHESIZE", "CONCLUDE"]:
                key_points.append(f"{exchange['speaker']}: {exchange['content'][:100]}...")
        
        key_points_text = "\n".join(key_points[:5]) if key_points else "Various perspectives were shared."
        
        prompt = f"""You are {self.name}, the host of AI Talks. The discussion on "{topic}" has just concluded.

Key exchanges:
{key_points_text}

Create a brief summary (3-4 sentences) that:
1. Captures the main insights and arguments
2. Acknowledges different perspectives presented
3. Highlights any consensus or key disagreements
4. Sounds natural and conversational

IMPORTANT: Avoid pop culture references. Keep it intellectual and timeless.

Your summary:"""
        
        response = await self.generate_with_llm(prompt)
        return strip_reasoning(response)
    
    async def generate_closing_remarks(self, topic: str) -> str:
        """Generate podcast-style closing remarks"""
        prompt = f"""You are {self.name}, the host of AI Talks. You're closing today's episode about "{topic}".

Generate closing remarks (2-3 sentences) in this style:
"That's a wrap on today's AI Talks. I'm {self.name}. If today's dive into [topic] sparked something in you, follow and share the show. Join us next time as we explore another fascinating intellectual journey. Until then — stay curious, and keep questioning. Thank you for listening!"

Adapt the template to:
1. Reference today's specific topic naturally
2. Keep the call-to-action (follow/share)
3. Tease the next episode without specifics
4. Include the "stay curious" sentiment
5. End with thanks

IMPORTANT: Avoid pop culture references. Keep it professional and timeless.

Your closing:"""
        
        response = await self.generate_with_llm(prompt)
        return strip_reasoning(response)
    
    async def coordinate_transition(
        self,
        last_speaker: str,
        last_content: str,
        last_move: str,
        next_speaker: str,
        topic: str,
        turn_number: int
    ) -> str:
        """Generate a brief coordinator interjection between speakers"""
        
        # Extract key point from last content (first 150 chars for context)
        last_snippet = last_content[:150] if len(last_content) > 150 else last_content
        
        # Create move-specific context
        move_context = {
            "CHALLENGE": "challenging perspective",
            "SUPPORT": "supportive insight",
            "DEEPEN": "deeper exploration",
            "QUESTION": "probing question",
            "SYNTHESIZE": "synthesis",
            "CONCLUDE": "concluding thought"
        }.get(last_move, "contribution")
        
        prompt = f"""You are {self.name}, the discussion coordinator for AI Talks. 

Last speaker: {last_speaker} ({move_context})
Key point: "{last_snippet}..."
Next speaker: {next_speaker}
Turn: {turn_number}
Topic: {topic}

Generate a VERY BRIEF interjection (1-2 short sentences MAX) that:
1. Acknowledges the significance or nature of what {last_speaker} just said
2. Smoothly transitions to {next_speaker}

CRITICAL RULES:
- Be concise and natural
- Vary your language - don't repeat phrases from previous turns
- Reference the content subtly without summarizing
- Use different transition styles based on turn number to avoid repetition
- Keep energy and engagement high
- No generic phrases like "interesting point"

Examples of good interjections:
- "That's a provocative angle. {next_speaker}, how do you see it?"
- "The plot thickens! {next_speaker}, your turn."
- "{last_speaker} just opened a new door. {next_speaker}, walk us through it."
- "Now we're getting somewhere. {next_speaker}?"
- "That challenges everything. {next_speaker}, thoughts?"

Your interjection:"""
        
        response = await self.generate_with_llm(prompt)
        return strip_reasoning(response)
    
    async def generate_full_closing(
        self,
        topic: str,
        exchanges: List[Dict[str, str]],
        participants: List[ParticipantState]
    ) -> List[Dict[str, str]]:
        """Generate the complete closing sequence"""
        closing_segments = []
        
        # Generate summary
        summary = await self.summarize_discussion(topic, exchanges, participants)
        closing_segments.append({
            "type": "summary",
            "content": summary,
            "speaker": self.name
        })
        
        # Generate closing remarks
        closing = await self.generate_closing_remarks(topic)
        closing_segments.append({
            "type": "closing_remarks",
            "content": closing,
            "speaker": self.name
        })
        
        return closing_segments