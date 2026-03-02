"""
Variant Generator - Production Video Transformer
Comprehensive video transformation engine for creating variants
"""

import subprocess
import os
import json
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import cv2

logger = logging.getLogger(__name__)


class VideoTransformer:
    """Production-grade video transformation engine"""
    
    def __init__(self):
        self.temp_dir = None
    
    def _get_temp_dir(self):
        """Get or create temp directory"""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix="vcos_transform_")
        return self.temp_dir
    
    def _validate_video_file(self, video_path: str, max_wait_seconds: int = 10) -> bool:
        """Validate that video file exists and is readable, waiting for file to be fully written"""
        
        if not os.path.exists(video_path):
            logger.error(f"Video file does not exist: {video_path}")
            return False
        
        # Wait for file to be fully written (check file size stability)
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
                    if stable_count >= 3:  # File size stable for 1.5 seconds
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
        
        # Try to validate with ffprobe first (more reliable for MP4)
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
    
    def _get_video_info(self, video_path: str) -> Dict:
        """Get video metadata using OpenCV"""
        if not self._validate_video_file(video_path):
            raise ValueError(f"Invalid video file: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration": duration
        }
    
    def _check_audio_stream(self, video_path: str) -> bool:
        """Check if video has audio stream"""
        try:
            cmd = [
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=codec_type", "-of", "json",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return "codec_type" in result.stdout
        except Exception:
            return False
    
    def apply_speed_change(
        self,
        video_path: str,
        speed_multiplier: float,
        output_path: str,
        preserve_audio: bool = True
    ) -> str:
        """
        Apply speed change to video using FFmpeg
        
        Args:
            video_path: Input video path
            speed_multiplier: Speed multiplier (1.0 = normal, >1.0 = faster)
            output_path: Output video path
            preserve_audio: Whether to preserve audio pitch
            
        Returns:
            Path to transformed video
        """
        # Clamp multiplier
        speed_multiplier = max(0.25, min(2.0, speed_multiplier))
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Check for audio
        has_audio = self._check_audio_stream(video_path) if preserve_audio else False
        
        if has_audio:
            # Use setpts for video and atempo for audio
            # atempo can only handle 0.5-2.0 range, so chain if needed
            if speed_multiplier < 0.5:
                # Chain atempo filters
                atempo_chain = f"atempo=0.5,atempo={speed_multiplier / 0.5}"
            elif speed_multiplier > 2.0:
                # Chain atempo filters
                atempo_chain = f"atempo=2.0,atempo={speed_multiplier / 2.0}"
            else:
                atempo_chain = f"atempo={speed_multiplier}"
            
            filter_complex = (
                f"[0:v]setpts=PTS/{speed_multiplier}[v];"
                f"[0:a]{atempo_chain}[a]"
            )
            
            cmd = [
                "ffmpeg", "-i", video_path,
                "-filter_complex", filter_complex,
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                "-y", output_path
            ]
        else:
            # No audio, simpler command
            cmd = [
                "ffmpeg", "-i", video_path,
                "-filter:v", f"setpts=PTS/{speed_multiplier}",
                "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                "-y", output_path
            ]
        
        # Validate input file first
        if not self._validate_video_file(video_path):
            raise ValueError(f"Input video file is invalid or corrupted: {video_path}")
        
        try:
            logger.info(f"Applying speed change {speed_multiplier}x to {video_path}")
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Validate output file was created and is valid
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise RuntimeError(f"Output file was not created or is empty: {output_path}")
            
            if not self._validate_video_file(output_path):
                raise RuntimeError(f"Output video file is corrupted: {output_path}")
            
            logger.info(f"Speed change applied: {output_path}")
            return output_path
        except subprocess.TimeoutExpired:
            logger.error(f"Speed change timed out for {video_path}")
            # Clean up partial output
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Speed change failed: {e.stderr}")
            # Clean up partial output
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            raise
    
    def apply_zoom_pattern(
        self,
        video_path: str,
        zoom_regions: List[Dict],
        output_path: str
    ) -> str:
        """
        Apply zoom pattern using FFmpeg crop and scale filters
        
        Args:
            video_path: Input video path
            zoom_regions: List of zoom regions with timestamp, x, y, width, height, duration, intensity
            output_path: Output video path
            
        Returns:
            Path to transformed video
        """
        if not zoom_regions:
            # No zooms, just copy
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path
        
        # Get video info
        info = self._get_video_info(video_path)
        width = info["width"]
        height = info["height"]
        duration = info["duration"]
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Build complex filter for zoom effects
        # We'll use crop and scale filters with timeline expressions
        filter_parts = []
        
        # Sort zoom regions by timestamp
        sorted_regions = sorted(zoom_regions, key=lambda r: r.get("timestamp", 0))
        
        # Build zoom filter chain
        # For each zoom region, we crop and scale
        zoom_filters = []
        for i, region in enumerate(sorted_regions):
            start_time = region.get("timestamp", 0)
            zoom_duration = region.get("duration", 2.0)
            intensity = region.get("intensity", 1.5)
            
            # Calculate crop parameters
            crop_width = int(width / intensity)
            crop_height = int(height / intensity)
            crop_x = region.get("x", (width - crop_width) // 2)
            crop_y = region.get("y", (height - crop_height) // 2)
            
            # Create zoom filter for this region
            # Use between() to apply only during the zoom duration
            zoom_filter = (
                f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y},"
                f"scale={width}:{height}"
            )
            
            # Apply only during zoom duration
            if i == 0:
                # First zoom: use if between start and end
                condition = f"between(t,{start_time},{start_time + zoom_duration})"
            else:
                # Subsequent zooms: use if between start and end, and not in previous zoom
                prev_end = sorted_regions[i-1].get("timestamp", 0) + sorted_regions[i-1].get("duration", 2.0)
                condition = f"between(t,{start_time},{start_time + zoom_duration})"
            
            zoom_filters.append((condition, zoom_filter))
        
        # Build final filter complex
        # Use select and overlay to apply zooms at specific times
        # Simplified: apply zooms sequentially
        if len(zoom_filters) == 1:
            # Single zoom - simple case
            condition, zoom_filter = zoom_filters[0]
            filter_complex = f"[0:v]{zoom_filter}[v]"
        else:
            # Multiple zooms - use select filter with timeline
            # For simplicity, we'll use a different approach: split and overlay
            # This is complex, so we'll use a simpler method: apply all zooms as a single filter chain
            filter_parts = []
            for condition, zoom_filter in zoom_filters:
                filter_parts.append(f"if({condition},{zoom_filter},null)")
            
            # Use select filter for conditional zoom
            # Simplified: apply zoom at each timestamp
            filter_complex = "[0:v]null[v]"  # Placeholder - complex implementation
        
        # Use FFmpeg directly for zoom (ScreenArc CLI is unreliable and times out)
        # Build complex filter with timeline expressions for multiple zoom regions
        if not zoom_regions:
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path
        
        logger.info(f"Applying {len(zoom_regions)} zoom regions using FFmpeg")
        
        # Build zoom filter with timeline expressions
        # Use crop and scale with conditional expressions based on time
        filter_parts = []
        
        # Create a filter that applies zoom at specific timestamps
        # Format: crop=w:h:x:y:enable='between(t,start,end)'
        zoom_filters = []
        
        for i, region in enumerate(sorted_regions):
            start_time = region.get("timestamp", 0)
            zoom_duration = region.get("duration", 2.0)
            end_time = start_time + zoom_duration
            intensity = region.get("intensity", 1.5)
            
            # Calculate crop parameters
            crop_width = int(width / intensity)
            crop_height = int(height / intensity)
            crop_x = region.get("x", (width - crop_width) // 2)
            crop_y = region.get("y", (height - crop_height) // 2)
            
            # Create conditional crop filter for this zoom region
            # Use enable expression to apply zoom only during this time window
            crop_filter = f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y}:enable='between(t,{start_time},{end_time})'"
            scale_filter = f"scale={width}:{height}"
            
            if i == 0:
                # First zoom: apply crop conditionally, then scale
                zoom_filters.append(f"[0:v]{crop_filter}[v{i}];[v{i}]{scale_filter}[v{i}_scaled]")
            else:
                # Subsequent zooms: apply to previous output
                prev_output = f"[v{i-1}_scaled]" if i > 1 else "[v0_scaled]"
                zoom_filters.append(f"{prev_output}{crop_filter}[v{i}];[v{i}]{scale_filter}[v{i}_scaled]")
        
        # Build FFmpeg filter for dynamic zoom effects
        # Use crop and scale with conditional application
        # For multiple zooms, we'll apply them sequentially using split and overlay
        
        # Get video FPS for timing calculations
        info = self._get_video_info(video_path)
        fps = info["fps"]
        
        # Build filter chain: for each zoom region, split video, apply zoom, then overlay conditionally
        if len(sorted_regions) == 1:
            # Single zoom - simpler case
            region = sorted_regions[0]
            start_time = region.get("timestamp", 0)
            zoom_duration = region.get("duration", 2.0)
            intensity = region.get("intensity", 1.5)
            
            crop_width = int(width / intensity)
            crop_height = int(height / intensity)
            crop_x = region.get("x", (width - crop_width) // 2)
            crop_y = region.get("y", (height - crop_height) // 2)
            
            # Use crop with scale - apply for the zoom duration
            # Split video, crop one branch, then use overlay with enable
            filter_complex = (
                f"[0:v]split=2[base][zoom_input];"
                f"[zoom_input]crop={crop_width}:{crop_height}:{crop_x}:{crop_y},scale={width}:{height}[zoomed];"
                f"[base][zoomed]overlay=0:0:enable='between(t,{start_time},{start_time + zoom_duration})'[v]"
            )
        else:
            # Multiple zooms: chain them together
            # Start with base video
            filter_parts = ["[0:v]"]
            current_stream = "base0"
            filter_parts[0] = f"[0:v]split=2[{current_stream}][zoom0_input]"
            
            for i, region in enumerate(sorted_regions):
                start_time = region.get("timestamp", 0)
                zoom_duration = region.get("duration", 2.0)
                intensity = region.get("intensity", 1.5)
                
                crop_width = int(width / intensity)
                crop_height = int(height / intensity)
                crop_x = region.get("x", (width - crop_width) // 2)
                crop_y = region.get("y", (height - crop_height) // 2)
                
                # Apply zoom to this region's input
                zoom_input = f"zoom{i}_input"
                zoomed = f"zoomed{i}"
                next_base = f"base{i+1}"
                
                filter_parts.append(
                    f"[{zoom_input}]crop={crop_width}:{crop_height}:{crop_x}:{crop_y},scale={width}:{height}[{zoomed}];"
                    f"[{current_stream}][{zoomed}]overlay=0:0:enable='between(t,{start_time},{start_time + zoom_duration})'[{next_base}]"
                )
                
                # Prepare for next zoom (if any)
                if i < len(sorted_regions) - 1:
                    filter_parts.append(f"[{next_base}]split=2[{next_base}][zoom{i+1}_input]")
                    current_stream = next_base
            
            filter_complex = ";".join(filter_parts).replace(f"[{next_base}]", "[v]")
        
        # Check for audio
        has_audio = self._check_audio_stream(video_path)
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-y", output_path
        ]
        
        if has_audio:
            cmd.extend(["-map", "0:a", "-c:a", "copy"])
        else:
            cmd.extend(["-an"])
        
        try:
            logger.info(f"Applying zoom pattern with FFmpeg (regions: {len(zoom_regions)})")
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Validate output
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise RuntimeError(f"Output file was not created or is empty: {output_path}")
            
            if not self._validate_video_file(output_path):
                raise RuntimeError(f"Output video file is corrupted: {output_path}")
            
            logger.info(f"Zoom pattern applied successfully: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg zoom failed: {e.stderr}")
            # Fallback: apply first zoom as static crop
            if zoom_regions:
                first_zoom = sorted_regions[0]
                intensity = first_zoom.get("intensity", 1.5)
                crop_width = int(width / intensity)
                crop_height = int(height / intensity)
                crop_x = (width - crop_width) // 2
                crop_y = (height - crop_height) // 2
                
                cmd = [
                    "ffmpeg", "-i", video_path,
                    "-vf", f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y},scale={width}:{height}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                    "-c:a", "copy" if has_audio else "-an",
                    "-y", output_path
                ]
                
                subprocess.run(cmd, check=True, capture_output=True, timeout=300)
                logger.warning(f"Applied simplified zoom (first region only) as fallback")
                return output_path
            else:
                import shutil
                shutil.copy2(video_path, output_path)
                return output_path
    
    def apply_subtitles(
        self,
        video_path: str,
        subtitles: List[Dict],
        style: Dict,
        output_path: str
    ) -> str:
        """
        Apply subtitles to video using FFmpeg subtitles filter
        
        Args:
            video_path: Input video path
            subtitles: List of subtitle entries with start, end, text
            style: Subtitle style configuration
            output_path: Output video path
            
        Returns:
            Path to video with subtitles
        """
        if not subtitles:
            # No subtitles, just copy
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create SRT subtitle file
        temp_dir = self._get_temp_dir()
        srt_path = os.path.join(temp_dir, "subtitles.srt")
        
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, subtitle in enumerate(subtitles, 1):
                start = subtitle.get("start", 0)
                end = subtitle.get("end", start + 2)
                text = subtitle.get("text", "")
                
                # Convert seconds to SRT time format (HH:MM:SS,mmm)
                start_time = self._seconds_to_srt_time(start)
                end_time = self._seconds_to_srt_time(end)
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        # Build FFmpeg command with subtitles filter
        # Apply style using subtitles filter options
        font_size = style.get("font_size", "large")
        font_size_map = {"small": 24, "medium": 32, "large": 48}
        size = font_size_map.get(font_size, 32)
        
        font_color = style.get("color", "#FFFFFF")
        bg_color = style.get("background", "#000000")
        
        # Build subtitles filter
        subtitle_filter = f"subtitles={srt_path}"
        
        # Add style options if supported
        # Note: FFmpeg subtitles filter has limited styling, so we use ASS format for better control
        # For now, use simple SRT with force_style
        if style.get("font_weight") == "bold":
            # Use ASS format for better styling
            ass_path = self._create_ass_subtitle_file(subtitles, style, temp_dir)
            subtitle_filter = f"subtitles={ass_path}"
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", subtitle_filter,
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "copy",
            "-y", output_path
        ]
        
        try:
            logger.info(f"Applying subtitles to {video_path}")
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            logger.info(f"Subtitles applied: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Subtitle application failed: {e.stderr}")
            # Fallback: return original
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _create_ass_subtitle_file(
        self,
        subtitles: List[Dict],
        style: Dict,
        temp_dir: str
    ) -> str:
        """Create ASS format subtitle file with styling"""
        ass_path = os.path.join(temp_dir, "subtitles.ass")
        
        # ASS header
        font_name = "Arial"
        font_size = {"small": 24, "medium": 32, "large": 48}.get(style.get("font_size", "medium"), 32)
        primary_color = self._hex_to_ass_color(style.get("color", "#FFFFFF"))
        outline_color = self._hex_to_ass_color(style.get("outline", "#000000"))
        back_color = self._hex_to_ass_color(style.get("background", "#000000"))
        
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write("[Script Info]\n")
            f.write("Title: VCOS Subtitles\n")
            f.write("ScriptType: v4.00+\n\n")
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            f.write(f"Style: Default,{font_name},{font_size},{primary_color},&H00FFFFFF,{outline_color},{back_color},1,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1\n\n")
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            for subtitle in subtitles:
                start = subtitle.get("start", 0)
                end = subtitle.get("end", start + 2)
                text = subtitle.get("text", "")
                
                start_time = self._seconds_to_ass_time(start)
                end_time = self._seconds_to_ass_time(end)
                
                f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n")
        
        return ass_path
    
    def _seconds_to_ass_time(self, seconds: float) -> str:
        """Convert seconds to ASS time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"
    
    def _hex_to_ass_color(self, hex_color: str) -> str:
        """Convert hex color to ASS format (BGR, alpha)"""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            # ASS format: &HAABBGGRR (alpha, blue, green, red)
            return f"&H00{b:02X}{g:02X}{r:02X}"
        return "&H00FFFFFF"
    
    def apply_all_transformations(
        self,
        video_path: str,
        transformations: Dict,
        output_path: str
    ) -> str:
        """
        Apply all transformations in sequence
        
        Args:
            video_path: Input video path
            transformations: Dict with speed, zoom, subtitles
            output_path: Final output path
            
        Returns:
            Path to fully transformed video
        """
        current_path = video_path
        temp_files = []
        
        # Validate input file first
        if not self._validate_video_file(video_path):
            raise ValueError(f"Input video file is invalid or corrupted: {video_path}")
        
        try:
            # Apply speed change if specified
            if "speed" in transformations and transformations["speed"] != 1.0:
                temp_path = os.path.join(self._get_temp_dir(), "speed_temp.mp4")
                try:
                    current_path = self.apply_speed_change(
                        current_path,
                        transformations["speed"],
                        temp_path
                    )
                    if current_path != video_path:
                        temp_files.append(current_path)
                except Exception as e:
                    logger.error(f"Failed to apply speed transformation: {e}")
                    raise
            
            # Apply zoom pattern if specified
            if "zoom_regions" in transformations and transformations["zoom_regions"]:
                temp_path = os.path.join(self._get_temp_dir(), "zoom_temp.mp4")
                current_path = self.apply_zoom_pattern(
                    current_path,
                    transformations["zoom_regions"],
                    temp_path
                )
                if current_path != video_path and current_path not in temp_files:
                    temp_files.append(current_path)
            
            # Apply subtitles if specified
            if "subtitles" in transformations and transformations["subtitles"]:
                temp_path = os.path.join(self._get_temp_dir(), "subtitle_temp.mp4")
                current_path = self.apply_subtitles(
                    current_path,
                    transformations["subtitles"],
                    transformations.get("subtitle_style", {}),
                    temp_path
                )
                if current_path != video_path and current_path not in temp_files:
                    temp_files.append(current_path)
            
            # Copy final result to output path
            if current_path != output_path:
                import shutil
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(current_path, output_path)
            
            # Cleanup temp files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file) and temp_file != output_path:
                        os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Transformation failed: {e}", exc_info=True)
            # Cleanup on error
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception:
                    pass
            raise
