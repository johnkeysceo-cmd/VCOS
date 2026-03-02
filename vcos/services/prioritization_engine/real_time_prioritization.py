"""
Prioritization Engine - Real-Time Prioritization
Incorporates real-time analytics for dynamic prioritization
"""

from services.prioritization_engine.momentum_predictor import predict_momentum
from services.analytics_ingestion.real_time_analytics import real_time_adapter
from services.topic_engine.trend_data_integration import trend_aggregator
from services.topic_engine.cultural_timing_analyzer import analyze_cultural_timing
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def prioritize_with_real_time_data(
    topics: List[Dict],
    platform: str = "tiktok"
) -> List[Dict]:
    """
    Prioritize topics with real-time data integration
    
    Args:
        topics: List of candidate topics
        platform: Target platform
        
    Returns:
        Prioritized topics with scores
    """
    prioritized = []
    
    # Get algorithm state
    algorithm_state = real_time_adapter.get_platform_algorithm_state(platform)
    
    for topic_data in topics:
        topic = topic_data.get("topic", "")
        cluster = topic_data.get("cluster", "")
        
        # Base score
        base_score = topic_data.get("priority_score", 0.5)
        
        # Trend momentum
        trend_momentum = trend_aggregator.get_topic_momentum(topic)
        
        # Cultural timing
        timing = analyze_cultural_timing(topic, cluster)
        timing_score = timing["timing_score"]
        
        # Real-time momentum
        momentum = predict_momentum(cluster)
        
        # Algorithm adaptation bonus
        algorithm_bonus = 1.0
        if algorithm_state.get("current_trend") == "rising":
            algorithm_bonus = 1.1
        elif algorithm_state.get("current_trend") == "declining":
            algorithm_bonus = 0.9
        
        # Composite real-time score
        real_time_score = (
            base_score * 0.4 +
            trend_momentum * 0.2 +
            timing_score * 0.2 +
            momentum * 0.15 +
            (algorithm_bonus - 1.0) * 0.05
        )
        
        prioritized.append({
            **topic_data,
            "real_time_score": real_time_score,
            "trend_momentum": trend_momentum,
            "timing_score": timing_score,
            "algorithm_bonus": algorithm_bonus
        })
    
    # Sort by real-time score
    prioritized.sort(key=lambda x: x["real_time_score"], reverse=True)
    
    logger.info(f"Prioritized {len(prioritized)} topics with real-time data")
    
    return prioritized
