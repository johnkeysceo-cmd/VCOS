"""Recording Service - Screen Studio clone core with ScreenArc integration"""

# Export main functions
from services.recording_service.screen_capture import capture_screen, capture_screen_async
from services.recording_service.auto_zoom_engine import apply_auto_zoom, detect_zoom_regions
from services.recording_service.video_processor import process_video, optimize_for_retention
from services.recording_service.screenarc_integration import (
    process_video_with_screenarc,
    batch_process_videos,
    get_available_presets
)

__all__ = [
    "capture_screen",
    "capture_screen_async",
    "apply_auto_zoom",
    "detect_zoom_regions",
    "process_video",
    "optimize_for_retention",
    "process_video_with_screenarc",
    "batch_process_videos",
    "get_available_presets"
]
