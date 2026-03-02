"""
Prioritization Engine - Content Calendar Generator
Generates content calendar based on recommendations
"""

from services.prioritization_engine.topic_recommender import recommend_next
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def generate_content_calendar(days: int = 7) -> dict:
    """
    Generate content calendar
    
    Args:
        days: Number of days to plan
        
    Returns:
        Content calendar dictionary
    """
    recommendations = await recommend_next(count=days * 2)  # 2 videos per day
    
    calendar = {
        "start_date": datetime.now().isoformat(),
        "days": days,
        "schedule": []
    }
    
    current_date = datetime.now()
    
    for i, rec in enumerate(recommendations[:days * 2]):
        day = i // 2  # 2 videos per day
        date = (current_date + timedelta(days=day)).isoformat()
        
        calendar["schedule"].append({
            "date": date,
            "topic": rec["topic"],
            "cluster": rec["cluster"],
            "priority_score": rec["priority_score"]
        })
    
    logger.info(f"Generated content calendar for {days} days")
    
    return calendar
