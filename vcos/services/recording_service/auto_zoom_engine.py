"""
Recording Service - Auto Zoom Engine
Tracks cursor positions and applies auto-zoom
"""

import json
import os
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

def apply_auto_zoom(
    video_path: str,
    cursor_data_path: str,
    output_path: str = None
) -> str:
    """
    Apply auto-zoom based on cursor tracking data
    
    Args:
        video_path: Path to raw video
        cursor_data_path: Path to cursor tracking JSON
        output_path: Optional output path
        
    Returns:
        Path to zoomed video
    """
    # Load cursor data
    if not os.path.exists(cursor_data_path):
        logger.warning(f"Cursor data not found: {cursor_data_path}")
        return video_path
    
    with open(cursor_data_path, 'r') as f:
        cursor_data = json.load(f)
    
    # Extract click events for zoom targets
    click_events = [
        event for event in cursor_data.get("events", [])
        if event.get("type") == "click"
    ]
    
    logger.info(f"Found {len(click_events)} click events for zoom")
    
    # Use ScreenArc integration for zoom
    from services.recording_service.screenarc_integration import apply_zoom_effects_screenarc
    
    zoom_regions = detect_zoom_regions(cursor_data)
    
    if not output_path:
        import os
        from shared.config.settings import settings
        os.makedirs(settings.OPTIMIZED_VIDEOS_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(settings.OPTIMIZED_VIDEOS_DIR, f"{base_name}_zoomed.mp4")
    
    try:
        return apply_zoom_effects_screenarc(video_path, zoom_regions, output_path)
    except Exception as e:
        logger.error(f"Zoom application failed: {e}, returning original")
        return video_path

def detect_zoom_regions(cursor_data: Dict, video_width: int = 1920, video_height: int = 1080) -> List[Dict]:
    """
    Detect regions to zoom into based on cursor activity
    
    Args:
        cursor_data: Cursor tracking data
        video_width: Video width
        video_height: Video height
        
    Returns:
        List of zoom regions with timestamps
    """
    zoom_regions = []
    
    # Group cursor positions by time windows
    events = cursor_data.get("events", [])
    
    for event in events:
        if event.get("type") == "click":
            x = event.get("x", video_width // 2)
            y = event.get("y", video_height // 2)
            timestamp = event.get("timestamp", 0)
            
            # Define zoom region (crop around click point)
            zoom_width = video_width // 2
            zoom_height = video_height // 2
            
            # Center crop on click point
            crop_x = max(0, min(x - zoom_width // 2, video_width - zoom_width))
            crop_y = max(0, min(y - zoom_height // 2, video_height - zoom_height))
            
            zoom_regions.append({
                "timestamp": timestamp,
                "x": crop_x,
                "y": crop_y,
                "width": zoom_width,
                "height": zoom_height,
                "duration": 2.0  # 2 second zoom
            })
    
    return zoom_regions
