"""
Analytics Ingestion - Velocity Tracker
Tracks view velocity (views per time period)
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

def compute_velocity(views_first_30m: int) -> float:
    """
    Compute view velocity (views per minute)
    
    Args:
        views_first_30m: Views in first 30 minutes
        
    Returns:
        Velocity (views per minute)
    """
    return views_first_30m / 30.0 if views_first_30m > 0 else 0.0

def track_velocity_over_time(views_data: Dict) -> Dict:
    """
    Track velocity over different time windows
    
    Args:
        views_data: Dictionary with views at different timestamps
        
    Returns:
        Velocity metrics
    """
    velocities = {}
    
    if "views_15m" in views_data:
        velocities["15m"] = views_data["views_15m"] / 15.0
    
    if "views_30m" in views_data:
        velocities["30m"] = views_data["views_30m"] / 30.0
    
    if "views_1h" in views_data:
        velocities["1h"] = views_data["views_1h"] / 60.0
    
    if "views_24h" in views_data:
        velocities["24h"] = views_data["views_24h"] / (24 * 60.0)
    
    return velocities
