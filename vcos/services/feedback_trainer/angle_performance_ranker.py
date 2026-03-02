"""
Feedback Trainer - Angle Performance Ranker
Ranks emotional angles by performance
"""

from services.hook_engine.emotional_buckets import get_all_angles
from services.analytics_ingestion.analytics_db import get_db_connection
import logging

logger = logging.getLogger(__name__)

def rank_angles() -> dict:
    """
    Rank emotional angles by average performance
    
    Returns:
        Dictionary mapping angle to average performance score
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    angles = get_all_angles()
    angle_scores = {}
    
    for angle in angles:
        cursor.execute("""
            SELECT AVG(retention_3s * 0.4 + completion_rate * 0.3 + shares_per_1k * 0.3) as score
            FROM analytics
            WHERE emotional_angle = ?
        """, (angle,))
        
        row = cursor.fetchone()
        score = row[0] if row and row[0] else 0.5
        angle_scores[angle] = score
    
    conn.close()
    
    # Sort by score
    ranked = dict(sorted(angle_scores.items(), key=lambda x: x[1], reverse=True))
    
    logger.info(f"Ranked angles: {ranked}")
    
    return ranked
