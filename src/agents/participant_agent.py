import logging
from typing import List, Dict, Optional
from src.agents.base_agent import BaseAgent
from src.states.participant_state import ParticipantState, Gender
from src.states.group_state import GroupDiscussionState
from src.game_theory import DialogueMove
from src.game_theory.payoff_calculator import PayoffCalculator
from src.utils.text_processing import strip_reasoning

logger = logging.getLogger(__name__)


class ParticipantAgent(BaseAgent):
    """A single participant in a multi-person discussion with tool calling capabilities"""
    
    def __init__(
        self,
        participant_id: str,
        name: str,
        gender: Gender,
        personality,
        expertise: str,
        session_id: str,
        llm_model: str = "qwen3:32b",
        llm_temperature: float = 0.85,
        web_search: bool = True,
        use_rag_styling: bool = True
    ):
        # Initialize base agent with tool support
        super().__init__(
            agent_id=participant_id,
            web_search=web_search,
            model=llm_model,
            session_id=session_id,
            llm_params={"temperature": llm_temperature}
        )
        
        self.state = ParticipantState(
            participant_id=participant_id,
            name=name,
            gender=gender,
            personality=personality,
            expertise_area=expertise
        )
        
        self.payoff_calculator = PayoffCalculator()
        
        # RAG Style Transfer
        self.use_rag_styling = use_rag_styling
        self._style_transfer = None
        
        if use_rag_styling:
            from src.agents.rag_style_transfer import RAGStyleTransferAgent
            self._style_transfer = RAGStyleTransferAgent(session_id=session_id)
            logger.info(f"🎨 Style transfer enabled for {name}")
    
    async def process(self, prompt: str, context: Optional[str] = None) -> str:
        """Implementation of abstract method from BaseAgent"""
        # Generate response using the LLM with potential tool calls
        response = await self.generate_with_llm(prompt, context)
        
        # Strip reasoning blocks from the response
        cleaned_content = strip_reasoning(response)
        
        return cleaned_content
    
    async def generate_response(
        self,
        topic: str,
        group_state: GroupDiscussionState,
        recommended_move: DialogueMove,
        narrator_context: Optional[str] = None
    ) -> str:
        """Generate philosophical response using game theory and tools"""
        
        prompt = self._build_prompt(
            topic=topic,
            group_state=group_state,
            move=recommended_move,
            narrator_context=narrator_context
        )
        
        logger.info(f"{self.state.name} generating response for move: {recommended_move.move_type}")
        
        # Use the enhanced generate_with_llm that handles tool calls
        raw_response = await self.generate_with_llm(prompt)
        
        # Check if web search or other tools were used
        tools_used = self._tools_used_this_turn
        
        # Apply style transfer if RAG was used
        if self.use_rag_styling and tools_used and self._style_transfer:
            logger.info(f"🎨 Applying style transfer for {self.state.name} (tools were used)")
            
            # Build discussion context for style transfer
            recent_exchanges = group_state.exchanges[-3:] if group_state.exchanges else []
            recent_context = "\n".join([
                f"{e['speaker']}: {e['content']}"
                for e in recent_exchanges
            ])
            
            try:
                styled_response = await self._style_transfer.rewrite_in_voice(
                    source_text=raw_response,
                    agent_persona=self.state,
                    discussion_context=recent_context,
                    search_metadata={"tools_called": self._last_tool_calls}
                )
                response = styled_response
            except Exception as e:
                logger.error(f"Style transfer failed: {e}, using raw response")
                response = raw_response
        else:
            response = raw_response
        
        # Strip reasoning blocks from the response
        cleaned_content = strip_reasoning(response)
        
        # Add to conversation history
        await self.add_to_history("assistant", cleaned_content, {
            "move_type": recommended_move.move_type,
            "target": recommended_move.target,
            "style_transferred": tools_used and self.use_rag_styling
        })
        
        await self._update_state(cleaned_content, recommended_move, group_state)
        
        return cleaned_content
    
    def _build_prompt(
        self,
        topic: str,
        group_state: GroupDiscussionState,
        move: DialogueMove,
        narrator_context: Optional[str] = None
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
        
        # Add narrator context section if this is the first response
        narrator_section = ""
        if narrator_context:
            narrator_section = f"""\nHOST INTRODUCTION:
{narrator_context}

The host has just called on you to begin the discussion. Acknowledge this naturally and dive into the topic.
"""
        
        return f"""You are {self.state.name}, a {self.state.personality.value} thinker with expertise in {self.state.expertise_area}.
You use {self.state.get_pronouns()} pronouns.

DISCUSSION TOPIC: {topic}
TARGET DEPTH: Level {group_state.target_depth}/5
{narrator_section}
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

FORBIDDEN TOPICS:
- DO NOT make references to pop culture (movies, TV shows, celebrities, memes, social media)
- Focus on timeless philosophical concepts and universal human experiences
- Draw from classical philosophy, science, logic, and enduring human questions

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
            self.state.questions_asked += 1
    
    def _extract_aspects(self, text: str) -> set:
        """Extract discussed aspects (simplified)"""
        # Simple keyword extraction for philosophical concepts
        keywords = []
        concept_markers = ["nature of", "meaning of", "essence of", "role of", "value of", 
                          "implications", "consequences", "perspective", "framework", "principle"]
        
        text_lower = text.lower()
        for marker in concept_markers:
            if marker in text_lower:
                # Extract the phrase around the marker
                idx = text_lower.find(marker)
                # Get surrounding words
                start = max(0, idx - 20)
                end = min(len(text), idx + len(marker) + 30)
                phrase = text[start:end].strip()
                if phrase:
                    keywords.append(phrase[:50])  # Limit length
        
        return set(keywords)