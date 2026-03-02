"""
Hook Engine - Hook Database
Database operations for hook performance data
"""

import sqlite3
import os
from typing import Optional
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Initialize database path
DB_PATH = os.path.join(settings.DATA_ROOT, "hooks.db")

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
    
    # Hooks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hooks (
            hook_id TEXT PRIMARY KEY,
            hook_text TEXT NOT NULL,
            template_structure TEXT,
            emotional_angle TEXT,
            predicted_ctr_score REAL,
            actual_ctr REAL,
            lift REAL DEFAULT 1.0,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Template performance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS template_performance (
            template_structure TEXT PRIMARY KEY,
            avg_ctr REAL DEFAULT 0.0,
            avg_lift REAL DEFAULT 1.0,
            usage_count INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Hook database initialized")

def get_historical_performance(template_structure: str) -> Optional[float]:
    """
    Get historical performance lift for a template
    
    Args:
        template_structure: Template structure string
        
    Returns:
        Historical lift (default 1.0 if no data)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT avg_lift FROM template_performance WHERE template_structure = ?
    """, (template_structure,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row[0]
    
    return None

def update_hook_performance(hook_id: str, actual_ctr: float, lift: float):
    """Update hook performance data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update hook
    cursor.execute("""
        UPDATE hooks 
        SET actual_ctr = ?, lift = ?, usage_count = usage_count + 1
        WHERE hook_id = ?
    """, (actual_ctr, lift, hook_id))
    
    # Update template performance
    cursor.execute("""
        SELECT template_structure FROM hooks WHERE hook_id = ?
    """, (hook_id,))
    
    row = cursor.fetchone()
    if row:
        template_structure = row[0]
        
        # Calculate new average
        cursor.execute("""
            SELECT AVG(lift), COUNT(*) FROM hooks 
            WHERE template_structure = ? AND actual_ctr IS NOT NULL
        """, (template_structure,))
        
        avg_row = cursor.fetchone()
        if avg_row and avg_row[1] > 0:
            avg_lift = avg_row[0]
            
            cursor.execute("""
                INSERT OR REPLACE INTO template_performance 
                (template_structure, avg_lift, usage_count, updated_at)
                VALUES (?, ?, 
                    (SELECT COUNT(*) FROM hooks WHERE template_structure = ?),
                    CURRENT_TIMESTAMP)
            """, (template_structure, avg_lift, template_structure))
    
    conn.commit()
    conn.close()
    logger.info(f"Updated performance for hook: {hook_id}")

# Initialize database on import
init_db()
