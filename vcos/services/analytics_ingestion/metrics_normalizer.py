"""
Analytics Ingestion - Metrics Normalizer
Normalize different platform metrics to common format
"""

from typing import Dict
from shared.feature_definitions.platform_signal_mapper import normalize_platform_signal
import logging

logger = logging.getLogger(__name__)

def normalize_metrics(platform_data: Dict, platform: str) -> Dict:
    """
    Normalize platform-specific metrics to common format
    
    Args:
        platform_data: Raw platform metrics
        platform: Platform name
        
    Returns:
        Normalized metrics dictionary
    """
    # Use platform signal mapper for proper normalization
    normalized_signal = normalize_platform_signal(platform, platform_data)
    
    # Convert to metrics format
    return {
        "retention_3s": normalized_signal.stop_rate,
        "retention_50pct": normalized_signal.mid_hold,
        "completion_rate": normalized_signal.completion,
        "shares_per_1k": normalized_signal.share_velocity,
        "comments_per_1k": normalized_signal.comment_velocity,
        "view_velocity": normalized_signal.view_velocity,
        "save_rate": normalized_signal.save_rate,
        "views": platform_data.get("views", 0),
        "platform": platform
    }
