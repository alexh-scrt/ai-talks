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
        min_aspects = self.aspects_required.get(self.target_depth, 3)
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
        min_aspects = self.aspects_required.get(self.target_depth, 3)
        min_exchanges = self.target_depth * 3
        
        aspect_progress = min(1.0, len(aspects_covered) / min_aspects)
        exchange_progress = min(1.0, exchange_count / min_exchanges)
        
        return (aspect_progress + exchange_progress) / 2