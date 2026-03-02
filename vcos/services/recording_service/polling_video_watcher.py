"""
Recording Service - Polling Video Watcher
Fast polling-based video detection (backup to file watcher)
"""

import os
import time
from pathlib import Path
from typing import Callable, Set
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PollingVideoWatcher:
    """Fast polling-based video watcher as backup"""
    
    def __init__(self, watch_directories: list, on_video_saved: Callable, poll_interval: float = 0.5, min_age_seconds: int = 5, max_age_seconds: int = 180, start_time: float = None):
        self.watch_directories = [Path(d) for d in watch_directories]
        self.on_video_saved = on_video_saved
        self.poll_interval = poll_interval
        self.processed_files: Set[str] = set()
        self.running = False
        self.min_age_seconds = min_age_seconds  # Wait 5 seconds for file to be written
        self.max_age_seconds = max_age_seconds  # Only process files created in last 3 minutes
        self.start_time = start_time or time.time()  # Only process files created after watcher started
    
    def start(self):
        """Start polling"""
        import threading
        
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        logger.info(f"Polling watcher started on {len(self.watch_directories)} directories (interval: {self.poll_interval}s)")
    
    def _poll_loop(self):
        """Poll directories for new videos"""
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
        
        while self.running:
            try:
                for watch_dir in self.watch_directories:
                    if not watch_dir.exists():
                        continue
                    
                    # Find all video files
                    for file_path in watch_dir.iterdir():
                        if not file_path.is_file():
                            continue
                        
                        if file_path.suffix.lower() not in video_extensions:
                            continue
                        
                        # CRITICAL: Skip variant files to prevent infinite reprocessing loop
                        if '_variant_' in file_path.name or '_optimized' in file_path.name:
                            continue
                        
                        file_key = str(file_path)
                        if file_key in self.processed_files:
                            continue
                        
                        # Check if file is complete and NEW (created after watcher started)
                        try:
                            file_stat = file_path.stat()
                            file_created_time = file_stat.st_mtime
                            current_time = time.time()
                            file_age = current_time - file_created_time
                            
                            # CRITICAL: Only process files created AFTER watcher started
                            if file_created_time < self.start_time:
                                continue  # Skip files created before watcher started
                            
                            # Skip if file is too new (less than min_age_seconds) - still being written
                            if file_age < self.min_age_seconds:
                                continue  # Wait for file to finish writing
                            
                            if file_stat.st_size > 0:
                                # Quick check if file is stable
                                size1 = file_stat.st_size
                                time.sleep(0.1)
                                size2 = file_path.stat().st_size
                                
                                if size1 == size2:
                                    # File is stable and recent, process it
                                    self.processed_files.add(file_key)
                                    logger.info(f"Polling detected new video: {file_path} (age: {file_age:.1f}s)")
                                    self.on_video_saved(str(file_path))
                        except (OSError, PermissionError):
                            pass  # File might be locked, skip for now
                
                time.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(self.poll_interval)
    
    def stop(self):
        """Stop polling"""
        self.running = False
        logger.info("Polling watcher stopped")
