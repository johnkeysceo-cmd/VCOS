"""
Analytics Ingestion - Analytics Database
Database operations for analytics data
"""

import sqlite3
import os
from typing import Optional, Dict
from shared.config.settings import settings
from shared.schemas.batch_schema import AnalyticsSchema
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(settings.DATA_ROOT, "analytics.db")

def get_db_connection():
    """Get database connection"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize analytics database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            hook_type TEXT,
            emotional_angle TEXT,
            topic_cluster TEXT,
            length REAL,
            retention_3s REAL,
            retention_50pct REAL,
            completion_rate REAL,
            shares_per_1k REAL,
            comments_per_1k REAL,
            velocity_30min REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Analytics database initialized")

def store_analytics(analytics: AnalyticsSchema):
    """Store analytics data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO analytics 
        (video_id, hook_type, emotional_angle, topic_cluster, length,
         retention_3s, retention_50pct, completion_rate,
         shares_per_1k, comments_per_1k, velocity_30min)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        analytics.video_id,
        analytics.hook_type,
        analytics.emotional_angle,
        analytics.topic_cluster,
        analytics.length,
        analytics.retention_3s,
        analytics.retention_50pct,
        analytics.completion_rate,
        analytics.shares_per_1k,
        analytics.comments_per_1k,
        analytics.velocity_30min
    ))
    
    conn.commit()
    conn.close()
    logger.info(f"Stored analytics for {analytics.video_id}")

init_db()
