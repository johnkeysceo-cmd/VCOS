"""
Export Service - Metadata Injector
Injects metadata into video files
"""

import subprocess
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def inject_metadata(video_path: str, metadata: Dict) -> str:
    """
    Inject metadata into video file
    
    Args:
        video_path: Video file path
        metadata: Metadata dictionary
        
    Returns:
        Path to video with metadata (same file, modified in place)
    """
    # Use ffmpeg to inject metadata
    cmd = ["ffmpeg", "-i", video_path]
    
    # Add metadata fields
    for key, value in metadata.items():
        cmd.extend(["-metadata", f"{key}={value}"])
    
    cmd.extend(["-c", "copy", "-y", video_path])
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Injected metadata into {video_path}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Metadata injection failed (non-critical): {e}")
    
    return video_path
