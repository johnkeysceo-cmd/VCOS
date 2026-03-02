"""
Retention Optimizer - Pause Trimmer
Removes detected silence/pause periods from video
"""

import subprocess
import os
from typing import List, Tuple
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def trim_pauses(video_path: str, silence_periods: List[Tuple[float, float]], output_path: str = None) -> str:
    """
    Trim silence periods from video
    
    Args:
        video_path: Input video path
        silence_periods: List of (start, end) silence periods
        output_path: Output video path
        
    Returns:
        Path to trimmed video
    """
    if not silence_periods:
        logger.info("No silence periods to trim")
        return video_path
    
    if not output_path:
        os.makedirs(settings.OPTIMIZED_VIDEOS_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(settings.OPTIMIZED_VIDEOS_DIR, f"{base_name}_trimmed.mp4")
    
    # Build ffmpeg filter to remove silence segments
    # Use complex filter to concatenate non-silent segments
    filter_parts = []
    segment_files = []
    
    # For each non-silent segment, extract it
    prev_end = 0.0
    
    for i, (silence_start, silence_end) in enumerate(silence_periods):
        if silence_start > prev_end:
            # Extract segment before silence
            segment_file = f"/tmp/segment_{i}.mp4"
            segment_files.append(segment_file)
            
            duration = silence_start - prev_end
            cmd = [
                "ffmpeg", "-i", video_path,
                "-ss", str(prev_end),
                "-t", str(duration),
                "-c", "copy",
                "-y", segment_file
            ]
            subprocess.run(cmd, capture_output=True)
        
        prev_end = silence_end
    
    # Handle final segment
    # Get video duration first
    import cv2
    cap = cv2.VideoCapture(video_path)
    video_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    if prev_end < video_duration:
        segment_file = f"/tmp/segment_final.mp4"
        segment_files.append(segment_file)
        
        duration = video_duration - prev_end
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", str(prev_end),
            "-t", str(duration),
            "-c", "copy",
            "-y", segment_file
        ]
        subprocess.run(cmd, capture_output=True)
    
    # Concatenate all segments
    if segment_files:
        concat_file = "/tmp/concat_list.txt"
        with open(concat_file, 'w') as f:
            for seg in segment_files:
                f.write(f"file '{seg}'\n")
        
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            "-y", output_path
        ]
        subprocess.run(cmd, capture_output=True)
        
        # Cleanup
        for seg in segment_files:
            if os.path.exists(seg):
                os.remove(seg)
        if os.path.exists(concat_file):
            os.remove(concat_file)
    else:
        # No segments, just copy original
        import shutil
        shutil.copy2(video_path, output_path)
    
    logger.info(f"Trimmed pauses: {output_path}")
    
    return output_path
