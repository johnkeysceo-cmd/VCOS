"""
Topic Engine - Topic Database
Database operations for topic and cluster data
"""

import sqlite3
import os
from typing import Dict, Optional
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Initialize database path
DB_PATH = os.path.join(settings.DATA_ROOT, "topics.db")

def get_db_connection():
    """Get database connection"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Topics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            topic_id TEXT PRIMARY KEY,
            topic_text TEXT NOT NULL,
            cluster TEXT NOT NULL,
            priority_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Cluster metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cluster_metrics (
            cluster TEXT PRIMARY KEY,
            avg_retention REAL DEFAULT 0.5,
            avg_shares_per_1k REAL DEFAULT 0.1,
            repeat_watch_lift REAL DEFAULT 1.0,
            video_count INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Topic database initialized")

def get_cluster_metrics(cluster: str) -> Dict:
    """
    Get metrics for a cluster
    
    Args:
        cluster: Cluster name
        
    Returns:
        Dictionary of cluster metrics
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM cluster_metrics WHERE cluster = ?
    """, (cluster,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    
    # Return defaults if cluster doesn't exist
    return {
        "avg_retention": 0.5,
        "avg_shares_per_1k": 0.1,
        "repeat_watch_lift": 1.0,
        "video_count": 0
    }

def update_cluster_metrics(cluster: str, metrics: Dict):
    """Update cluster metrics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO cluster_metrics 
        (cluster, avg_retention, avg_shares_per_1k, repeat_watch_lift, video_count, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        cluster,
        metrics.get("avg_retention", 0.5),
        metrics.get("avg_shares_per_1k", 0.1),
        metrics.get("repeat_watch_lift", 1.0),
        metrics.get("video_count", 0)
    ))
    
    conn.commit()
    conn.close()
    logger.info(f"Updated metrics for cluster: {cluster}")

# Initialize database on import
init_db()
