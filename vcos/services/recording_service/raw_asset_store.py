"""
Recording Service - Raw Asset Store
Manages storage of raw recording assets
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def store_raw_asset(video_path: str, metadata: Dict = None) -> str:
    """
    Store raw video asset and metadata
    
    Args:
        video_path: Path to raw video file
        metadata: Optional metadata dictionary
        
    Returns:
        Asset ID
    """
    os.makedirs(settings.RAW_VIDEOS_DIR, exist_ok=True)
    
    # Generate asset ID from file hash
    with open(video_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    asset_id = f"raw_{file_hash[:12]}"
    
    # Copy file to storage (in production, use proper file operations)
    import shutil
    stored_path = os.path.join(settings.RAW_VIDEOS_DIR, f"{asset_id}.mp4")
    shutil.copy2(video_path, stored_path)
    
    # Store metadata
    if metadata:
        metadata_path = os.path.join(settings.RAW_VIDEOS_DIR, f"{asset_id}.json")
        metadata["asset_id"] = asset_id
        metadata["stored_at"] = datetime.now().isoformat()
        metadata["video_path"] = stored_path
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    logger.info(f"Stored raw asset: {asset_id}")
    
    return asset_id

def get_raw_asset(asset_id: str) -> Optional[Dict]:
    """
    Retrieve raw asset metadata
    
    Args:
        asset_id: Asset ID
        
    Returns:
        Asset metadata dictionary or None
    """
    metadata_path = os.path.join(settings.RAW_VIDEOS_DIR, f"{asset_id}.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    with open(metadata_path, 'r') as f:
        return json.load(f)
