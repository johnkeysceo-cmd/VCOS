"""
Retention Optimizer - Optimized Asset Store
Manages storage of optimized video assets
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def store_optimized_asset(video_path: str, metadata: Dict = None) -> str:
    """
    Store optimized video asset
    
    Args:
        video_path: Path to optimized video
        metadata: Optimization metadata
        
    Returns:
        Asset ID
    """
    os.makedirs(settings.OPTIMIZED_VIDEOS_DIR, exist_ok=True)
    
    # Generate asset ID
    with open(video_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    asset_id = f"opt_{file_hash[:12]}"
    
    # Copy file
    import shutil
    stored_path = os.path.join(settings.OPTIMIZED_VIDEOS_DIR, f"{asset_id}.mp4")
    shutil.copy2(video_path, stored_path)
    
    # Store metadata
    if metadata:
        metadata_path = os.path.join(settings.OPTIMIZED_VIDEOS_DIR, f"{asset_id}.json")
        metadata["asset_id"] = asset_id
        metadata["stored_at"] = datetime.now().isoformat()
        metadata["video_path"] = stored_path
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    logger.info(f"Stored optimized asset: {asset_id}")
    
    return asset_id

def get_optimized_asset(asset_id: str) -> Optional[Dict]:
    """Retrieve optimized asset metadata"""
    metadata_path = os.path.join(settings.OPTIMIZED_VIDEOS_DIR, f"{asset_id}.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    with open(metadata_path, 'r') as f:
        return json.load(f)
