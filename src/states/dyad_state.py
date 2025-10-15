from dataclasses import dataclass
from typing import Tuple


@dataclass
class DyadState:
    """Tracks conversation volleys between two agents"""
    pair: Tuple[str, str]
    volleys_used: int = 0
    max_volleys: int = 2
    
    def can_continue(self) -> bool:
        """Check if dyad can continue conversation"""
        return self.volleys_used < self.max_volleys
    
    def increment(self):
        """Increment volley count"""
        self.volleys_used += 1
    
    def reset(self):
        """Reset volley count"""
        self.volleys_used = 0
    
    def __repr__(self) -> str:
        return f"DyadState({self.pair}, {self.volleys_used}/{self.max_volleys})"