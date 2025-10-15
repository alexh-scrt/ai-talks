"""Controller for managing discussion progression and preventing orbiting"""

import asyncio
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from ..states.tension_state import TensionState, ConsequenceTest
from ..utils.topic_extractor import TopicExtractor
from ..utils.entailment_detector import EntailmentDetector, EntailmentType
from ..agents.consequence_test_generator import ConsequenceTestGenerator, ConsequenceTestContext
from ..utils.llm_client import LLMClient


@dataclass
class ProgressionConfig:
    """Configuration for progression control"""
    cycles_threshold: int = 2
    max_consequence_tests: int = 2
    synthesis_interval: int = 12
    entailment_required: bool = True
    enable_progression: bool = True
    topic_window: int = 2
    test_timeout_turns: int = 3
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ProgressionConfig':
        """Create config from dictionary"""
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})


@dataclass
class ProgressionState:
    """Current state of progression control"""
    tensions: Dict[Tuple[str, str], TensionState]
    turn_index: int = 0
    last_pivot_turn: int = -1
    recent_topics: List[Set[str]] = None
    current_tension: Optional[Tuple[str, str]] = None
    pending_tests: List[ConsequenceTest] = None
    
    def __post_init__(self):
        if self.recent_topics is None:
            self.recent_topics = []
        if self.pending_tests is None:
            self.pending_tests = []


