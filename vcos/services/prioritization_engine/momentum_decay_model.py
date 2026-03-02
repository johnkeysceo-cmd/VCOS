"""
Prioritization Engine - Momentum Decay Model
Prevents topic over-saturation by decaying priority over time
"""

from typing import Dict
from datetime import datetime, timedelta
import math
import logging

logger = logging.getLogger(__name__)

def compute_momentum_decay(
    base_score: float,
    last_used: datetime,
    decay_half_life_days: int = 7
) -> float:
    """
    Compute momentum decay for a topic/cluster
    
    Args:
        base_score: Base priority score
        last_used: When this topic was last used
        decay_half_life_days: Days for score to halve
        
    Returns:
        Decayed score
    """
    if not last_used:
        return base_score
    
    # Calculate days since last use
    days_since = (datetime.now() - last_used).days
    
    if days_since <= 0:
        return base_score
    
    # Exponential decay
    decay_factor = math.pow(0.5, days_since / decay_half_life_days)
    
    decayed_score = base_score * decay_factor
    
    logger.debug(
        f"Momentum decay: {base_score:.2f} -> {decayed_score:.2f} "
        f"({days_since} days, half-life: {decay_half_life_days}d)"
    )
    
    return decayed_score

def apply_decay_to_clusters(cluster_scores: Dict[str, float], last_used: Dict[str, datetime]) -> Dict[str, float]:
    """
    Apply decay to cluster scores
    
    Args:
        cluster_scores: Base cluster scores
        last_used: Last usage timestamps per cluster
        
    Returns:
        Decayed cluster scores
    """
    decayed = {}
    
    for cluster, score in cluster_scores.items():
        last_used_time = last_used.get(cluster)
        decayed[cluster] = compute_momentum_decay(score, last_used_time)
    
    return decayed
