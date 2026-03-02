"""
Analytics Ingestion - Retention Curve Storage
Stores time-series retention data
"""

import os
import json
from datetime import datetime
from typing import List, Dict
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def store_retention_curve(video_id: str, retention_data: List[Dict]):
    """
    Store retention curve data
    
    Args:
        video_id: Video ID
        retention_data: List of retention data points with timestamps
    """
    os.makedirs(os.path.join(settings.ANALYTICS_DIR, "retention_curves"), exist_ok=True)
    
    curve_path = os.path.join(settings.ANALYTICS_DIR, "retention_curves", f"{video_id}.json")
    
    curve_data = {
        "video_id": video_id,
        "data_points": retention_data,
        "updated_at": datetime.now().isoformat()
    }
    
    with open(curve_path, 'w') as f:
        json.dump(curve_data, f, indent=2)
    
    logger.info(f"Stored retention curve for {video_id}")
