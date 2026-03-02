"""
Export Service - Video Encoder
Encodes videos for specific platforms
"""

import subprocess
import os
from typing import Dict
from pathlib import Path
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)


def encode_for_platform(video_path: str, platform: str, output_path: str = None) -> str:
    """
    Encode video for specific platform
    
    Args:
        video_path: Input video path (must be absolute)
        platform: Platform name (tiktok, instagram, youtube)
        output_path: Output video path (optional)
        
    Returns:
        Path to encoded video
    """
    # Convert to absolute paths
    video_path = str(Path(video_path).resolve())
    
    # Check if input file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Input video not found: {video_path}")
    
    # Import platform config
    if platform == "tiktok":
        from services.export_service.platform_profiles.tiktok import get_export_settings
    elif platform == "instagram":
        from services.export_service.platform_profiles.instagram import get_export_settings
    elif platform == "youtube":
        from services.export_service.platform_profiles.youtube_shorts import get_export_settings
    else:
        raise ValueError(f"Unknown platform: {platform}")
    
    config = get_export_settings()
    
    if not output_path:
        os.makedirs(settings.VARIANTS_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(settings.VARIANTS_DIR, f"{base_name}_{platform}.mp4")
    
    # Convert output to absolute path
    output_path = str(Path(output_path).resolve())
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Get video duration to check platform limits
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        
        # Check duration limits
        max_duration = config.get("max_duration", 60)
        if duration > max_duration:
            logger.warning(f"Video duration {duration:.1f}s exceeds {platform} max {max_duration}s, will be trimmed")
            # Trim video to max duration
            trim_filter = f"trim=duration={max_duration}"
        else:
            trim_filter = None
    except Exception as e:
        logger.warning(f"Failed to get video duration: {e}, proceeding without trim check")
        trim_filter = None
    
    # Build ffmpeg command with proper error handling
    width, height = config["resolution"]
    
    # Build video filter chain
    video_filters = [
        f"scale={width}:{height}:force_original_aspect_ratio=decrease",
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black"
    ]
    
    if trim_filter:
        video_filters.insert(0, trim_filter)
    
    vf_string = ",".join(video_filters)
    
    # Check for audio stream
    has_audio = _check_audio_stream(video_path)
    
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", vf_string,
        "-c:v", "libx264",
        "-preset", "medium",
        "-b:v", config["bitrate"],
        "-r", str(config["fps"]),
        "-pix_fmt", "yuv420p",  # Ensure compatibility
        "-movflags", "+faststart",  # Enable streaming
    ]
    
    if has_audio:
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])
    else:
        cmd.append("-an")  # No audio
    
    cmd.extend(["-y", output_path])
    
    try:
        logger.info(f"Encoding for {platform}: {video_path} -> {output_path}")
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        # Verify output file was created
        if not os.path.exists(output_path):
            raise RuntimeError(f"Encoding completed but output file not found: {output_path}")
        
        # Check file size
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        max_size_mb = config.get("max_file_size_mb", 500)
        
        if file_size_mb > max_size_mb:
            logger.warning(f"Encoded file size {file_size_mb:.1f}MB exceeds {platform} max {max_size_mb}MB")
            # Re-encode with lower bitrate if needed
            if file_size_mb > max_size_mb * 1.2:  # 20% over limit
                logger.info(f"Re-encoding with lower bitrate to meet size limit")
                return _reencode_with_lower_bitrate(video_path, platform, output_path, config, max_size_mb)
        
        logger.info(f"Successfully encoded for {platform}: {output_path} ({file_size_mb:.1f}MB)")
        return output_path
        
    except subprocess.TimeoutExpired:
        logger.error(f"Encoding timed out for {video_path}")
        raise RuntimeError(f"Encoding timed out after 10 minutes")
    except subprocess.CalledProcessError as e:
        # Check if output file was actually created despite the error
        # FFmpeg may exit with non-zero code if interrupted, but encoding might have completed
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"Encoding completed successfully despite non-zero exit code: {output_path} ({file_size_mb:.1f}MB)")
            # Check file size limits
            max_size_mb = config.get("max_file_size_mb", 500)
            if file_size_mb > max_size_mb * 1.2:
                logger.warning(f"File size {file_size_mb:.1f}MB exceeds limit, may need re-encoding")
            return output_path
        
        # If file doesn't exist, it's a real error
        logger.error(f"Encoding failed: {e.stderr}")
        # Try to provide more helpful error message
        if "No such file" in e.stderr or "Invalid data" in e.stderr:
            raise FileNotFoundError(f"Invalid video file: {video_path}")
        raise RuntimeError(f"FFmpeg encoding failed: {e.stderr}")


def _check_audio_stream(video_path: str) -> bool:
    """Check if video has audio stream"""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_type",
            "-of", "json",
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)
        return "codec_type" in result.stdout and "audio" in result.stdout
    except Exception:
        return False


def _reencode_with_lower_bitrate(
    video_path: str,
    platform: str,
    output_path: str,
    config: Dict,
    max_size_mb: float
) -> str:
    """Re-encode with lower bitrate to meet size limit"""
    from pathlib import Path
    
    # Calculate target bitrate based on duration and max size
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 60.0
        cap.release()
        
        # Target bitrate: (max_size_mb * 8) / duration (convert MB to Mbits, then to kbits)
        target_bitrate_k = int((max_size_mb * 8 * 1000) / duration * 0.9)  # 90% of max to be safe
        target_bitrate = f"{target_bitrate_k}k"
    except Exception:
        # Fallback to lower bitrate
        target_bitrate = "3000k"
    
    width, height = config["resolution"]
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black",
        "-c:v", "libx264", "-preset", "medium",
        "-b:v", target_bitrate,
        "-r", str(config["fps"]),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "96k",  # Lower audio bitrate too
        "-y", output_path
    ]
    
    subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    return output_path
