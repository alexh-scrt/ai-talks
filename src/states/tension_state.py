from dataclasses import dataclass
from typing import Tuple, List
from datetime import datetime


@dataclass
class ConsequenceTest:
    """Represents a consequence test injected for a tension"""
    turn: int
    prompt: str
    responded: bool = False
    had_entailment: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TensionState:
    """Tracks cycles on a specific philosophical tension with consequence test support"""
    pair: Tuple[str, str]  # e.g., ('necessity', 'contingency')
    cycles: int = 0
    last_new_entailment_turn: int = -1
    max_cycles: int = 2
    consequence_tests: List[ConsequenceTest] = None
    last_consequence_turn: int = -1
    max_consequence_tests: int = 2
    needs_pivot: bool = False
    
    def __post_init__(self):
        if self.consequence_tests is None:
            self.consequence_tests = []
    
    def can_continue(self) -> bool:
        """Check if tension can continue being explored"""
        return self.cycles < self.max_cycles and not self.needs_pivot
    
    def increment_cycle(self):
        """Increment cycle count"""
        self.cycles += 1
    
    def reset(self):
        """Reset cycle count and consequence tests"""
        self.cycles = 0
        self.consequence_tests.clear()
        self.last_consequence_turn = -1
        self.needs_pivot = False
    
    def record_entailment(self, turn: int):
        """Record when a new entailment was found for this tension"""
        self.last_new_entailment_turn = turn
        # Reset cycles since we have new content
        self.cycles = 0
        self.needs_pivot = False
    
    def is_saturated(self) -> bool:
        """Check if tension is saturated (cycles >= threshold without new entailment)"""
        return self.cycles >= self.max_cycles
    
    def add_consequence_test(self, turn: int, prompt: str) -> ConsequenceTest:
        """Add a consequence test for this tension"""
        test = ConsequenceTest(turn=turn, prompt=prompt)
        self.consequence_tests.append(test)
        self.last_consequence_turn = turn
        return test
    
    def get_recent_tests(self, window: int = 8) -> List[ConsequenceTest]:
        """Get consequence tests within the recent window"""
        return [test for test in self.consequence_tests 
                if test.turn >= max(0, self.last_consequence_turn - window)]
    
    def count_failed_tests(self, window: int = 8) -> int:
        """Count consequence tests that didn't produce new entailments"""
        recent_tests = self.get_recent_tests(window)
        return sum(1 for test in recent_tests if test.responded and not test.had_entailment)
    
    def should_inject_test(self) -> bool:
        """Check if a consequence test should be injected"""
        return (self.is_saturated() and 
                len(self.consequence_tests) < self.max_consequence_tests and
                not self.needs_pivot)
    
    def should_pivot(self) -> bool:
        """Check if we should pivot away from this tension"""
        if self.needs_pivot:
            return True
        
        failed_tests = self.count_failed_tests()
        return failed_tests >= self.max_consequence_tests
    
    def mark_pivot_needed(self):
        """Mark that this tension needs to pivot"""
        self.needs_pivot = True
    
    def get_status_summary(self) -> str:
        """Get a human-readable status summary"""
        status_parts = [f"cycles:{self.cycles}/{self.max_cycles}"]
        
        if self.consequence_tests:
            failed = self.count_failed_tests()
            status_parts.append(f"tests:{len(self.consequence_tests)}")
            if failed > 0:
                status_parts.append(f"failed:{failed}")
        
        if self.needs_pivot:
            status_parts.append("PIVOT_NEEDED")
        elif self.is_saturated():
            status_parts.append("SATURATED")
        
        return f"TensionState({self.pair[0]}/{self.pair[1]}, {', '.join(status_parts)})"
    
    def __repr__(self) -> str:
        return self.get_status_summary()