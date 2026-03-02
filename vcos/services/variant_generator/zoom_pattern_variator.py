"""
Variant Generator - Zoom Pattern Variator
Varies zoom frequency and patterns
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Zoom pattern presets
ZOOM_PATTERNS = {
    "aggressive": {
        "frequency": 3.0,  # per minute
        "duration": 1.5,  # seconds
        "intensity": 1.5  # zoom level
    },
    "moderate": {
        "frequency": 2.0,
        "duration": 2.0,
        "intensity": 1.3
    },
    "subtle": {
        "frequency": 1.0,
        "duration": 2.5,
        "intensity": 1.2
    },
    "minimal": {
        "frequency": 0.5,
        "duration": 3.0,
        "intensity": 1.1
    },
    "no_zoom": {
        "frequency": 0.0,  # No zooms - for removing existing zoom effects
        "duration": 0.0,
        "intensity": 1.0
    }
}

def generate_zoom_schedule(video_duration: float, pattern: str = "moderate") -> List[Dict]:
    """
    Generate zoom schedule based on pattern
    
    Args:
        video_duration: Video duration in seconds
        pattern: Pattern name
        
    Returns:
        List of zoom events with timestamps
    """
    pattern_config = ZOOM_PATTERNS.get(pattern, ZOOM_PATTERNS["moderate"])
    
    # Handle "no_zoom" pattern - return empty list
    if pattern == "no_zoom" or pattern_config["frequency"] == 0.0:
        logger.info(f"Generated 0 zoom events for {pattern} pattern (no zoom variant)")
        return []
    
    # Scale frequency to video duration (frequency is per minute, but scale for short videos)
    frequency = pattern_config["frequency"]
    
    # For videos shorter than 60s, scale the interval proportionally
    # e.g., if video is 5s and frequency is 1.0/min, we want ~1 zoom in 5s = every 5s
    # if video is 30s and frequency is 2.0/min, we want ~1 zoom every 30s = every 15s
    if video_duration < 60.0:
        # Scale interval: for 1.0/min in 60s = every 60s, so for 5s = every 5s
        # More precisely: interval = video_duration / (frequency * video_duration / 60)
        # Simplified: interval = 60 / frequency, but scaled by video_duration/60
        interval = (60.0 / frequency) * (video_duration / 60.0)
        # But ensure minimum interval of 1 second for very short videos
        interval = max(1.0, min(interval, video_duration / 2))
    else:
        interval = 60.0 / frequency  # seconds between zooms
    
    zooms = []
    # Start first zoom after 10% of video (avoid immediate zoom)
    current_time = max(0.5, video_duration * 0.1)
    
    # Ensure zoom duration doesn't exceed remaining video time
    max_zoom_duration = min(pattern_config["duration"], video_duration * 0.3)
    
    while current_time < video_duration - max_zoom_duration:
        zooms.append({
            "timestamp": current_time,
            "duration": max_zoom_duration,
            "intensity": pattern_config["intensity"]
        })
        current_time += interval
    
    logger.info(f"Generated {len(zooms)} zoom events for {pattern} pattern (video: {video_duration:.1f}s, interval: {interval:.1f}s)")
    
    return zooms

def apply_zoom_pattern(video_path: str, pattern: str, output_path: str = None) -> str:
    """
    Apply zoom pattern to video
    
    Args:
        video_path: Input video
        pattern: Pattern name
        output_path: Output video path
        
    Returns:
        Path to video with zoom pattern
    """
    # Use ScreenArc integration for zoom pattern application
    from services.recording_service.screenarc_integration import apply_zoom_effects_screenarc
    
    if not output_path:
        import os
        from shared.config.settings import settings
        os.makedirs(settings.VARIANTS_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(settings.VARIANTS_DIR, f"{base_name}_zoom_{pattern}.mp4")
    
    # Get video duration
    import cv2
    cap = cv2.VideoCapture(video_path)
    video_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    # Generate zoom schedule
    zoom_schedule = generate_zoom_schedule(video_duration, pattern)
    
    # Convert to zoom regions
    zoom_regions = []
    for zoom_event in zoom_schedule:
        zoom_width = int(width / zoom_event["intensity"])
        zoom_height = int(height / zoom_event["intensity"])
        zoom_x = (width - zoom_width) // 2
        zoom_y = (height - zoom_height) // 2
        
        zoom_regions.append({
            "timestamp": zoom_event["timestamp"],
            "x": zoom_x,
            "y": zoom_y,
            "width": zoom_width,
            "height": zoom_height,
            "duration": zoom_event["duration"],
            "intensity": zoom_event["intensity"]
        })
    
    try:
        logger.info(f"Applying {pattern} zoom pattern with {len(zoom_regions)} zooms")
        return apply_zoom_effects_screenarc(video_path, zoom_regions, output_path, preset=pattern)
    except Exception as e:
        logger.error(f"Zoom pattern application failed: {e}, returning original")
        return video_path
