"""
Topic Engine - Cluster Manager
Tracks which topic cluster performs best
"""

from services.topic_engine.authority_score_model import compute_cluster_score
from services.topic_engine.topic_db import get_cluster_metrics
import logging

logger = logging.getLogger(__name__)

# Define available clusters
AVAILABLE_CLUSTERS = [
    "rebuild_tools",
    "automation",
    "ai_tools",
    "replacement",
    "challenge",
    "tutorial"
]

def get_top_cluster() -> str:
    """
    Get the top performing cluster based on authority scores
    
    Returns:
        Name of the top cluster
    """
    cluster_scores = {}
    
    for cluster in AVAILABLE_CLUSTERS:
        score = compute_cluster_score(cluster)
        cluster_scores[cluster] = score
        logger.debug(f"Cluster {cluster} score: {score}")
    
    top_cluster = max(cluster_scores, key=cluster_scores.get)
    logger.info(f"Top cluster selected: {top_cluster} (score: {cluster_scores[top_cluster]})")
    
    return top_cluster

def get_all_cluster_scores() -> dict:
    """Get scores for all clusters"""
    return {
        cluster: compute_cluster_score(cluster)
        for cluster in AVAILABLE_CLUSTERS
    }

def update_cluster_performance(cluster: str, performance_data: dict):
    """Update cluster performance data"""
    from services.topic_engine.topic_db import update_cluster_metrics
    update_cluster_metrics(cluster, performance_data)
    logger.info(f"Updated performance for cluster: {cluster}")
