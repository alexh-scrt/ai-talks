import numpy as np
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class MeaningModel:
    """
    Computes meaning score M(S, A, D) using ridge model:
    
    M = A^α · exp(-(S-S*)²/(2σ²)) · exp(-βD)
    
    Where:
    - S: Structure (0-1)
    - A: Agency (0-1)  
    - D: Dependence (0-1)
    - S*: Optimal structure target (default 0.6)
    - σ: Ridge width (default 0.18)
    - α: Agency curvature (default 1.0)
    - β: Dependence penalty (default 1.2)
    """
    
    def __init__(
        self,
        S_star: float = 0.6,
        sigma: float = 0.18,
        alpha: float = 1.0,
        beta: float = 1.2
    ):
        """Initialize meaning model with parameters"""
        self.S_star = S_star
        self.sigma = sigma
        self.alpha = alpha
        self.beta = beta
        
        # Validate parameters
        assert 0 < sigma <= 0.5, f"σ must be in (0, 0.5], got {sigma}"
        assert 0 <= beta <= 3, f"β must be in [0, 3], got {beta}"
        assert 0 <= S_star <= 1, f"S* must be in [0, 1], got {S_star}"
        assert alpha >= 0, f"α must be non-negative, got {alpha}"
        
        logger.info(f"MeaningModel initialized: S*={S_star}, σ={sigma}, α={alpha}, β={beta}")
    
    def compute(self, S: float, A: float, D: float) -> float:
        """
        Compute meaning score M(S, A, D)
        
        Args:
            S: Structure signal [0,1]
            A: Agency signal [0,1]
            D: Dependence signal [0,1]
            
        Returns:
            M: Meaning score [0,1]
        """
        # Validate inputs
        assert 0 <= S <= 1, f"S must be in [0,1], got {S}"
        assert 0 <= A <= 1, f"A must be in [0,1], got {A}"
        assert 0 <= D <= 1, f"D must be in [0,1], got {D}"
        
        # Agency gain
        agency_term = A ** self.alpha
        
        # Structure ridge (Gaussian centered at S*)
        structure_term = np.exp(-((S - self.S_star) ** 2) / (2 * self.sigma ** 2))
        
        # Dependence penalty
        dependence_term = np.exp(-self.beta * D)
        
        # Combined meaning
        M = agency_term * structure_term * dependence_term
        
        return float(np.clip(M, 0, 1))
    
    def get_interpretation(self, S: float, A: float, D: float) -> str:
        """
        Generate verbal axiom based on signal positions
        
        Returns: Human-readable interpretation string
        """
        # Structure interpretation
        if S < self.S_star - self.sigma:
            structure_clause = "Meaning grows by **adding form**: agency is present, but structure is too loose."
        elif abs(S - self.S_star) <= self.sigma:
            structure_clause = "Meaning **peaks where agency strains against near-optimal structure**."
        else:  # S > S_star + sigma
            structure_clause = "Meaning is **over-constrained**: loosen structure to give agency room to work."
        
        # Dependence interpretation
        if D < 0.3:
            dependence_clause = "External dependence is **low**—guard against drift."
        elif D < 0.6:
            dependence_clause = "External dependence is **medium**—maintain balance."
        else:
            dependence_clause = "External dependence is **high**—guard against fatalism."
        
        return f"{structure_clause} {dependence_clause}"
    
    def get_maxim(self, M_current: float, M_previous: Optional[float] = None) -> str:
        """
        Select maxim based on momentum
        
        Args:
            M_current: Current meaning score
            M_previous: Previous meaning score (if available)
            
        Returns: Memorable maxim
        """
        if M_previous is None:
            return "**Hold the ridge: less noise, not more rules.**"
        
        delta = M_current - M_previous
        
        if delta > 0.05:
            return "**Meaning lives at the ridge between chaos and command.**"
        elif delta < -0.05:
            return "**Loosen the code; let choice bite.**"
        else:
            return "**Hold the ridge: less noise, not more rules.**"
    
    def recommend_actions(self, components: Dict[str, float]) -> List[str]:
        """
        Generate actionable recommendations based on weak signals
        
        Args:
            components: Dict of all S/A/D component signals
            
        Returns: List of concrete next-step recommendations
        """
        actions = []
        
        # Structure recommendations
        if components.get('S_cite', 0) < 0.3:
            actions.append("Ground the next claim with one source citation.")
        
        if components.get('S_logic', 0) < 0.4:
            actions.append("Add explicit logical connectors (if-then, therefore).")
        
        if components.get('S_consis', 0) < 0.3:
            actions.append("Support claims with reasoning or evidence.")
        
        if components.get('S_focus', 0) < 0.4:
            actions.append("Return to the central topic or connect ideas more clearly.")
        
        # Agency recommendations
        if components.get('A_ought', 0) < 0.3:
            actions.append("Introduce a normative claim (should/ought/must).")
        
        if components.get('A_decis', 0) < 0.3:
            actions.append("Make a clear decision or commitment statement.")
        
        if components.get('A_conse', 0) < 0.4:
            actions.append("Propose a testable consequence in the next turn.")
        
        if components.get('A_stanc', 0) < 0.3:
            actions.append("Take a clear stance rather than hedging.")
        
        # Dependence recommendations  
        if components.get('D_rules', 0) > 0.6:
            actions.append("Reduce moderator constraints for 2-3 turns.")
        
        if components.get('D_nonvar', 0) > 0.7:
            actions.append("Introduce a novel perspective or counterexample.")
        
        if components.get('D_sim', 0) > 0.5:
            actions.append("Focus on participant agency rather than external forces.")
        
        return actions[:3]  # Limit to top 3 actions
    
    def get_equation_string(self) -> str:
        """Get the mathematical equation as a string"""
        return "M = A^α · exp(−(S−S*)²/(2σ²)) · exp(−βD)"
    
    def get_parameters_dict(self) -> Dict[str, float]:
        """Get model parameters as dictionary"""
        return {
            'alpha': self.alpha,
            'beta': self.beta,
            'S_star': self.S_star,
            'sigma': self.sigma
        }
    
    def format_numbers(self, S: float, A: float, D: float, M: float) -> str:
        """Format the numerical values for display"""
        return f"A={A:.2f}, S={S:.2f}, D={D:.2f}, α={self.alpha}, S*={self.S_star}, σ={self.sigma}, β={self.beta} → M={M:.2f}"
    
    def explain_ridge_concept(self) -> str:
        """Explain the ridge concept for educational purposes"""
        return (
            f"The meaning model uses a 'ridge' function where structure has an optimal value of {self.S_star}. "
            f"Too little structure (S < {self.S_star - self.sigma:.2f}) creates chaos; "
            f"too much structure (S > {self.S_star + self.sigma:.2f}) creates rigidity. "
            f"Agency multiplies meaning linearly, while dependence diminishes it exponentially."
        )