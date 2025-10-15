from dataclasses import dataclass
from typing import Tuple


@dataclass
class TensionState:
    """Tracks cycles on a specific philosophical tension"""
    pair: Tuple[str, str]  # e.g., ('necessity', 'contingency')
    cycles: int = 0
    last_new_entailment_turn: int = -1
    max_cycles: int = 2
    
    def can_continue(self) -> bool:
        """Check if tension can continue being explored"""
        return self.cycles < self.max_cycles
    
    def increment_cycle(self):
        """Increment cycle count"""
        self.cycles += 1
    
    def reset(self):
        """Reset cycle count"""
        self.cycles = 0
    
    def record_entailment(self, turn: int):
        """Record when a new entailment was found for this tension"""
        self.last_new_entailment_turn = turn
    
    def __repr__(self) -> str:
        return f"TensionState({self.pair}, {self.cycles}/{self.max_cycles})"