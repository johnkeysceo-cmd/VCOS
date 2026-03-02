"""
Recording Service - Screen Capture
Handles screen recording using ffmpeg
"""

import subprocess
import os
import logging
from pathlib import Path
from shared.config.settings import settings

logger = logging.getLogger(__name__)

def find_ffmpeg():
    """Find ffmpeg binary"""
    from services.recording_service.screenarc_integration import get_ffmpeg_path
    return get_ffmpeg_path()

def capture_screen(duration: int, output_path: str = None, monitor: int = 0) -> str:
    """
    Capture screen using ffmpeg
    
    Args:
        duration: Recording duration in seconds
        output_path: Optional output path
        monitor: Monitor index (0 = primary)
        
    Returns:
        Path to recorded video file
    """
    if not output_path:
        os.makedirs(settings.RAW_VIDEOS_DIR, exist_ok=True)
        import time
        output_path = os.path.join(settings.RAW_VIDEOS_DIR, f"recording_{int(time.time())}.mp4")
    
    ffmpeg_bin = find_ffmpeg()
    
    # Platform-specific capture command
    import platform
    system = platform.system()
    
    if system == "Windows":
        # Windows: use gdigrab
        cmd = [
            ffmpeg_bin,
            "-f", "gdigrab",
            "-framerate", "30",
            "-i", "desktop",
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            output_path
        ]
    elif system == "Darwin":
        # macOS: use avfoundation
        cmd = [
            ffmpeg_bin,
            "-f", "avfoundation",
            "-framerate", "30",
            "-i", f"{monitor}:none",
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            output_path
        ]
    else:
        # Linux: use x11grab
        cmd = [
            ffmpeg_bin,
            "-f", "x11grab",
            "-framerate", "30",
            "-s", "1920x1080",  # Default resolution
            "-i", ":0.0",
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            output_path
        ]
    
    try:
        logger.info(f"Starting screen capture: {output_path}")
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Screen capture completed: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Screen capture failed: {e}")
        raise Exception(f"Screen capture failed: {e.stderr.decode() if e.stderr else str(e)}")

async def capture_screen_async(duration: int, output_path: str = None, monitor: int = 0) -> str:
    """Async version of capture_screen"""
    import asyncio
    return await asyncio.to_thread(capture_screen, duration, output_path, monitor)
