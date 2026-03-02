#!/usr/bin/env python3
"""
Manual Video Processor
Manually trigger pipeline for a video file
"""

import sys
import argparse
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.auto_pipeline_processor import process_video_sync
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Manually process a video through VCOS pipeline")
    parser.add_argument("video_path", help="Path to video file")
    
    args = parser.parse_args()
    
    video_path = Path(args.video_path)
    
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    print(f"Processing video: {video_path}")
    print("=" * 60)
    
    result = process_video_sync(str(video_path))
    
    if result["success"]:
        print(f"\nSuccess! Pipeline started.")
        print(f"Job ID: {result['job_id']}")
        print(f"Video will be optimized for virality")
    else:
        print(f"\nError: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
