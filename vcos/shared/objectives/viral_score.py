"""
Core Performance Objective - Viral Score
Formally defines what "good" means across the entire system
"""

from dataclasses import dataclass
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Canonical viral score weights
VIRAL_SCORE_WEIGHTS = {
    "retention_50pct": 0.35,  # 50% retention is strongest signal
    "completion_rate": 0.25,  # Completion = high engagement
    "shares_per_1k": 0.20,    # Shares = viral potential
    "comment_velocity": 0.10, # Comments = engagement depth
    "view_velocity": 0.10     # Velocity = algorithm favor
}

@dataclass
class ViralScore:
    """Canonical viral score definition"""
    retention_50pct: float
    completion_rate: float
    shares_per_1k: float
    comment_velocity: float  # Comments per 1k views per hour
    view_velocity: float     # Views per minute in first 30min
    
    def compute(self) -> float:
        """
        Compute composite viral score
        
        Returns:
            Viral score (0.0 to 1.0+)
        """
        score = (
            self.retention_50pct * VIRAL_SCORE_WEIGHTS["retention_50pct"] +
            self.completion_rate * VIRAL_SCORE_WEIGHTS["completion_rate"] +
            min(self.shares_per_1k / 10.0, 1.0) * VIRAL_SCORE_WEIGHTS["shares_per_1k"] +
            min(self.comment_velocity / 5.0, 1.0) * VIRAL_SCORE_WEIGHTS["comment_velocity"] +
            min(self.view_velocity / 100.0, 1.0) * VIRAL_SCORE_WEIGHTS["view_velocity"]
        )
        
        return min(1.0, max(0.0, score))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "retention_50pct": self.retention_50pct,
            "completion_rate": self.completion_rate,
            "shares_per_1k": self.shares_per_1k,
            "comment_velocity": self.comment_velocity,
            "view_velocity": self.view_velocity,
            "viral_score": self.compute()
        }

def compute_viral_score_from_metrics(metrics: Dict) -> ViralScore:
    """
    Compute viral score from analytics metrics
    
    Args:
        metrics: Dictionary with analytics data
        
    Returns:
        ViralScore object
    """
    return ViralScore(
        retention_50pct=metrics.get("retention_50pct", 0.0),
        completion_rate=metrics.get("completion_rate", 0.0),
        shares_per_1k=metrics.get("shares_per_1k", 0.0),
        comment_velocity=metrics.get("comment_velocity", 0.0),
        view_velocity=metrics.get("view_velocity", 0.0)
    )
