import numpy as np
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def plot_meaning_ridge(
    S: float,
    A: float,
    D: float,
    S_star: float = 0.6,
    sigma: float = 0.18,
    alpha: float = 1.0,
    beta: float = 1.2,
    output_path: Optional[str] = None
) -> str:
    """
    Generate ridge plot showing meaning landscape
    
    Args:
        S: Current structure value
        A: Current agency value
        D: Current dependence value
        S_star: Optimal structure target
        sigma: Ridge width
        alpha: Agency curvature
        beta: Dependence penalty
        output_path: Optional path to save figure
        
    Returns: Path to saved figure
    """
    try:
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Left plot: S-A ridge with current position
        S_grid = np.linspace(0, 1, 100)
        A_grid = np.linspace(0, 1, 100)
        S_mesh, A_mesh = np.meshgrid(S_grid, A_grid)
        
        # Compute M for grid
        M_mesh = (A_mesh ** alpha) * np.exp(-((S_mesh - S_star) ** 2) / (2 * sigma ** 2)) * np.exp(-beta * D)
        
        contour = ax1.contourf(S_mesh, A_mesh, M_mesh, levels=20, cmap='viridis')
        ax1.scatter([S], [A], color='red', s=200, marker='*', edgecolors='white', linewidths=2, zorder=10)
        ax1.set_xlabel('Structure (S)', fontsize=12)
        ax1.set_ylabel('Agency (A)', fontsize=12)
        ax1.set_title(f'Meaning Ridge (D={D:.2f})', fontsize=14)
        ax1.grid(True, alpha=0.3)
        plt.colorbar(contour, ax=ax1, label='M')
        
        # Add optimal structure line
        ax1.axvline(S_star, color='yellow', linestyle='--', alpha=0.7, label=f'S*={S_star}')
        ax1.legend()
        
        # Right plot: Dependence gauge
        ax2.barh(['D'], [D], color='coral', height=0.3)
        ax2.set_xlim(0, 1)
        ax2.set_xlabel('Dependence (D)', fontsize=12)
        ax2.set_title('External Control', fontsize=14)
        ax2.axvline(0.3, color='green', linestyle='--', alpha=0.5, label='Low')
        ax2.axvline(0.6, color='orange', linestyle='--', alpha=0.5, label='Medium')
        ax2.axvline(0.8, color='red', linestyle='--', alpha=0.5, label='High')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        if output_path is None:
            output_dir = Path("outputs/codas/figs")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"ridge_{S:.2f}_{A:.2f}_{D:.2f}.png"
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 Meaning ridge plot saved to {output_path}")
        return str(output_path)
        
    except ImportError:
        logger.warning("matplotlib not available, skipping visualization")
        return ""
    except Exception as e:
        logger.error(f"Failed to generate ridge plot: {e}")
        return ""


def plot_meaning_sparkline(
    M_history: list,
    output_path: Optional[str] = None
) -> str:
    """
    Generate sparkline showing meaning score over time
    
    Args:
        M_history: List of meaning scores over time
        output_path: Optional path to save figure
        
    Returns: Path to saved figure
    """
    try:
        import matplotlib.pyplot as plt
        
        if len(M_history) < 2:
            logger.warning("Not enough data points for sparkline")
            return ""
        
        fig, ax = plt.subplots(1, 1, figsize=(6, 2))
        
        turns = list(range(len(M_history)))
        ax.plot(turns, M_history, 'b-', linewidth=2, marker='o', markersize=3)
        ax.fill_between(turns, M_history, alpha=0.3)
        
        ax.set_xlabel('Turn', fontsize=10)
        ax.set_ylabel('M', fontsize=10)
        ax.set_title('Meaning Score Evolution', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1)
        
        # Highlight trend
        if M_history[-1] > M_history[0]:
            ax.text(0.7, 0.9, '↗ Rising', transform=ax.transAxes, color='green', fontweight='bold')
        elif M_history[-1] < M_history[0]:
            ax.text(0.7, 0.9, '↘ Falling', transform=ax.transAxes, color='red', fontweight='bold')
        else:
            ax.text(0.7, 0.9, '→ Stable', transform=ax.transAxes, color='blue', fontweight='bold')
        
        plt.tight_layout()
        
        # Save figure
        if output_path is None:
            output_dir = Path("outputs/codas/figs")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"sparkline_{len(M_history)}_turns.png"
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📈 Meaning sparkline saved to {output_path}")
        return str(output_path)
        
    except ImportError:
        logger.warning("matplotlib not available, skipping sparkline")
        return ""
    except Exception as e:
        logger.error(f"Failed to generate sparkline: {e}")
        return ""


