"""
Variant Generator - Pacing Variator
Adjusts playback speed (1.0 - 1.12)
"""

import subprocess
import os
from typing import List
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def adjust_speed(video_path: str, multiplier: float, output_path: str = None) -> str:
    """
    Adjust video playback speed
    
    Args:
        video_path: Input video path
        multiplier: Speed multiplier (1.0 = normal, >1.0 = faster)
        output_path: Output video path
        
    Returns:
        Path to speed-adjusted video
    """
    # Clamp multiplier to valid range
    multiplier = max(1.0, min(1.12, multiplier))
    
    if not output_path:
        os.makedirs(settings.VARIANTS_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(settings.VARIANTS_DIR, f"{base_name}_speed_{multiplier:.2f}x.mp4")
    
    # Use ffmpeg filter to change speed
    # For video: setpts filter
    # For audio: atempo filter (if audio exists)
    cmd = [
        "ffmpeg", "-i", video_path,
        "-filter_complex",
        f"[0:v]setpts=PTS/{multiplier}[v];[0:a]atempo={multiplier}[a]",
        "-map", "[v]", "-map", "[a]",
        "-y", output_path
    ]
    
    # If no audio, simpler command
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        # Try without audio filter
        cmd_no_audio = [
            "ffmpeg", "-i", video_path,
            "-filter:v", f"setpts=PTS/{multiplier}",
            "-y", output_path
        ]
        subprocess.run(cmd_no_audio, check=True, capture_output=True)
    
    logger.info(f"Adjusted speed to {multiplier}x: {output_path}")
    
    return output_path

def generate_speed_variants(video_path: str, variants: List[float] = None) -> List[str]:
    """
    Generate multiple speed variants
    
    Args:
        video_path: Input video
        variants: List of speed multipliers (default: [1.0, 1.03, 1.06, 1.09, 1.12])
        
    Returns:
        List of output video paths
    """
    if not variants:
        variants = [1.0, 1.03, 1.06, 1.09, 1.12]
    
    output_paths = []
    for multiplier in variants:
        output_path = adjust_speed(video_path, multiplier)
        output_paths.append(output_path)
    
    return output_paths
