"""
Variant Generator - Hook Swapper
Swaps hook/intro segment of video
"""

import subprocess
import os
from typing import List
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def swap_hook(video_path: str, new_hook_clip_path: str, hook_duration: float = 3.0, output_path: str = None) -> str:
    """
    Swap the hook/intro segment of a video
    
    Args:
        video_path: Original video path
        new_hook_clip_path: Path to new hook clip
        hook_duration: Duration of hook segment in seconds
        output_path: Output video path
        
    Returns:
        Path to video with swapped hook
    """
    if not output_path:
        os.makedirs(settings.VARIANTS_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(settings.VARIANTS_DIR, f"{base_name}_hook_swapped.mp4")
    
    # Extract main video (skip hook segment)
    main_video = "/tmp/main_video.mp4"
    cmd_extract = [
        "ffmpeg", "-i", video_path,
        "-ss", str(hook_duration),
        "-c", "copy",
        "-y", main_video
    ]
    subprocess.run(cmd_extract, capture_output=True)
    
    # Concatenate new hook + main video
    concat_file = "/tmp/concat_hook.txt"
    with open(concat_file, 'w') as f:
        f.write(f"file '{new_hook_clip_path}'\n")
        f.write(f"file '{main_video}'\n")
    
    cmd_concat = [
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        "-y", output_path
    ]
    subprocess.run(cmd_concat, capture_output=True)
    
    # Cleanup
    for f in [main_video, concat_file]:
        if os.path.exists(f):
            os.remove(f)
    
    logger.info(f"Swapped hook: {output_path}")
    
    return output_path
