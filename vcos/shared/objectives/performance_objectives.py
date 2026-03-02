"""
Performance Objectives
Formal definitions of what each service optimizes
"""

from shared.objectives.viral_score import ViralScore, VIRAL_SCORE_WEIGHTS
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Service-specific objectives
SERVICE_OBJECTIVES = {
    "hook_engine": {
        "primary": "maximize_ctr",
        "secondary": "maximize_curiosity",
        "target": 0.8  # Target CTR score
    },
    "retention_optimizer": {
        "primary": "maximize_retention_50pct",
        "secondary": "maximize_completion",
        "target": 0.7  # Target 50% retention
    },
    "variant_generator": {
        "primary": "maximize_viral_score_variance",
        "secondary": "minimize_correlation",
        "target": 0.1  # Target variance in viral scores
    },
    "topic_engine": {
        "primary": "maximize_cluster_authority",
        "secondary": "maintain_identity_consistency",
        "target": 0.8  # Target authority score
    }
}

def get_service_objective(service_name: str) -> Dict:
    """Get performance objective for a service"""
    return SERVICE_OBJECTIVES.get(service_name, {
        "primary": "maximize_viral_score",
        "target": 0.5
    })

def evaluate_service_performance(service_name: str, metrics: Dict) -> float:
    """
    Evaluate how well a service is meeting its objective
    
    Args:
        service_name: Service name
        metrics: Performance metrics
        
    Returns:
        Performance score (0.0 to 1.0)
    """
    objective = get_service_objective(service_name)
    primary = objective["primary"]
    target = objective["target"]
    
    if primary == "maximize_ctr":
        actual = metrics.get("ctr_score", 0.0)
    elif primary == "maximize_retention_50pct":
        actual = metrics.get("retention_50pct", 0.0)
    elif primary == "maximize_viral_score":
        viral_score = ViralScore(
            retention_50pct=metrics.get("retention_50pct", 0.0),
            completion_rate=metrics.get("completion_rate", 0.0),
            shares_per_1k=metrics.get("shares_per_1k", 0.0),
            comment_velocity=metrics.get("comment_velocity", 0.0),
            view_velocity=metrics.get("view_velocity", 0.0)
        )
        actual = viral_score.compute()
    else:
        actual = 0.5
    
    # Performance = how close to target
    performance = min(1.0, actual / target) if target > 0 else 0.0
    
    return performance
