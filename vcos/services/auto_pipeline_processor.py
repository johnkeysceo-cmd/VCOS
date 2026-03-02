"""
Auto Pipeline Processor
Automatically processes videos through VCOS pipeline when detected
"""

import os
import asyncio
from pathlib import Path
from typing import Dict
import sys
from pathlib import Path
# Add vcos to path if not already there
vcos_path = Path(__file__).parent.parent.parent
if str(vcos_path) not in sys.path:
    sys.path.insert(0, str(vcos_path))

from orchestration.pipeline_manager import start_batch_pipeline
import logging

logger = logging.getLogger(__name__)

async def process_video_through_pipeline(video_path: str) -> Dict:
    """
    Process a video through the full VCOS pipeline
    
    Args:
        video_path: Path to the input video
        
    Returns:
        Processing result
    """
    logger.info(f"Starting automatic pipeline processing for: {video_path}")
    
    # Convert to absolute path
    video_path_abs = str(Path(video_path).resolve())
    
    # Build pipeline payload
    payload = {
        "input_video": video_path_abs,
        "topic": "Auto-generated from recording",  # Could be extracted from video metadata
        "num_variants": 10,
        "platforms": ["tiktok", "instagram", "youtube"],
        "auto_process": True
    }
    
    try:
        # Start pipeline
        job_id = await start_batch_pipeline(payload)
        
        logger.info(f"Pipeline started with job_id: {job_id}")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": f"Video is being processed through VCOS pipeline",
            "video_path": video_path
        }
    except Exception as e:
        logger.error(f"Pipeline processing failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "video_path": video_path
        }

def process_video_sync(video_path: str) -> Dict:
    """Synchronous wrapper for async processing"""
    return asyncio.run(process_video_through_pipeline(video_path))
