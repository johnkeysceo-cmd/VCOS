"""
Recording Service - Export Video Watcher
Watches for exported videos from ScreenArc (when user clicks export button)
"""

import os
import time
from pathlib import Path
from typing import Callable, Set
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ExportVideoWatcher:
    """Watches for exported videos from ScreenArc editor"""
    
    def __init__(self, on_export_saved: Callable, watch_directories: list = None, start_time: float = None):
        """
        Initialize export watcher
        
        Args:
            on_export_saved: Callback when exported video is detected
            watch_directories: Directories to watch (default: Downloads, Desktop, VCOS exports)
            start_time: Only process exports created after this time
        """
        self.on_export_saved = on_export_saved
        self.start_time = start_time or time.time()
        self.processed_files: Set[str] = set()
        
        # Default watch directories: Downloads, Desktop, VCOS export directory
        if watch_directories is None:
            home = Path(os.path.expanduser("~"))
            # Get VCOS root (go up from services/recording_service/export_watcher.py to vcos root)
            # export_watcher.py is at: vcos/services/recording_service/export_watcher.py
            # So parent.parent.parent = vcos root
            vcos_root = Path(__file__).parent.parent.parent
            vcos_exports = vcos_root / "data" / "exports"
            vcos_exports.mkdir(parents=True, exist_ok=True)
            
            watch_directories = [
                str(home / "Downloads"),
                str(home / "Desktop"),
                str(home),  # Also watch home directory (ScreenArc sometimes saves here)
                str(vcos_exports.resolve())  # Use absolute path
            ]
            
            logger.info(f"Export watcher will monitor: {watch_directories}")
        
        # Store home directory for filtering
        self.home_dir = Path(os.path.expanduser("~"))
        self.watch_directories = [Path(d) for d in watch_directories]
        self.running = False
    
    def start(self):
        """Start watching for exported videos"""
        import threading
        
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        logger.info(f"Export watcher started on {len(self.watch_directories)} directories (only NEW exports)")
    
    def _poll_loop(self):
        """Poll directories for exported videos"""
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.gif'}
        
        while self.running:
            try:
                for watch_dir in self.watch_directories:
                    if not watch_dir.exists():
                        logger.debug(f"Export watch directory does not exist: {watch_dir}")
                        continue
                    
                    # Find all video files
                    try:
                        files = list(watch_dir.iterdir())
                    except (OSError, PermissionError) as e:
                        logger.debug(f"Cannot read directory {watch_dir}: {e}")
                        continue
                    
                    for file_path in files:
                        if not file_path.is_file():
                            continue
                        
                        if file_path.suffix.lower() not in video_extensions:
                            continue
                        
                        # Skip files created by VCOS pipeline (not original exports)
                        # BUT: Only skip if it's in the VCOS data directory, not user's Downloads/Desktop
                        file_stem_lower = file_path.stem.lower()
                        file_path_str_lower = str(file_path).lower()
                        is_in_vcos_data = "vcos" in file_path_str_lower and ("data" in file_path_str_lower or "exports" in file_path_str_lower)
                        
                        if is_in_vcos_data and ("_optimized" in file_stem_lower or "_vcos_processed" in file_stem_lower or "_variant_" in file_stem_lower):
                            logger.debug(f"Skipping pipeline-generated file in VCOS data: {file_path.name}")
                            continue
                        
                        # Allow ScreenArc- prefixed files from Downloads/Desktop/Home (user exports)
                        # Only skip if it's clearly a pipeline output
                        # For home directory, only process ScreenArc-*.mp4 files (actual exports)
                        is_home_dir = str(file_path.parent).lower() == str(self.home_dir).lower()
                        if is_home_dir and not file_path.name.startswith("ScreenArc-"):
                            logger.debug(f"Skipping non-ScreenArc file in home directory: {file_path.name}")
                            continue
                        
                        if not is_in_vcos_data and "_optimized" in file_stem_lower and file_stem_lower.count("_optimized") > 1:
                            logger.debug(f"Skipping multi-optimized file: {file_path.name}")
                            continue
                        
                        # Skip if already processed
                        file_key = str(file_path.resolve())  # Use absolute path
                        if file_key in self.processed_files:
                            continue
                        
                        # Check if file is NEW (created/modified after watcher started)
                        try:
                            file_stat = file_path.stat()
                            # Use mtime (modification time) which is more reliable for exports
                            file_modified_time = file_stat.st_mtime
                            current_time = time.time()
                            file_age = current_time - file_modified_time
                            
                            # Only process files created/modified AFTER watcher started
                            if file_modified_time < self.start_time:
                                logger.debug(f"Skipping old file: {file_path.name} (modified: {file_modified_time:.1f}, start: {self.start_time:.1f})")
                                continue
                            
                            # Wait a bit to ensure file is complete (exports can be large)
                            # But don't wait too long - exports can take time, so we check stability instead
                            if file_age < 1:  # Wait 1 second minimum for export to start
                                logger.debug(f"File too new, waiting: {file_path.name} (age: {file_age:.1f}s)")
                                continue
                            
                            # Check if file is stable (not still being written)
                            size1 = file_stat.st_size
                            # Skip empty or very small files (likely incomplete exports)
                            if size1 < 1024:  # Less than 1KB is likely incomplete
                                logger.debug(f"File too small (likely incomplete): {file_path.name} (size: {size1} bytes)")
                                continue
                            
                            # Wait a bit and check if file size is stable
                            time.sleep(0.5)  # Wait 0.5 seconds for file to stabilize
                            try:
                                size2 = file_path.stat().st_size
                            except (OSError, PermissionError):
                                continue  # File might be locked
                            
                            if size1 == size2 and size2 >= 1024:
                                # File is stable and has reasonable size - process it
                                self.processed_files.add(file_key)
                                logger.info(f"Export detected: {file_path} (age: {file_age:.1f}s, size: {size1 / 1024 / 1024:.1f} MB)")
                                logger.info(f"  Calling on_export_saved callback with: {str(file_path.resolve())}")
                                try:
                                    self.on_export_saved(str(file_path.resolve()))
                                    logger.info(f"  Successfully triggered pipeline for: {file_path.name}")
                                except Exception as e:
                                    logger.error(f"  Error in on_export_saved callback: {e}", exc_info=True)
                            else:
                                logger.debug(f"File still being written or too small: {file_path.name} (size: {size1} -> {size2} bytes)")
                        except (OSError, PermissionError) as e:
                            logger.debug(f"Error checking file {file_path}: {e}")
                            pass  # File might be locked, skip for now
                
                time.sleep(1.0)  # Poll every 1 second (faster detection)
            except Exception as e:
                logger.error(f"Error in export polling loop: {e}", exc_info=True)
                time.sleep(2.0)
    
    def stop(self):
        """Stop watching"""
        self.running = False
        logger.info("Export watcher stopped")
