"""
Variant Generator - Intro Rewriter
Rewrites first 2 seconds preview
"""

import subprocess
import os
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def inject_preview(video_path: str, preview_clip_path: str, preview_duration: float = 1.5, output_path: str = None) -> str:
    """
    Inject outcome preview at start of video
    
    Args:
        video_path: Main video path
        preview_clip_path: Preview clip path (extracted from end of video)
        preview_duration: Preview duration in seconds
        output_path: Output video path
        
    Returns:
        Path to video with preview
    """
    if not output_path:
        os.makedirs(settings.VARIANTS_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(settings.VARIANTS_DIR, f"{base_name}_preview.mp4")
    
    # Extract preview clip if not provided
    if not preview_clip_path:
        # Extract last N seconds as preview
        import cv2
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        start_frame = total_frames - int(preview_duration * fps)
        start_time = start_frame / fps
        
        preview_clip_path = "/tmp/preview_clip.mp4"
        cmd_extract = [
            "ffmpeg", "-i", video_path,
            "-ss", str(start_time),
            "-t", str(preview_duration),
            "-c", "copy",
            "-y", preview_clip_path
        ]
        subprocess.run(cmd_extract, capture_output=True)
    
    # Concatenate preview + main video
    concat_file = "/tmp/concat_preview.txt"
    with open(concat_file, 'w') as f:
        f.write(f"file '{preview_clip_path}'\n")
        f.write(f"file '{video_path}'\n")
    
    cmd_concat = [
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        "-y", output_path
    ]
    subprocess.run(cmd_concat, capture_output=True)
    
    # Cleanup
    if os.path.exists(concat_file):
        os.remove(concat_file)
    
    logger.info(f"Injected preview: {output_path}")
    
    return output_path
