#!/usr/bin/env python3
"""
Check Videos Script
Lists videos in watched directory and can manually trigger processing
"""

import sys
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config.settings import settings
import os

def main():
    watched_dir = Path(settings.RAW_VIDEOS_DIR)
    
    print("=" * 60)
    print("VCOS Video Checker")
    print("=" * 60)
    print(f"\nWatched directory: {watched_dir.absolute()}")
    print(f"Directory exists: {watched_dir.exists()}")
    print()
    
    if not watched_dir.exists():
        print("Directory doesn't exist. Creating it...")
        watched_dir.mkdir(parents=True, exist_ok=True)
        print("Directory created.")
        return
    
    # List all video files
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
    video_files = [
        f for f in watched_dir.iterdir()
        if f.is_file() and f.suffix.lower() in video_extensions
    ]
    
    if not video_files:
        print("No video files found in watched directory.")
        print("\nTo process a video manually:")
        print(f"  python scripts/manual_process_video.py <path_to_video>")
        return
    
    print(f"Found {len(video_files)} video file(s):\n")
    
    for i, video_file in enumerate(video_files, 1):
        size_mb = video_file.stat().st_size / (1024 * 1024)
        print(f"{i}. {video_file.name}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Modified: {video_file.stat().st_mtime}")
        print()
    
    print("To process a video manually:")
    print(f"  python scripts/manual_process_video.py \"{video_files[0]}\"")

if __name__ == "__main__":
    main()
