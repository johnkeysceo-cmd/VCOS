"""
Variant Generator - Variant Registry
Tracks and manages all generated variants
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def register_variant(base_video_id: str, variant_config: Dict, output_path: str) -> str:
    """
    Register a generated variant
    
    Args:
        base_video_id: ID of base video
        variant_config: Variant configuration (hook, pacing, zoom, etc.)
        output_path: Path to variant video
        
    Returns:
        Variant ID
    """
    os.makedirs(settings.VARIANTS_DIR, exist_ok=True)
    
    # Generate variant ID
    variant_key = f"{base_video_id}_{hashlib.md5(json.dumps(variant_config, sort_keys=True).encode()).hexdigest()[:8]}"
    variant_id = f"variant_{variant_key}"
    
    # Store variant metadata
    metadata = {
        "variant_id": variant_id,
        "base_video_id": base_video_id,
        "config": variant_config,
        "output_path": output_path,
        "created_at": datetime.now().isoformat()
    }
    
    metadata_path = os.path.join(settings.VARIANTS_DIR, f"{variant_id}.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Registered variant: {variant_id}")
    
    return variant_id

def get_variants_for_base(base_video_id: str) -> List[Dict]:
    """
    Get all variants for a base video
    
    Args:
        base_video_id: Base video ID
        
    Returns:
        List of variant metadata
    """
    variants = []
    
    if not os.path.exists(settings.VARIANTS_DIR):
        return variants
    
    for filename in os.listdir(settings.VARIANTS_DIR):
        if filename.endswith(".json"):
            metadata_path = os.path.join(settings.VARIANTS_DIR, filename)
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    if metadata.get("base_video_id") == base_video_id:
                        variants.append(metadata)
            except Exception as e:
                logger.warning(f"Error reading variant metadata {filename}: {e}")
    
    return variants

def generate_variant_tree(base_video_id: str) -> Dict:
    """
    Generate variant tree structure
    
    Args:
        base_video_id: Base video ID
        
    Returns:
        Tree structure of variants
    """
    variants = get_variants_for_base(base_video_id)
    
    # Group by variant dimensions
    tree = {
        "base_video_id": base_video_id,
        "hook_variants": {},
        "pacing_variants": {},
        "zoom_variants": {},
        "style_variants": {}
    }
    
    for variant in variants:
        config = variant.get("config", {})
        
        # Group by hook
        hook = config.get("hook_type", "default")
        if hook not in tree["hook_variants"]:
            tree["hook_variants"][hook] = {}
        
        # Group by pacing
        pacing = config.get("pacing_speed", 1.0)
        if pacing not in tree["hook_variants"][hook]:
            tree["hook_variants"][hook][pacing] = []
        
        tree["hook_variants"][hook][pacing].append(variant["variant_id"])
    
    return tree
