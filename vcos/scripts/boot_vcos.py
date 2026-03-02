#!/usr/bin/env python3
"""
VCOS Boot Script
Boots up ScreenArc and watches for videos to process through pipeline
"""

import sys
import time
import signal
import os
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recording_service.screenarc_launcher import screenarc_launcher
from services.recording_service.video_watcher import VideoWatcher
from services.auto_pipeline_processor import process_video_sync
from shared.config.settings import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global watcher
video_watcher = None

def on_video_saved(video_path: str):
    """Called when a new video is saved"""
    logger.info("=" * 60)
    logger.info(f"New video detected: {video_path}")
    logger.info("=" * 60)
    
    # Process through pipeline
    result = process_video_sync(video_path)
    
    if result["success"]:
        logger.info(f"Pipeline started! Job ID: {result['job_id']}")
        logger.info(f"   Video will be optimized for virality")
    else:
        logger.error(f"Pipeline failed: {result.get('error')}")

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("\n\nShutting down VCOS...")
    if video_watcher:
        video_watcher.stop()
    sys.exit(0)

def main():
    """Main boot function"""
    print("=" * 60)
    print("VCOS Boot System")
    print("=" * 60)
    print()
    
    # Check ScreenArc setup
    print("Checking ScreenArc setup...")
    setup = screenarc_launcher.check_setup()
    
    if not setup["ready"]:
        print("WARNING: ScreenArc not ready:")
        if not setup["node_available"]:
            print("   - Node.js not found. Install Node.js to use ScreenArc.")
        if not setup["screenarc_exists"]:
            print("   - ScreenArc directory not found.")
        print()
        print("You can still use VCOS, but ScreenArc recording won't be available.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    else:
        print("OK: ScreenArc ready")
    
    # Set output directory
    output_dir = settings.RAW_VIDEOS_DIR
    print(f"\nVideo output directory: {output_dir}")
    print(f"   Videos saved here will be automatically processed")
    
    # Launch ScreenArc
    if setup["ready"]:
        print("\nLaunching ScreenArc...")
        launch_result = screenarc_launcher.launch_recording(output_dir)
        
        if launch_result["success"]:
            print(f"OK: {launch_result['message']}")
        else:
            print(f"WARNING: {launch_result.get('error')}")
            print("   You can manually record videos and save them to the output directory")
    
    # Start video watcher
    print(f"\nStarting video watcher on: {output_dir}")
    print("   Waiting for videos to process...")
    print()
    
    global video_watcher
    video_watcher = VideoWatcher(output_dir, on_video_saved)
    video_watcher.start()
    
    # Also start fast polling watcher as backup (catches files file watcher might miss)
    from services.recording_service.polling_video_watcher import PollingVideoWatcher
    import os
    import time
    home_dir = str(Path(os.path.expanduser("~")))
    screenarc_dir = str(Path(os.path.expanduser("~")) / ".screenarc")
    polling_dirs = [output_dir, screenarc_dir, home_dir]
    
    # Record start time - only process files created AFTER this time
    start_time = time.time()
    
    polling_watcher = PollingVideoWatcher(
        polling_dirs, 
        on_video_saved, 
        poll_interval=0.5,
        min_age_seconds=5,  # Wait 5 seconds for file to finish writing
        max_age_seconds=180,  # Only process files created in last 3 minutes
        start_time=start_time  # Only process NEW files
    )
    polling_watcher.start()
    logger.info("Fast polling watcher started as backup (only processing NEW files created after start)")
    
    # Also watch for exported videos from ScreenArc (when user clicks export)
    from services.recording_service.export_watcher import ExportVideoWatcher
    export_watcher = ExportVideoWatcher(on_video_saved, start_time=start_time)
    export_watcher.start()
    logger.info(f"Export watcher started (watching Downloads, Desktop, and VCOS exports directory)")
    logger.info(f"  Start time: {time.ctime(start_time)}")
    logger.info(f"  Will process files modified after: {time.ctime(start_time)}")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("VCOS is running!")
    print("=" * 60)
    print()
    print("Instructions:")
    print("   1. Record your video in ScreenArc (or save any video to the output directory)")
    print("   2. Save the video to the output directory")
    print("   3. VCOS will automatically detect and process it through the pipeline")
    print("   4. Optimized videos will be created with variants")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