class ProgressionController:
    """Main controller for discussion progression and orbit prevention"""
    
    def __init__(self, config: ProgressionConfig, llm_client: Optional[LLMClient] = None):
        """Initialize progression controller"""
        self.config = config
        self.llm_client = llm_client or LLMClient()
        
        # Core components
        self.topic_extractor = TopicExtractor()
        self.entailment_detector = EntailmentDetector()
        self.test_generator = ConsequenceTestGenerator(llm_client)
        
        # State
        self.state = ProgressionState(tensions={})
        
        # Metrics
        self.metrics = {
            "orbit_count": 0,
            "tests_injected": 0,
            "pivots_forced": 0,
            "entailments_detected": 0,
            "turns_processed": 0
        }
    
    async def process_turn(self, content: str, speaker: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a discussion turn and determine any interventions needed"""
        
        if not self.config.enable_progression:
            return {"interventions": [], "state_update": {}}
        
        self.state.turn_index += 1
        self.metrics["turns_processed"] += 1
        
        # Extract topics and detect tensions
        current_topics = self.topic_extractor.extract_topics(content)
        self.state.recent_topics.append(current_topics)
        
        # Keep only recent topic history
        if len(self.state.recent_topics) > self.config.topic_window + 1:
            self.state.recent_topics.pop(0)
        
        active_tensions = self.topic_extractor.detect_tensions(
            content, 
            self.state.recent_topics[:-1], 
            self.config.topic_window
        )
        
        # Detect entailments
        entailments = self.entailment_detector.detect(content)
        has_entailment = len(entailments) > 0
        
        if has_entailment:
            self.metrics["entailments_detected"] += 1
        
        # Update tension states
        interventions = []
        for tension in active_tensions:
            tension_state = self._get_or_create_tension_state(tension)
            
            # Check if this is a cycle without new entailment
            if not has_entailment:
                tension_state.increment_cycle()
                
                # Check if we need intervention
                if tension_state.should_inject_test():
                    test_intervention = await self._create_consequence_test(tension_state, content, context)
                    if test_intervention:
                        interventions.append(test_intervention)
                        self.metrics["tests_injected"] += 1
                
                elif tension_state.should_pivot():
                    pivot_intervention = await self._create_pivot_intervention(tension_state, context)
                    if pivot_intervention:
                        interventions.append(pivot_intervention)
                        self.metrics["pivots_forced"] += 1
                        self.state.last_pivot_turn = self.state.turn_index
            else:
                # Record entailment and reset cycles
                tension_state.record_entailment(self.state.turn_index)
        
        # Check for orbiting (multiple tensions saturated without progress)
        saturated_tensions = [ts for ts in self.state.tensions.values() if ts.is_saturated()]
        if len(saturated_tensions) > 1:
            self.metrics["orbit_count"] += 1
        
        # Process any pending consequence test responses
        await self._process_pending_tests(content, entailments)
        
        # Periodic synthesis check
        if (self.state.turn_index - self.state.last_pivot_turn > self.config.synthesis_interval and 
            self.state.last_pivot_turn != -1):
            synthesis_intervention = await self._create_synthesis_intervention(context)
            if synthesis_intervention:
                interventions.append(synthesis_intervention)
        
        return {
            "interventions": interventions,
            "state_update": {
                "turn_index": self.state.turn_index,
                "active_tensions": list(active_tensions),
                "current_topics": list(current_topics),
                "has_entailment": has_entailment,
                "entailment_types": [e.value for e in entailments],
                "saturated_tensions": len(saturated_tensions),
                "metrics": self.metrics.copy()
            }
        }
    
    def _get_or_create_tension_state(self, tension: Tuple[str, str]) -> TensionState:
        """Get or create tension state for a tension pair"""
        normalized_tension = tuple(sorted(tension))
        
        if normalized_tension not in self.state.tensions:
            self.state.tensions[normalized_tension] = TensionState(
                pair=normalized_tension,
                max_cycles=self.config.cycles_threshold,
                max_consequence_tests=self.config.max_consequence_tests
            )
        
        return self.state.tensions[normalized_tension]
    
    async def _create_consequence_test(self, tension_state: TensionState, content: str, 
                                     context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a consequence test intervention"""
        
        # Prepare context for test generation
        discussion_summary = context.get("episode_summary", "Ongoing philosophical discussion")
        previous_tests = [test.prompt for test in tension_state.consequence_tests]
        
        test_context = ConsequenceTestContext(
            tension=tension_state.pair,
            current_claim=content,
            discussion_summary=discussion_summary,
            turn_count=self.state.turn_index,
            previous_tests=previous_tests
        )
        
        try:
            test_prompt = await self.test_generator.generate_test(test_context)
            
            # Add to tension state
            consequence_test = tension_state.add_consequence_test(self.state.turn_index, test_prompt)
            self.state.pending_tests.append(consequence_test)
            
            return {
                "type": "consequence_test",
                "prompt": test_prompt,
                "tension": tension_state.pair,
                "turn": self.state.turn_index,
                "test_id": len(tension_state.consequence_tests) - 1
            }
            
        except Exception as e:
            print(f"Error generating consequence test: {e}")
            return None
    
    async def _create_pivot_intervention(self, tension_state: TensionState, 
                                       context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a pivot intervention when consequence tests fail"""
        
        failed_tests = [test.prompt for test in tension_state.consequence_tests 
                       if test.responded and not test.had_entailment]
        
        discussion_summary = context.get("episode_summary", "Ongoing philosophical discussion")
        
        try:
            synthesis_prompt = self.test_generator.generate_synthesis_prompt(
                tension_state.pair, failed_tests, discussion_summary
            )
            
            # Mark tension as needing pivot
            tension_state.mark_pivot_needed()
            
            return {
                "type": "pivot",
                "prompt": synthesis_prompt,
                "tension": tension_state.pair,
                "turn": self.state.turn_index,
                "failed_tests": len(failed_tests)
            }
            
        except Exception as e:
            print(f"Error generating pivot intervention: {e}")
            return None
    
    async def _create_synthesis_intervention(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create periodic synthesis intervention"""
        
        # Find most active tensions
        active_tensions = [(t, ts) for t, ts in self.state.tensions.items() 
                          if ts.cycles > 0 or ts.consequence_tests]
        
        if not active_tensions:
            return None
        
        # Use most cycled tension for synthesis
        most_active = max(active_tensions, key=lambda x: x[1].cycles + len(x[1].consequence_tests))
        tension, tension_state = most_active
        
        discussion_summary = context.get("episode_summary", "Ongoing philosophical discussion")
        
        try:
            synthesis_prompt = self.test_generator.generate_synthesis_prompt(
                tension, [], discussion_summary
            )
            
            return {
                "type": "synthesis",
                "prompt": synthesis_prompt,
                "tension": tension,
                "turn": self.state.turn_index,
                "reason": "periodic_synthesis"
            }
            
        except Exception as e:
            print(f"Error generating synthesis intervention: {e}")
            return None
    
    async def _process_pending_tests(self, content: str, entailments: Set[EntailmentType]):
        """Process responses to pending consequence tests"""
        
        # Check if current content responds to any pending tests
        for test in self.state.pending_tests[:]:  # Copy list to allow modification
            
            # Check if test has timed out
            if self.state.turn_index - test.turn > self.config.test_timeout_turns:
                test.responded = True
                test.had_entailment = False
                self.state.pending_tests.remove(test)
                continue
            
            # Check if content addresses the test
            validation = self.entailment_detector.validate_consequence_response(test.prompt, content)
            
            if validation["addresses_test"] or validation["has_entailments"]:
                test.responded = True
                test.had_entailment = validation["has_entailments"]
                self.state.pending_tests.remove(test)
                
                # Update corresponding tension state
                for tension_state in self.state.tensions.values():
                    if test in tension_state.consequence_tests:
                        if test.had_entailment:
                            tension_state.record_entailment(self.state.turn_index)
                        break
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        
        tension_statuses = {}
        for tension, state in self.state.tensions.items():
            tension_statuses[f"{tension[0]}/{tension[1]}"] = {
                "cycles": state.cycles,
                "max_cycles": state.max_cycles,
                "consequence_tests": len(state.consequence_tests),
                "last_entailment_turn": state.last_new_entailment_turn,
                "needs_pivot": state.needs_pivot,
                "is_saturated": state.is_saturated(),
                "should_inject_test": state.should_inject_test(),
                "should_pivot": state.should_pivot()
            }
        
        return {
            "config": {
                "cycles_threshold": self.config.cycles_threshold,
                "max_consequence_tests": self.config.max_consequence_tests,
                "entailment_required": self.config.entailment_required,
                "enable_progression": self.config.enable_progression
            },
            "state": {
                "turn_index": self.state.turn_index,
                "last_pivot_turn": self.state.last_pivot_turn,
                "current_tension": self.state.current_tension,
                "pending_tests": len(self.state.pending_tests),
                "recent_topics_count": len(self.state.recent_topics)
            },
            "tensions": tension_statuses,
            "metrics": self.metrics.copy()
        }
    
    def save_state(self, filepath: str):
        """Save progression state to file"""
        
        # Prepare serializable state
        serializable_state = {
            "tensions": {},
            "turn_index": self.state.turn_index,
            "last_pivot_turn": self.state.last_pivot_turn,
            "current_tension": self.state.current_tension,
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        # Convert tension states to dict
        for tension, state in self.state.tensions.items():
            serializable_state["tensions"][f"{tension[0]}|{tension[1]}"] = {
                "cycles": state.cycles,
                "last_new_entailment_turn": state.last_new_entailment_turn,
                "consequence_tests": [
                    {
                        "turn": test.turn,
                        "prompt": test.prompt,
                        "responded": test.responded,
                        "had_entailment": test.had_entailment,
                        "timestamp": test.timestamp.isoformat()
                    }
                    for test in state.consequence_tests
                ],
                "needs_pivot": state.needs_pivot
            }
        
        # Save to file
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(serializable_state, f, indent=2)
    
    def load_state(self, filepath: str):
        """Load progression state from file"""
        
        if not Path(filepath).exists():
            return
        
        with open(filepath, 'r') as f:
            saved_state = json.load(f)
        
        # Restore basic state
        self.state.turn_index = saved_state.get("turn_index", 0)
        self.state.last_pivot_turn = saved_state.get("last_pivot_turn", -1)
        self.state.current_tension = saved_state.get("current_tension")
        self.metrics.update(saved_state.get("metrics", {}))
        
        # Restore tension states
        self.state.tensions = {}
        for tension_key, tension_data in saved_state.get("tensions", {}).items():
            tension_parts = tension_key.split("|")
            if len(tension_parts) == 2:
                tension = tuple(tension_parts)
                
                # Recreate tension state
                state = TensionState(
                    pair=tension,
                    cycles=tension_data.get("cycles", 0),
                    last_new_entailment_turn=tension_data.get("last_new_entailment_turn", -1),
                    max_cycles=self.config.cycles_threshold,
                    max_consequence_tests=self.config.max_consequence_tests,
                    needs_pivot=tension_data.get("needs_pivot", False)
                )
                
                # Restore consequence tests
                for test_data in tension_data.get("consequence_tests", []):
                    test = ConsequenceTest(
                        turn=test_data["turn"],
                        prompt=test_data["prompt"],
                        responded=test_data.get("responded", False),
                        had_entailment=test_data.get("had_entailment", False),
                        timestamp=datetime.fromisoformat(test_data["timestamp"])
                    )
                    state.consequence_tests.append(test)
                
                self.state.tensions[tension] = state