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
        last_exchange: str = ""
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
        
        # Criterion 5: Low novelty (repetition)
        if group_state.novelty_score < 0.2 and exchange_count > self.target_depth * 4:
            return True, "Discussion becoming repetitive"
        
        return False, "Continue dialogue"