"""
Prioritization Engine - Momentum Predictor
Predicts momentum for topics/clusters
"""

from services.analytics_ingestion.analytics_db import get_db_connection
import logging

logger = logging.getLogger(__name__)

def predict_momentum(cluster: str) -> float:
    """
    Predict momentum for a cluster
    
    Args:
        cluster: Cluster name
        
    Returns:
        Momentum score (0.0 to 1.0)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate recent velocity trend
    cursor.execute("""
        SELECT AVG(velocity_30min) as avg_velocity
        FROM analytics
        WHERE topic_cluster = ?
        AND timestamp > datetime('now', '-7 days')
    """, (cluster,))
    
    row = cursor.fetchone()
    conn.close()
    
    velocity = row[0] if row and row[0] else 0.0
    
    # Normalize to 0-1 (assuming max velocity of 1000 views/min)
    momentum = min(1.0, velocity / 1000.0)
    
    return momentum
