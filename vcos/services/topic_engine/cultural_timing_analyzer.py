"""
Topic Engine - Cultural Timing Analyzer
Analyzes cultural timing and virality patterns
"""

from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def analyze_cultural_timing(topic: str, cluster: str) -> Dict:
    """
    Analyze cultural timing for a topic
    
    Args:
        topic: Topic text
        cluster: Topic cluster
        
    Returns:
        Timing analysis
    """
    # Check for time-sensitive keywords
    time_sensitive_keywords = [
        "new", "latest", "2024", "2025", "now", "recent", "update",
        "trending", "viral", "breaking"
    ]
    
    has_timing = any(keyword in topic.lower() for keyword in time_sensitive_keywords)
    
    # Check day of week (weekends often better for entertainment)
    day_of_week = datetime.now().weekday()
    weekend_bonus = 1.0 if day_of_week >= 5 else 0.9
    
    # Check time of day (platform-specific optimal times)
    hour = datetime.now().hour
    # TikTok: 6-10am, 7-9pm optimal
    # Instagram: 11am-1pm, 7-9pm optimal
    # YouTube: 2-4pm, 8-11pm optimal
    
    timing_score = 0.5
    if 6 <= hour <= 10 or 19 <= hour <= 21:
        timing_score = 0.8
    elif 11 <= hour <= 13 or 20 <= hour <= 23:
        timing_score = 0.75
    
    return {
        "has_timing_keywords": has_timing,
        "day_of_week": day_of_week,
        "weekend_bonus": weekend_bonus,
        "hour": hour,
        "timing_score": timing_score,
        "optimal_platforms": _get_optimal_platforms(hour, day_of_week)
    }

def _get_optimal_platforms(hour: int, day_of_week: int) -> List[str]:
    """Get optimal platforms for current time"""
    platforms = []
    
    # TikTok optimal: 6-10am, 7-9pm
    if (6 <= hour <= 10 or 19 <= hour <= 21):
        platforms.append("tiktok")
    
    # Instagram optimal: 11am-1pm, 7-9pm
    if (11 <= hour <= 13 or 19 <= hour <= 21):
        platforms.append("instagram")
    
    # YouTube optimal: 2-4pm, 8-11pm
    if (14 <= hour <= 16 or 20 <= hour <= 23):
        platforms.append("youtube")
    
    return platforms if platforms else ["tiktok", "instagram", "youtube"]
