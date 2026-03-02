"""
Retention Optimizer - Zoom Injector
Injects zoom effects at idea boundaries and key moments
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def detect_idea_boundaries(transcript: List[Dict]) -> List[float]:
    """
    Detect topic/idea shift boundaries
    
    Args:
        transcript: List of sentences with timestamps
        
    Returns:
        List of timestamps where ideas shift
    """
    boundaries = []
    
    if len(transcript) < 2:
        return boundaries
    
    # Simple heuristic: detect topic shifts by sentence similarity
    # In production, use NLP for better detection
    
    for i in range(1, len(transcript)):
        prev_text = transcript[i-1].get("text", "").lower()
        curr_text = transcript[i].get("text", "").lower()
        
        # Check for transition words
        transition_words = ["now", "next", "then", "also", "but", "however", "so", "because"]
        
        # Check if sentence starts with transition or has low word overlap
        words_prev = set(prev_text.split())
        words_curr = set(curr_text.split())
        
        overlap = len(words_prev & words_curr) / max(len(words_prev), len(words_curr), 1)
        
        if overlap < 0.2 or any(curr_text.startswith(word) for word in transition_words):
            timestamp = transcript[i].get("timestamp", 0)
            boundaries.append(timestamp)
            logger.debug(f"Idea boundary detected at {timestamp:.2f}s")
    
    logger.info(f"Detected {len(boundaries)} idea boundaries")
    
    return boundaries

def inject_zoom_effects(video_path: str, boundaries: List[float], output_path: str = None) -> str:
    """
    Inject zoom effects at boundaries
    
    Args:
        video_path: Input video
        boundaries: List of timestamps for zoom
        output_path: Output video path
        
    Returns:
        Path to video with zoom effects
    """
    # Use ScreenArc integration for zoom injection
    from services.recording_service.screenarc_integration import apply_zoom_effects_screenarc
    
    if not boundaries:
        logger.info("No boundaries to inject zoom")
        return video_path
    
    if not output_path:
        import os
        from shared.config.settings import settings
        os.makedirs(settings.OPTIMIZED_VIDEOS_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(settings.OPTIMIZED_VIDEOS_DIR, f"{base_name}_zoom_injected.mp4")
    
    # Convert boundaries to zoom regions
    zoom_regions = []
    for boundary in boundaries:
        # Get video dimensions
        import cv2
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        # Create zoom region centered on screen
        zoom_width = width // 2
        zoom_height = height // 2
        zoom_x = (width - zoom_width) // 2
        zoom_y = (height - zoom_height) // 2
        
        zoom_regions.append({
            "timestamp": boundary,
            "x": zoom_x,
            "y": zoom_y,
            "width": zoom_width,
            "height": zoom_height,
            "duration": 2.0,
            "intensity": 1.5
        })
    
    try:
        logger.info(f"Injecting {len(boundaries)} zoom effects")
        return apply_zoom_effects_screenarc(video_path, zoom_regions, output_path)
    except Exception as e:
        logger.error(f"Zoom injection failed: {e}, returning original")
        return video_path
