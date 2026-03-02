"""
Recording Service - Video Processor
Main interface for video processing using ScreenArc
"""

from services.recording_service.screenarc_integration import (
    process_video_with_screenarc,
    batch_process_videos,
    get_available_presets,
    apply_zoom_effects_screenarc
)
from typing import Dict, List, Optional
import logging
import os
import cv2

logger = logging.getLogger(__name__)

def _validate_video_file(video_path: str, max_wait_seconds: int = 10) -> bool:
    """Validate that video file exists and is readable, waiting for file to be fully written"""
    import time
    import subprocess
    
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return False
    
    # Wait for file size to stabilize (file is being written)
    start_time = time.time()
    last_size = 0
    stable_count = 0
    
    while time.time() - start_time < max_wait_seconds:
        try:
            current_size = os.path.getsize(video_path)
            if current_size == 0:
                time.sleep(0.5)
                continue
            
            if current_size == last_size:
                stable_count += 1
                if stable_count >= 3:  # Stable for 1.5 seconds
                    break
            else:
                stable_count = 0
                last_size = current_size
            
            time.sleep(0.5)
        except OSError:
            time.sleep(0.5)
            continue
    
    if os.path.getsize(video_path) == 0:
        logger.error(f"Video file is empty: {video_path}")
        return False
    
    # Try ffprobe first (more reliable for MP4 - checks for moov atom)
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        pass  # Fall back to OpenCV
    
    # Fallback: Try to open with OpenCV
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Cannot open video file: {video_path}")
            return False
        
        # Try to read first frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logger.error(f"Cannot read frames from video: {video_path}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating video {video_path}: {e}")
        return False

def process_video(
    input_path: str,
    output_path: str,
    preset: str = "cinematic",
    metadata_path: Optional[str] = None,
    zoom_regions: Optional[List[Dict]] = None,
    **options
) -> Dict:
    """
    Process a video with ScreenArc
    
    Args:
        input_path: Input video path
        output_path: Output video path
        preset: Preset name
        metadata_path: Optional metadata JSON
        zoom_regions: Optional zoom regions
        **options: Additional ScreenArc options
        
    Returns:
        Processing result
    """
    if zoom_regions:
        # Apply zoom effects
        return {
            "success": True,
            "output_path": apply_zoom_effects_screenarc(
                input_path,
                zoom_regions,
                output_path,
                preset
            )
        }
    
    # Standard processing
    return process_video_with_screenarc(
        input_path,
        output_path,
        metadata_path=metadata_path,
        preset=preset,
        **options
    )

def optimize_for_retention(
    video_path: str,
    output_path: str,
    transcript: Optional[List[Dict]] = None
) -> str:
    """
    Optimize video for retention using ScreenArc processing
    
    Args:
        video_path: Input video
        output_path: Output video
        transcript: Optional transcript for idea boundary detection
        
    Returns:
        Output video path
    """
    from services.retention_optimizer.zoom_injector import detect_idea_boundaries, inject_zoom_effects
    
    # Detect idea boundaries if transcript provided
    zoom_regions = []
    if transcript:
        boundaries = detect_idea_boundaries(transcript)
        # Convert to zoom regions
        import cv2
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        for boundary in boundaries:
            zoom_regions.append({
                "timestamp": boundary,
                "x": width // 4,
                "y": height // 4,
                "width": width // 2,
                "height": height // 2,
                "duration": 2.0,
                "intensity": 1.5
            })
    
    # Validate input file first
    if not _validate_video_file(video_path):
        raise ValueError(f"Input video file is invalid or corrupted: {video_path}")
    
    # Skip ScreenArc processing if video is already from exports (already has effects)
    # Check if video path contains "exports" or "ScreenArc-" (export naming pattern)
    video_path_lower = video_path.lower()
    if "exports" in video_path_lower or ("screenarc-" in video_path_lower and "recording" not in video_path_lower):
        logger.info(f"Video appears to be exported (already has effects), skipping ScreenArc processing")
        # Just copy to output path, but ensure we don't create excessively long filenames
        import shutil
        from pathlib import Path
        
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # If output path would be too long or already has _optimized, use a simpler name
        if len(str(output_path_obj)) > 200 or "_optimized" in output_path_obj.stem:
            # Use a hash-based short name to avoid path length issues
            import hashlib
            video_hash = hashlib.md5(video_path.encode()).hexdigest()[:8]
            output_path = str(output_path_obj.parent / f"processed_{video_hash}{output_path_obj.suffix}")
            output_path_obj = Path(output_path)
        
        shutil.copy2(video_path, output_path)
        
        # Validate copied file
        if not _validate_video_file(output_path):
            raise RuntimeError(f"Copied video file is corrupted: {output_path}")
        
        return output_path
    
    # Process with ScreenArc (with aggressive timeout to avoid hanging)
    # Use threading to make it non-blocking with timeout
    import threading
    result_container = {"result": None, "done": False}
    exception_container = {"exception": None}
    
    def run_processing():
        try:
            result_container["result"] = process_video(
                video_path,
                output_path,
                preset="cinematic",
                zoom_regions=zoom_regions if zoom_regions else None
            )
        except Exception as e:
            exception_container["exception"] = e
        finally:
            result_container["done"] = True
    
    # Start processing in thread
    thread = threading.Thread(target=run_processing, daemon=True)
    thread.start()
    
    # Wait with timeout (max 45 seconds total)
    thread.join(timeout=45)
    
    if not result_container["done"]:
        logger.error(f"ScreenArc processing TIMED OUT after 45s - skipping and using original video")
        return video_path
    
    if exception_container["exception"]:
        logger.warning(f"ScreenArc processing exception: {exception_container['exception']}, returning original")
        return video_path
    
    result = result_container["result"]
    if result and result.get("success"):
        # Verify output exists and is valid
        output_file = result["output_path"]
        if os.path.exists(output_file) and _validate_video_file(output_file):
            return output_file
        else:
            logger.warning(f"ScreenArc output file not found or invalid: {output_file}, using original")
            # Validate original before returning
            if _validate_video_file(video_path):
                return video_path
            else:
                raise RuntimeError(f"Both processed and original video files are invalid")
    else:
        error_msg = result.get("error", "Unknown error") if result else "No result"
        logger.warning(f"ScreenArc processing failed: {error_msg}, returning original")
        # Validate original before returning
        if _validate_video_file(video_path):
            return video_path
        else:
            raise RuntimeError(f"Original video file is invalid and processing failed: {error_msg}")
