#!/usr/bin/env python3
"""
Sync ScreenArc Videos
Copies videos from ScreenArc default directory to VCOS watched directory
"""

import sys
import shutil
from pathlib import Path
import os

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config.settings import settings

def main():
    # ScreenArc default directory
    screenarc_dir = Path(os.path.expanduser("~")) / ".screenarc"
    vcos_dir = Path(settings.RAW_VIDEOS_DIR).resolve()
    
    print("=" * 60)
    print("ScreenArc Video Sync")
    print("=" * 60)
    print(f"\nSource: {screenarc_dir}")
    print(f"Destination: {vcos_dir}")
    print()
    
    if not screenarc_dir.exists():
        print("ScreenArc directory doesn't exist. Nothing to sync.")
        return
    
    # Ensure VCOS directory exists
    vcos_dir.mkdir(parents=True, exist_ok=True)
    
    # Find video files
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
    video_files = [
        f for f in screenarc_dir.iterdir()
        if f.is_file() and f.suffix.lower() in video_extensions
    ]
    
    if not video_files:
        print("No video files found in ScreenArc directory.")
        return
    
    print(f"Found {len(video_files)} video file(s):\n")
    
    copied = 0
    for video_file in video_files:
        dest_file = vcos_dir / video_file.name
        
        if dest_file.exists():
            print(f"  {video_file.name} - Already exists in VCOS directory")
            continue
        
        try:
            shutil.copy2(video_file, dest_file)
            print(f"  {video_file.name} - Copied to VCOS directory")
            copied += 1
        except Exception as e:
            print(f"  {video_file.name} - Error: {e}")
    
    print(f"\nCopied {copied} new video(s) to VCOS directory.")
    print(f"\nVideos in VCOS directory will be automatically processed.")

if __name__ == "__main__":
    main()
