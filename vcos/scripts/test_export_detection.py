#!/usr/bin/env python3
"""
Test script to verify export watcher is detecting files correctly
"""

import sys
import time
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recording_service.export_watcher import ExportVideoWatcher
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_callback(video_path: str):
    """Test callback when video is detected"""
    logger.info("=" * 60)
    logger.info(f"TEST: Video detected by export watcher: {video_path}")
    logger.info("=" * 60)

def main():
    print("=" * 60)
    print("Export Watcher Test")
    print("=" * 60)
    print()
    print("This script will monitor for exported videos.")
    print("Export a video from ScreenArc and it should be detected.")
    print()
    
    # Create watcher
    watcher = ExportVideoWatcher(test_callback, start_time=time.time())
    
    print(f"Watching directories:")
    for d in watcher.watch_directories:
        print(f"  - {d}")
    print()
    
    # Start watcher
    watcher.start()
    print("Export watcher started. Waiting for exports...")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        watcher.stop()

if __name__ == "__main__":
    main()