def create_meaning_dashboard(
    S: float,
    A: float,
    D: float,
    M_history: Optional[list] = None,
    S_star: float = 0.6,
    sigma: float = 0.18,
    alpha: float = 1.0,
    beta: float = 1.2,
    output_path: Optional[str] = None
) -> str:
    """
    Create comprehensive meaning dashboard with multiple visualizations
    
    Args:
        S, A, D: Current signal values
        M_history: Historical meaning scores
        S_star, sigma, alpha, beta: Model parameters
        output_path: Optional path to save figure
        
    Returns: Path to saved dashboard figure
    """
    try:
        import matplotlib.pyplot as plt
        
        # Calculate current meaning
        M_current = (A ** alpha) * np.exp(-((S - S_star) ** 2) / (2 * sigma ** 2)) * np.exp(-beta * D)
        
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Ridge plot (top left)
        ax1 = plt.subplot(2, 3, 1)
        S_grid = np.linspace(0, 1, 50)
        A_grid = np.linspace(0, 1, 50)
        S_mesh, A_mesh = np.meshgrid(S_grid, A_grid)
        M_mesh = (A_mesh ** alpha) * np.exp(-((S_mesh - S_star) ** 2) / (2 * sigma ** 2)) * np.exp(-beta * D)
        
        contour = ax1.contourf(S_mesh, A_mesh, M_mesh, levels=15, cmap='viridis')
        ax1.scatter([S], [A], color='red', s=150, marker='*', edgecolors='white', linewidths=2)
        ax1.axvline(S_star, color='yellow', linestyle='--', alpha=0.7)
        ax1.set_xlabel('Structure (S)')
        ax1.set_ylabel('Agency (A)')
        ax1.set_title('Meaning Ridge')
        plt.colorbar(contour, ax=ax1, shrink=0.8)
        
        # 2. Signal bars (top middle)
        ax2 = plt.subplot(2, 3, 2)
        signals = ['S', 'A', 'D']
        values = [S, A, D]
        colors = ['blue', 'green', 'red']
        bars = ax2.bar(signals, values, color=colors, alpha=0.7)
        ax2.set_ylim(0, 1)
        ax2.set_title('Current Signals')
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.2f}', ha='center', va='bottom')
        
        # 3. Meaning score gauge (top right)
        ax3 = plt.subplot(2, 3, 3)
        theta = np.linspace(0, np.pi, 100)
        r = np.ones_like(theta)
        ax3 = plt.subplot(2, 3, 3, projection='polar')
        ax3.fill_between(theta, 0, r, alpha=0.3, color='lightgray')
        
        # Color code the gauge
        M_angle = M_current * np.pi
        ax3.fill_between(theta[theta <= M_angle], 0, r[theta <= M_angle], 
                        alpha=0.8, color='green' if M_current > 0.6 else 'orange' if M_current > 0.3 else 'red')
        
        ax3.set_ylim(0, 1)
        ax3.set_title(f'Meaning Score: {M_current:.3f}', pad=20)
        ax3.set_theta_zero_location('W')
        ax3.set_theta_direction(1)
        ax3.set_thetagrids([0, 90, 180], ['1.0', '0.5', '0.0'])
        
        # 4. Historical trend (bottom left)
        if M_history and len(M_history) > 1:
            ax4 = plt.subplot(2, 3, 4)
            turns = list(range(len(M_history)))
            ax4.plot(turns, M_history, 'b-', linewidth=2, marker='o', markersize=4)
            ax4.fill_between(turns, M_history, alpha=0.3)
            ax4.set_xlabel('Turn')
            ax4.set_ylabel('Meaning Score')
            ax4.set_title('Historical Trend')
            ax4.grid(True, alpha=0.3)
            ax4.set_ylim(0, 1)
        else:
            ax4 = plt.subplot(2, 3, 4)
            ax4.text(0.5, 0.5, 'No historical data', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Historical Trend')
        
        # 5. Model parameters (bottom middle)
        ax5 = plt.subplot(2, 3, 5)
        params = [f'S* = {S_star}', f'σ = {sigma}', f'α = {alpha}', f'β = {beta}']
        ax5.text(0.1, 0.8, 'Model Parameters:', fontsize=12, fontweight='bold', transform=ax5.transAxes)
        for i, param in enumerate(params):
            ax5.text(0.1, 0.6 - i*0.15, param, fontsize=10, transform=ax5.transAxes)
        ax5.set_xlim(0, 1)
        ax5.set_ylim(0, 1)
        ax5.axis('off')
        
        # 6. Equation (bottom right)
        ax6 = plt.subplot(2, 3, 6)
        equation = r'$M = A^α \cdot \exp\left(-\frac{(S-S^*)^2}{2σ^2}\right) \cdot \exp(-βD)$'
        ax6.text(0.5, 0.6, equation, ha='center', va='center', fontsize=12, transform=ax6.transAxes)
        ax6.text(0.5, 0.3, f'Current M = {M_current:.3f}', ha='center', va='center', 
                fontsize=14, fontweight='bold', transform=ax6.transAxes)
        ax6.set_xlim(0, 1)
        ax6.set_ylim(0, 1)
        ax6.axis('off')
        ax6.set_title('Meaning Model')
        
        plt.suptitle('Cognitive Coda - Meaning Analysis Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        
        # Save dashboard
        if output_path is None:
            output_dir = Path("outputs/codas/figs")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"dashboard_{S:.2f}_{A:.2f}_{D:.2f}.png"
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 Meaning dashboard saved to {output_path}")
        return str(output_path)
        
    except ImportError:
        logger.warning("matplotlib not available, skipping dashboard")
        return ""
    except Exception as e:
        logger.error(f"Failed to generate dashboard: {e}")
        return ""