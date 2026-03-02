"""
Identity Model - Topic Drift Detector
Detects when content is drifting from established identity
"""

from services.identity_model.identity_tracker import identity_tracker
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def detect_topic_drift(new_topic: str, new_cluster: str) -> Dict:
    """
    Detect if new topic/cluster represents drift from identity
    
    Args:
        new_topic: New topic text
        new_cluster: New cluster name
        
    Returns:
        Drift detection result
    """
    report = identity_tracker.get_identity_report()
    
    dominant_cluster = report.get("dominant_cluster")
    consistency = report.get("consistency_score", 0.5)
    entropy = report.get("topic_entropy", 0.5)
    
    # Check if new cluster matches dominant
    is_drift = dominant_cluster and new_cluster != dominant_cluster
    
    # Calculate drift severity
    if is_drift:
        # Check how different this is
        cluster_dist = report.get("cluster_distribution", {})
        new_cluster_frequency = cluster_dist.get(new_cluster, 0) / max(sum(cluster_dist.values()), 1)
        
        drift_severity = 1.0 - new_cluster_frequency
    else:
        drift_severity = 0.0
    
    # High entropy + drift = concerning
    drift_risk = (drift_severity * 0.6) + (entropy * 0.4)
    
    return {
        "is_drift": is_drift,
        "drift_severity": drift_severity,
        "drift_risk": drift_risk,
        "recommendation": "proceed" if drift_risk < 0.5 else "caution" if drift_risk < 0.7 else "avoid"
    }
