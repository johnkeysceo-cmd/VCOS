"""
Recording Service - Scene Change Detector
Detects scene changes and significant visual transitions
"""

import cv2
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def detect_scene_changes(video_path: str, threshold: float = 0.3) -> List[Dict]:
    """
    Detect scene changes in video
    
    Args:
        video_path: Path to video file
        threshold: Change detection threshold (0.0 to 1.0)
        
    Returns:
        List of scene change timestamps
    """
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return []
        
        scene_changes = []
        prev_frame = None
        frame_count = 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to grayscale for comparison
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(prev_frame, gray)
                diff_score = np.mean(diff) / 255.0
                
                if diff_score > threshold:
                    timestamp = frame_count / fps
                    scene_changes.append({
                        "timestamp": timestamp,
                        "frame": frame_count,
                        "change_score": diff_score
                    })
                    logger.debug(f"Scene change detected at {timestamp:.2f}s")
            
            prev_frame = gray
            frame_count += 1
        
        cap.release()
        logger.info(f"Detected {len(scene_changes)} scene changes")
        
        return scene_changes
        
    except Exception as e:
        logger.error(f"Error detecting scene changes: {e}")
        return []
