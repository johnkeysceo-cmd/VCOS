"""
Prioritization Engine - Cluster Scoring
Scores clusters for prioritization
"""

from services.topic_engine.cluster_manager import get_all_cluster_scores
import logging

logger = logging.getLogger(__name__)

def score_clusters() -> dict:
    """Get scores for all clusters"""
    return get_all_cluster_scores()
