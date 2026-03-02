"""
Recording Service - ScreenArc Integration
Python wrapper for ScreenArc CLI functionality
"""

import os
import subprocess
import json
import platform
from pathlib import Path
from typing import Dict, Optional, List
import logging
import time

logger = logging.getLogger(__name__)

# Path to ScreenArc project
SCREENARC_ROOT = Path(__file__).parent.parent.parent.parent / "generation_content" / "screenarc"

def get_screenarc_cli_path() -> str:
    """Get path to ScreenArc CLI script"""
    system = platform.system().lower()
    
    # Try to find the CLI script
    cli_paths = [
        SCREENARC_ROOT / "scripts" / "screenarc-cli.cjs",
        SCREENARC_ROOT / "scripts" / "cli-export.cjs",
    ]
    
    for path in cli_paths:
        if path.exists():
            return str(path)
    
    # Fallback to npm script
    return None

def get_ffmpeg_path() -> str:
    """Get FFmpeg binary path from ScreenArc binaries"""
    system = platform.system().lower()
    
    if system == "windows":
        ffmpeg_path = SCREENARC_ROOT / "binaries" / "windows" / "ffmpeg.exe"
    elif system == "darwin":
        ffmpeg_path = SCREENARC_ROOT / "binaries" / "darwin" / "ffmpeg"
    else:  # linux
        ffmpeg_path = SCREENARC_ROOT / "binaries" / "linux" / "ffmpeg"
    
    if ffmpeg_path.exists():
        return str(ffmpeg_path)
    
    return "ffmpeg"  # Fallback to system ffmpeg

def process_video_with_screenarc(
    input_video: str,
    output_video: str,
    metadata_path: Optional[str] = None,
    preset: str = "cinematic",
    **kwargs
) -> Dict:
    """
    Process video using ScreenArc CLI (uses comprehensive wrapper)
    """
    from services.recording_service.screenarc_wrapper import screenarc_wrapper
    return screenarc_wrapper.start_screenarc_cli(
        input_video,
        output_video,
        preset,
        metadata_path,
        **kwargs
    )
    """
    Process video using ScreenArc CLI
    
    Args:
        input_video: Input video path
        output_video: Output video path
        metadata_path: Optional metadata JSON path
        preset: Preset name (cinematic, minimal, youtube, short, instagram, clean, dark)
        **kwargs: Additional ScreenArc options
        
    Returns:
        Processing result dictionary
    """
    # Use comprehensive wrapper
    from services.recording_service.screenarc_wrapper import screenarc_wrapper
    return screenarc_wrapper.start_screenarc_cli(
        input_video,
        output_video,
        preset,
        metadata_path,
        **kwargs
    )

def process_video_via_node(
    input_video: str,
    output_video: str,
    metadata_path: Optional[str] = None,
    preset: str = "cinematic",
    **kwargs
) -> Dict:
    """Process video using Node.js directly (fallback)"""
    # Use npm script
    cmd = ["npm", "run", "cli:process", "--",
           "-i", input_video,
           "-o", output_video,
           "-p", preset]
    
    if metadata_path:
        cmd.extend(["-m", metadata_path])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(SCREENARC_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "success": True,
            "output_path": output_video,
            "stdout": result.stdout
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Node processing failed: {e.stderr}")
        return {
            "success": False,
            "error": e.stderr
        }

def batch_process_videos(
    input_dir: str,
    output_dir: str,
    preset: str = "cinematic",
    pattern: str = "*.mp4"
) -> List[Dict]:
    """
    Batch process videos using ScreenArc
    
    Args:
        input_dir: Input directory
        output_dir: Output directory
        preset: Preset name
        pattern: File pattern
        
    Returns:
        List of processing results
    """
    cli_path = get_screenarc_cli_path()
    
    if not cli_path:
        return []
    
    cmd = ["node", cli_path, "batch",
           "-i", input_dir,
           "-o", output_dir,
           "-p", preset,
           "--pattern", pattern,
           "--json"]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(SCREENARC_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse JSON results
        results_file = os.path.join(output_dir, "batch-results.json")
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                return json.load(f)
        
        return []
    except subprocess.CalledProcessError as e:
        logger.error(f"Batch processing failed: {e.stderr}")
        return []

def get_available_presets() -> List[str]:
    """Get available ScreenArc presets"""
    return ["cinematic", "minimal", "youtube", "short", "instagram", "clean", "dark"]

def apply_zoom_effects_screenarc(
    video_path: str,
    zoom_regions: List[Dict],
    output_path: str,
    preset: str = "cinematic"
) -> str:
    """
    Apply zoom effects using ScreenArc
    
    Args:
        video_path: Input video
        zoom_regions: List of zoom region dicts with timestamp, x, y, width, height
        output_path: Output video path
        preset: Preset name
        
    Returns:
        Output video path
    """
    # Create metadata JSON with zoom regions
    metadata = {
        "events": [],
        "zoomRegions": []
    }
    
    for region in zoom_regions:
        metadata["zoomRegions"].append({
            "startTime": region.get("timestamp", 0),
            "duration": region.get("duration", 2.0),
            "x": region.get("x", 0),
            "y": region.get("y", 0),
            "width": region.get("width", 1920),
            "height": region.get("height", 1080),
            "zoomLevel": region.get("intensity", 1.5)
        })
    
    # Save metadata temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(metadata, f, indent=2)
        metadata_path = f.name
    
    try:
        # Process with ScreenArc
        result = process_video_with_screenarc(
            video_path,
            output_path,
            metadata_path=metadata_path,
            preset=preset
        )
        
        if result["success"]:
            return output_path
        else:
            raise Exception(f"ScreenArc processing failed: {result.get('error')}")
    finally:
        # Cleanup
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
    
    return output_path
