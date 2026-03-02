"""
Feedback Trainer - Cluster Strength Model
Updates cluster performance scores
"""

from services.topic_engine.cluster_manager import update_cluster_performance
from services.analytics_ingestion.analytics_db import get_db_connection
import logging

logger = logging.getLogger(__name__)

def update_cluster(cluster: str, performance_score: float):
    """
    Update cluster strength based on performance
    
    Args:
        cluster: Cluster name
        performance_score: Performance score (0.0 to 1.0)
    """
    # Get current cluster metrics
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            AVG(retention_3s) as avg_retention,
            AVG(shares_per_1k) as avg_shares,
            COUNT(*) as video_count
        FROM analytics
        WHERE topic_cluster = ?
    """, (cluster,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row and row[2] > 0:  # video_count > 0
        metrics = {
            "avg_retention": row[0] or 0.5,
            "avg_shares_per_1k": row[1] or 0.1,
            "video_count": row[2],
            "performance_score": performance_score
        }
        
        update_cluster_performance(cluster, metrics)
        logger.info(f"Updated cluster {cluster} with score {performance_score:.2f}")
