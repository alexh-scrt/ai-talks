import logging
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from src.config import TalksConfig
from src.states.group_state import GroupDiscussionState
from src.states.participant_state import ParticipantState, Gender, PersonalityArchetype
from src.agents.participant_agent import ParticipantAgent
from src.agents.narrator_agent import NarratorAgent
from src.game_theory.turn_selector import TurnSelector
from src.game_theory.payoff_calculator import PayoffCalculator
from src.game_theory.strategic_coordinator import StrategicCoordinator

logger = logging.getLogger(__name__)


class MultiAgentDiscussionOrchestrator:
    """Orchestrates discussion among N participants with optional narrator"""
    
    def __init__(
        self,
        topic: str,
        target_depth: int,
        participants_config: List[Dict],
        enable_narrator: Optional[bool] = None,
        narrator_name: Optional[str] = None,
        enable_synthesizer: Optional[bool] = None,
        synthesis_frequency: int = 8,
        synthesis_style: str = "hegelian",
        use_rag_styling: Optional[bool] = None,
        enable_strategic_scoring: Optional[bool] = None
    ):
        # Load configuration
        config = TalksConfig()
        
        self.session_id = f"talks_{uuid.uuid4().hex[:8]}"
        self.topic = topic
        self.target_depth = target_depth
        self.forbidden_topics = config.forbidden_topics
        self.recursion_limit = config.recursion_limit
        
        # Use config defaults if not specified
        if enable_narrator is None:
            enable_narrator = config.narrator_enabled
        if narrator_name is None:
            narrator_name = config.narrator_name
        
        # RAG styling configuration
        if use_rag_styling is None:
            use_rag_styling = config.rag_style_transfer_enabled
        
        # Initialize participants
        self.participants = {}
        for config_item in participants_config:
            agent = ParticipantAgent(
                participant_id=config_item["name"].lower().replace(" ", "_"),
                name=config_item["name"],
                gender=Gender(config_item["gender"]),
                personality=PersonalityArchetype(config_item["personality"]),
                expertise=config_item["expertise"],
                session_id=self.session_id,
                use_rag_styling=use_rag_styling
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
        
        # Narrator (optional)
        self.enable_narrator = enable_narrator
        self.narrator = None
        self.first_speaker_id = None  # Store who narrator calls on
        self.narrator_context = ""  # Store narrator's full introduction
        if enable_narrator:
            self.narrator = NarratorAgent(
                name=narrator_name,
                session_id=self.session_id
            )
        self.introduction_segments = []
        self.closing_segments = []
        
        # Synthesizer (optional)
        if enable_synthesizer is None:
            enable_synthesizer = config.get('synthesizer.enabled', True)
        
        self.enable_synthesizer = enable_synthesizer
        self.synthesizer = None
        self.synthesis_frequency = synthesis_frequency
        
        if enable_synthesizer:
            from src.agents.dialectical_synthesizer import DialecticalSynthesizerAgent
            self.synthesizer = DialecticalSynthesizerAgent(
                name=config.get('synthesizer.name', 'The Synthesizer'),
                synthesis_style=synthesis_style,
                session_id=self.session_id
            )
            logger.info(f"🔄 Synthesizer enabled: {self.synthesizer.name} (style: {synthesis_style}, freq: {synthesis_frequency})")
        
        # Strategic Coordinator (optional)
        if enable_strategic_scoring is None:
            enable_strategic_scoring = config.get('objectives.strategic_scoring', True)
        
        self.enable_strategic_scoring = enable_strategic_scoring
        self.strategic_coordinator = None
        self.strategic_metrics = {}  # Store final metrics
        
        if enable_strategic_scoring:
            self.strategic_coordinator = StrategicCoordinator()
            logger.info("📊 Strategic scoring enabled")
        
        # Initialize logging queue
        self._log_queue = asyncio.Queue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        self._log_filepath = outputs_dir / f"conversation_{self.session_id}_{timestamp}.md"
        self._log_task = None
    
    async def run_introduction(self) -> List[Dict[str, str]]:
        """Generate and return narrator introduction segments"""
        if not self.narrator:
            return []
        
        # Determine first speaker and store it
        self.first_speaker_id = self.turn_selector.select_next_speaker(self.group_state)
        first_speaker_name = self.participants[self.first_speaker_id].state.name
        
        # Mark first speaker as addressed by narrator
        self.group_state.participants[self.first_speaker_id].was_addressed = True
        
        # Generate full introduction
        participant_states = [agent.state for agent in self.participants.values()]
        self.introduction_segments = await self.narrator.generate_full_introduction(
            topic=self.topic,
            participants=participant_states,
            first_speaker=first_speaker_name
        )
        
        # Store narrator context for first speaker
        self.narrator_context = "\n".join([
            f"{seg['speaker']}: {seg['content']}"
            for seg in self.introduction_segments
        ])
        
        # Queue narrator introduction to log
        for segment in self.introduction_segments:
            await self._queue_message(
                segment['speaker'],
                segment['content'],
                "introduction"
            )
        
        return self.introduction_segments
    
    async def run_discussion(self, max_iterations: int = 30) -> List[Dict]:
        """Main discussion loop with optional narrator introduction"""
        
        logger.info(f"🎭 Starting {len(self.participants)}-person discussion")
        logger.info(f"📖 Topic: {self.topic}")
        logger.info(f"📊 Target Depth: {self.target_depth}")
        logger.info(f"🔄 Recursion Limit: {self.recursion_limit}")
        
        # Load coordinator settings from config
        config = TalksConfig()
        coordinator_mode = config.coordinator_mode
        coordinator_frequency = config.coordinator_frequency
        
        # Start logging
        await self._start_logging()
        
        try:
            # Run narrator introduction if enabled
            if self.enable_narrator:
                await self.run_introduction()
        
            while self.group_state.turn_number < max_iterations:
                # Select next speaker (use designated first speaker if this is turn 1 with narrator)
                if self.group_state.turn_number == 0 and self.first_speaker_id:
                    next_speaker_id = self.first_speaker_id
                else:
                    next_speaker_id = self.turn_selector.select_next_speaker(self.group_state)
                speaker = self.participants[next_speaker_id]
                
                logger.info(f"\n--- Turn {self.group_state.turn_number + 1}: {speaker.state.name} ---")
                
                # Check if coordinator should interject BEFORE this speaker (not on turn 0)
                if coordinator_mode and self.narrator and self.group_state.turn_number > 0 and not self._should_terminate_basic():
                    # coordinator_frequency: 0 means every turn, otherwise every N turns
                    if coordinator_frequency == 0:
                        should_interject = True
                    elif coordinator_frequency > 0:
                        should_interject = self.group_state.turn_number % coordinator_frequency == 0
                    else:
                        should_interject = False
                    
                    if should_interject:
                        # Get the last exchange for context
                        if self.group_state.exchanges:
                            last_exchange = self.group_state.exchanges[-1]
                            last_speaker_name = last_exchange["speaker"]
                            last_content = last_exchange["content"]
                            last_move = last_exchange["move"]
                            
                            # Generate coordinator interjection addressing the current speaker
                            coordinator_interjection = await self.narrator.coordinate_transition(
                                last_speaker=last_speaker_name,
                                last_content=last_content,
                                last_move=last_move,
                                next_speaker=speaker.state.name,  # Address the already-selected speaker
                                topic=self.topic,
                                turn_number=self.group_state.turn_number
                            )
                            
                            # Queue coordinator interjection to log
                            await self._queue_message(
                                self.narrator.name,
                                coordinator_interjection,
                                "discussion"
                            )
                            
                            logger.info(f"🎙️ [{self.narrator.name}]: {coordinator_interjection[:100]}...")
                
                # Calculate recommended move
                recommended_move, confidence = self.payoff_calculator.recommend_move_and_target(
                    speaker.state,
                    self.group_state
                )
                
                logger.info(f"Move: {recommended_move.move_type} (confidence: {confidence:.2f})")
                if recommended_move.target:
                    target_name = self.group_state.get_participant(recommended_move.target).name
                    logger.info(f"Addressing: {target_name}")
                
                # Generate response (pass narrator context to first speaker)
                if self.group_state.turn_number == 0 and self.narrator_context:
                    response = await speaker.generate_response(
                        topic=self.topic,
                        group_state=self.group_state,
                        recommended_move=recommended_move,
                        narrator_context=self.narrator_context
                    )
                else:
                    response = await speaker.generate_response(
                        topic=self.topic,
                        group_state=self.group_state,
                        recommended_move=recommended_move
                    )
                
                # Queue participant response to log
                await self._queue_message(
                    speaker.state.name,
                    response,
                    "discussion"
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
                
                # STRATEGIC SCORING
                if self.enable_strategic_scoring and self.strategic_coordinator:
                    try:
                        evaluation = await self.strategic_coordinator.evaluate_turn(
                            agent=speaker.state,
                            move=recommended_move,
                            response=response,
                            group_state=self.group_state
                        )
                        # Optionally store evaluation in exchange
                        exchange['strategic_evaluation'] = evaluation
                    except Exception as e:
                        logger.error(f"Strategic evaluation failed: {e}")
                        # Continue discussion even if scoring fails
                
                # Synthesis checkpoint
                if (self.enable_synthesizer and 
                    self.group_state.turn_number > 0 and
                    self.group_state.turn_number % self.synthesis_frequency == 0 and
                    len(self.group_state.exchanges) >= 3):
                    
                    logger.info(f"🔄 Synthesis checkpoint at turn {self.group_state.turn_number}")
                    
                    try:
                        synthesis = await self.synthesizer.synthesize_segment(
                            exchanges=self.group_state.exchanges,
                            turn_window=min(self.synthesis_frequency, 8),
                            topic=self.topic
                        )
                        
                        if synthesis:
                            # Queue synthesis to log
                            await self._queue_message(
                                self.synthesizer.name,
                                synthesis,
                                "synthesis"
                            )
                            
                            logger.info(f"🔄 [{self.synthesizer.name}]: {synthesis[:100]}...")
                        else:
                            logger.debug("Synthesizer returned no synthesis")
                            
                    except Exception as e:
                        logger.error(f"Synthesis failed: {e}")
                        # Continue discussion even if synthesis fails
                
                # Update group-level metrics
                await self._update_group_state(response, speaker.state)
                
                # Update addressing flags
                self._update_addressing(recommended_move)
                
                # Check basic termination (for now)
                if self._should_terminate_basic():
                    logger.info("\n✅ Discussion complete")
                    break
        
            # LOG AGGREGATE METRICS
            if self.enable_strategic_scoring and self.strategic_coordinator:
                self.strategic_metrics = self.strategic_coordinator.get_aggregate_metrics()
                logger.info(f"📊 Discussion Metrics: {self.strategic_metrics}")
        
            # Generate narrator closing if enabled
            if self.enable_narrator:
                await self.run_closing()
        
        finally:
            # Stop logging
            await self._stop_logging()
        
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
        
        # Simple convergence calculation
        if len(self.group_state.exchanges) > 5:
            recent_moves = [e["move"] for e in self.group_state.exchanges[-5:]]
            support_ratio = recent_moves.count("SUPPORT") / len(recent_moves)
            self.group_state.convergence_level = min(1.0, self.group_state.convergence_level * 0.9 + support_ratio * 0.1)
        
        # Simple novelty calculation
        if len(self.group_state.exchanges) > 10:
            # Check if we're repeating topics
            recent_contents = [e["content"] for e in self.group_state.exchanges[-5:]]
            older_contents = [e["content"] for e in self.group_state.exchanges[-10:-5]]
            
            # Very simple similarity check (could be improved with embeddings)
            similar_count = 0
            for recent in recent_contents:
                for older in older_contents:
                    if len(set(recent.lower().split()) & set(older.lower().split())) > 5:
                        similar_count += 1
            
            similarity = similar_count / (len(recent_contents) * len(older_contents))
            self.group_state.novelty_score = max(0.0, 1.0 - similarity)
    
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
        if len(self.group_state.exchanges) >= len(self.participants):
            conclude_count = sum(
                1 for e in self.group_state.exchanges[-len(self.participants):]
                if e.get("move") == "CONCLUDE"
            )
            
            if conclude_count >= len(self.participants) * 0.5:
                return True
        
        # Check if we've reached target depth with sufficient exploration
        if self.group_state.max_depth_reached >= self.target_depth:
            if len(self.group_state.aspects_explored) >= self.target_depth * 2:
                return True
        
        return False
    
    async def run_closing(self) -> List[Dict[str, str]]:
        """Generate and return narrator closing segments"""
        if not self.narrator or not self.group_state.exchanges:
            return []
        
        # Get participant states for closing
        participant_states = [agent.state for agent in self.participants.values()]
        
        # Generate full closing
        self.closing_segments = await self.narrator.generate_full_closing(
            topic=self.topic,
            exchanges=self.group_state.exchanges,
            participants=participant_states
        )
        
        # Queue narrator closing to log
        for segment in self.closing_segments:
            await self._queue_message(
                segment['speaker'],
                segment['content'],
                "closing"
            )
        
        return self.closing_segments
    
    async def _queue_message(self, speaker: str, content: str, section: str = "discussion"):
        """Add a message to the logging queue"""
        await self._log_queue.put((speaker, content, section))
    
    def _clean_content(self, speaker: str, content: str) -> str:
        """Remove redundant speaker name from beginning of content"""
        if not content:
            return content
        
        # Trim whitespace
        cleaned = content.strip()
        
        import re
        
        # Pattern 1: Remove any instance of "speaker:" or "speaker_id:" at the beginning
        # This handles multiple occurrences like "Michael Lee: Michael Lee: ..."
        # Also handles bold markdown format like "**Speaker:**"
        # Keep removing until no more matches
        speaker_variations = [speaker]
        # Add common variations like replacing spaces with underscores
        speaker_id = speaker.lower().replace(" ", "_")
        speaker_variations.append(speaker_id)
        
        # Remove all instances of speaker name followed by colon at the start
        changed = True
        while changed:
            original = cleaned
            for variant in speaker_variations:
                # Match "Name:" at the start (case-insensitive)
                pattern = rf"^{re.escape(variant)}:\s*"
                cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).lstrip()
                
                # Also match "**Name:**" in bold markdown format
                bold_pattern = rf"^\*\*{re.escape(variant)}:\*\*\s*"
                cleaned = re.sub(bold_pattern, "", cleaned, flags=re.IGNORECASE).lstrip()
            changed = (original != cleaned)
        
        # Pattern 2: "**Name's Response:**" or "**Name's response:**" etc.
        # Match variations like **Cynthia's Response:**, **Bob's response:**, etc.
        response_pattern = rf"\*\*{re.escape(speaker)}'s [Rr]esponse:\*\*\s*\n?"
        cleaned = re.sub(response_pattern, "", cleaned, count=1).lstrip()
        
        # Pattern 3: Remove quotes if the entire response is quoted
        # e.g., '"Thank you all..." ' becomes 'Thank you all...'
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1].strip()
        elif cleaned.startswith("'") and cleaned.endswith("'"):
            cleaned = cleaned[1:-1].strip()
        
        return cleaned
    
    async def _log_writer(self):
        """Async task that writes queued messages to log file"""
        try:
            with open(self._log_filepath, "w", encoding="utf-8") as f:
                # Write header
                f.write(f"# AI Talks Conversation Log\n\n")
                f.write(f"**Topic:** {self.topic}\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Session:** {self.session_id}\n")
                f.write(f"**Participants:** {', '.join([p.state.name for p in self.participants.values()])}\n")
                if self.narrator:
                    f.write(f"**Narrator:** {self.narrator.name}\n")
                f.write(f"\n---\n")
                
                current_section = None
                
                while True:
                    try:
                        # Get message from queue with timeout
                        message = await asyncio.wait_for(
                            self._log_queue.get(), 
                            timeout=1.0
                        )
                        
                        if message is None:  # Sentinel to stop
                            break
                        
                        speaker, content, section = message
                        
                        # Add section headers
                        if section != current_section:
                            current_section = section
                            section_title = section.replace("_", " ").title()
                            f.write(f"\n## {section_title}\n")
                        
                        # Clean content to remove redundant speaker prefixes
                        cleaned_content = self._clean_content(speaker, content)
                        
                        # Write message with cleaned content (speaker already identified by XML tags)
                        f.write(f"\n<{speaker}>\n{cleaned_content}\n</{speaker}>\n")
                        f.flush()  # Ensure real-time writing
                        
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Error in log writer: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to create log file: {e}")
    
    async def _start_logging(self):
        """Start the async logging task"""
        if not self._log_task:
            self._log_task = asyncio.create_task(self._log_writer())
            logger.info(f"📝 Logging to: {self._log_filepath}")
    
    async def _stop_logging(self):
        """Stop the logging task gracefully"""
        if self._log_task:
            await self._log_queue.put(None)  # Sentinel to stop
            await self._log_task
            self._log_task = None
            logger.info(f"📝 Log saved to: {self._log_filepath}")