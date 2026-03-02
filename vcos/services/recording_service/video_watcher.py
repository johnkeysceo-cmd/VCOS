"""
Recording Service - Video Watcher
Watches directory for new videos and triggers pipeline
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class VideoFileHandler(FileSystemEventHandler):
    """Handles new video file events"""
    
    def __init__(self, on_video_saved: Callable, min_age_seconds: int = 5, max_age_seconds: int = 180, start_time: float = None):
        self.on_video_saved = on_video_saved
        self.processed_files = set()
        self.min_age_seconds = min_age_seconds  # Wait 5 seconds for file to be written
        self.max_age_seconds = max_age_seconds  # Only process files created in last 3 minutes
        self.start_time = start_time or time.time()  # Only process files created after watcher started
    
    def on_created(self, event):
        """Called when a new file is created"""
        self._handle_file_event(event, "created")
    
    def on_modified(self, event):
        """Called when a file is modified (ScreenArc might save this way)"""
        self._handle_file_event(event, "modified")
    
    def _handle_file_event(self, event, event_type: str):
        """Handle file system events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's a video file
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
        if file_path.suffix.lower() not in video_extensions:
            return
        
        # CRITICAL: Skip variant files to prevent infinite reprocessing loop
        if '_variant_' in file_path.name or '_optimized' in file_path.name:
            logger.debug(f"Skipping variant/optimized file: {file_path.name}")
            return
        
        # Avoid processing same file twice
        file_key = str(file_path)
        if file_key in self.processed_files:
            return
        
        # Check file age - only process NEW files created AFTER watcher started
        try:
            file_stat = file_path.stat()
            file_created_time = file_stat.st_mtime
            current_time = time.time()
            file_age = current_time - file_created_time
            
            # CRITICAL: Only process files created AFTER watcher started
            if file_created_time < self.start_time:
                logger.debug(f"Skipping file created before watcher started: {file_path.name} (created: {file_created_time:.1f}, start: {self.start_time:.1f})")
                return
            
            # Skip if file is too new (less than min_age_seconds = 5 seconds) - still being written
            if file_age < self.min_age_seconds:
                logger.debug(f"File too new, waiting: {file_path.name} (age: {file_age:.1f}s)")
                return
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not check file age: {e}")
            return
        
        # Wait for file to be fully written (ScreenArc might still be writing)
        # Faster detection - minimal wait, process immediately if file looks ready
        max_wait = 2  # Wait up to 2 seconds
        wait_interval = 0.1  # Check every 100ms
        waited = 0
        stable_count = 0  # Count how many times size stayed the same
        
        while waited < max_wait:
            try:
                if file_path.exists():
                    size = file_path.stat().st_size
                    if size > 0:
                        # File has content, check if it's still growing
                        time.sleep(wait_interval)
                        new_size = file_path.stat().st_size
                        
                        if new_size == size:
                            stable_count += 1
                            # If size stable for 2 checks (200ms), assume complete
                            if stable_count >= 2:
                                break
                        else:
                            stable_count = 0  # Reset if size changed
                waited += wait_interval
                time.sleep(wait_interval)
            except (OSError, PermissionError):
                # File might be locked, wait a bit
                time.sleep(wait_interval)
                waited += wait_interval
        
        # Final check
        try:
            if not file_path.exists() or file_path.stat().st_size == 0:
                logger.warning(f"File {file_path} doesn't exist or is empty after waiting")
                return
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not access file {file_path}: {e}")
            return
        
        # Mark as processed
        self.processed_files.add(file_key)
        logger.info(f"New video detected ({event_type}): {file_path} ({file_path.stat().st_size} bytes)")
        
        # Trigger pipeline
        self.on_video_saved(str(file_path))

class VideoWatcher:
    """Watches directory for new videos"""
    
    def __init__(self, watch_directory: str, on_video_saved: Callable, watch_screenarc_default: bool = True):
        self.watch_directory = Path(watch_directory)
        self.on_video_saved = on_video_saved
        self.observer = None
        self.observer_screenarc = None
        self.observer_home = None
        self.running = False
        self.watch_screenarc_default = watch_screenarc_default
        self.poll_interval = 1.0  # Poll every 1 second for faster detection
    
    def start(self):
        """Start watching directory"""
        if not WATCHDOG_AVAILABLE:
            logger.error("watchdog not installed. Install with: pip install watchdog")
            return
        
        if self.running:
            logger.warning("Video watcher already running")
            return
        
        # Create directory if it doesn't exist
        self.watch_directory.mkdir(parents=True, exist_ok=True)
        
        # Record start time - only process files created AFTER this time
        start_time = time.time()
        
        event_handler = VideoFileHandler(self.on_video_saved, min_age_seconds=5, max_age_seconds=180, start_time=start_time)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_directory), recursive=False)
        self.observer.start()
        self.running = True
        
        logger.info(f"Video watcher started on: {self.watch_directory.absolute()} (only processing NEW files created after start)")
        
        # Also watch ScreenArc's default directory and user home directory as fallback
        if self.watch_screenarc_default:
            import os
            home_dir = Path(os.path.expanduser("~"))
            
            # Watch .screenarc directory
            screenarc_default = home_dir / ".screenarc"
            if screenarc_default != self.watch_directory:
                try:
                    screenarc_default.mkdir(parents=True, exist_ok=True)
                    event_handler_screenarc = VideoFileHandler(self.on_video_saved, min_age_seconds=5, max_age_seconds=180, start_time=start_time)
                    self.observer_screenarc = Observer()
                    self.observer_screenarc.schedule(event_handler_screenarc, str(screenarc_default), recursive=False)
                    self.observer_screenarc.start()
                    logger.info(f"Also watching ScreenArc default directory: {screenarc_default.absolute()}")
                except Exception as e:
                    logger.warning(f"Could not watch ScreenArc default directory: {e}")
            
            # Watch user home directory (ScreenArc sometimes saves directly there)
            if home_dir != self.watch_directory and home_dir != screenarc_default:
                try:
                    event_handler_home = VideoFileHandler(self.on_video_saved, min_age_seconds=5, max_age_seconds=180, start_time=start_time)
                    self.observer_home = Observer()
                    self.observer_home.schedule(event_handler_home, str(home_dir), recursive=False)
                    self.observer_home.start()
                    logger.info(f"Also watching user home directory: {home_dir.absolute()}")
                except Exception as e:
                    logger.warning(f"Could not watch home directory: {e}")
        
        # Log existing files in directory for debugging
        existing_videos = [
            f for f in self.watch_directory.iterdir()
            if f.is_file() and f.suffix.lower() in {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
        ]
        if existing_videos:
            logger.info(f"Found {len(existing_videos)} existing video(s) in VCOS directory (will not auto-process)")
    
    def stop(self):
        """Stop watching directory"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.observer_screenarc:
            self.observer_screenarc.stop()
            self.observer_screenarc.join()
        if self.observer_home:
            self.observer_home.stop()
            self.observer_home.join()
        self.running = False
        logger.info("Video watcher stopped")
