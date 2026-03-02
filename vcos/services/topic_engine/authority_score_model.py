"""
Topic Engine - Authority Score Model
Calculates weighted authority score for clusters
"""

from services.topic_engine.topic_db import get_cluster_metrics
import logging

logger = logging.getLogger(__name__)

# Weight configuration for scoring
WEIGHTS = {
    "retention": 0.5,
    "shares": 0.3,
    "repeat_lift": 0.2
}

def compute_cluster_score(cluster_name: str) -> float:
    """
    Calculate weighted authority score for a cluster
    
    Args:
        cluster_name: Name of the cluster
        
    Returns:
        Authority score (0.0 to 1.0+)
    """
    try:
        metrics = get_cluster_metrics(cluster_name)
        
        # Extract metrics with defaults
        retention = metrics.get("avg_retention", 0.5)
        shares = metrics.get("avg_shares_per_1k", 0.1)
        repeat_lift = metrics.get("repeat_watch_lift", 1.0)
        
        # Normalize shares (assuming 0.1 is baseline)
        normalized_shares = min(shares / 0.1, 1.0) if shares > 0 else 0.0
        
        # Calculate weighted score
        score = (
            retention * WEIGHTS["retention"] +
            normalized_shares * WEIGHTS["shares"] +
            (repeat_lift - 1.0) * WEIGHTS["repeat_lift"]
        )
        
        # Ensure score is at least 0
        score = max(0.0, score)
        
        logger.debug(f"Cluster {cluster_name} score: {score} (retention={retention}, shares={shares}, lift={repeat_lift})")
        
        return score
        
    except Exception as e:
        logger.warning(f"Error computing score for {cluster_name}: {e}, using default")
        # Return default score if cluster has no data
        return 0.3

def update_cluster_metrics(cluster_name: str, metrics: dict):
    """Update cluster metrics (called by feedback trainer)"""
    from services.topic_engine.topic_db import update_cluster_metrics
    update_cluster_metrics(cluster_name, metrics)
    logger.info(f"Updated metrics for cluster: {cluster_name}")
