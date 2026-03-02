"""
Recording Service - Motion Tracking
Tracks motion and cursor movements
"""

import json
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def track_motion(cursor_data_path: str) -> Dict:
    """
    Analyze motion patterns from cursor data
    
    Args:
        cursor_data_path: Path to cursor tracking JSON
        
    Returns:
        Motion analysis data
    """
    if not os.path.exists(cursor_data_path):
        return {"motion_score": 0.0, "active_regions": []}
    
    with open(cursor_data_path, 'r') as f:
        cursor_data = json.load(f)
    
    events = cursor_data.get("events", [])
    
    # Calculate motion score (activity level)
    motion_score = min(1.0, len(events) / 100.0)  # Normalize to 0-1
    
    # Identify active regions (where most activity occurs)
    active_regions = []
    
    if events:
        # Group events by screen regions
        # Simple implementation: divide screen into 9 regions
        region_counts = {}
        
        for event in events:
            x = event.get("x", 0)
            y = event.get("y", 0)
            
            # Determine region (3x3 grid)
            region_x = min(2, int(x / (1920 / 3)))
            region_y = min(2, int(y / (1080 / 3)))
            region_key = f"{region_x}_{region_y}"
            
            region_counts[region_key] = region_counts.get(region_key, 0) + 1
        
        # Get top active regions
        sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
        active_regions = [{"region": k, "activity": v} for k, v in sorted_regions[:3]]
    
    return {
        "motion_score": motion_score,
        "active_regions": active_regions,
        "total_events": len(events)
    }
