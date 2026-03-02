"""
Title & Thumbnail Engine - Thumbnail Text Generator
Generates text overlays for thumbnails
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def generate_thumbnail_text(title: str, max_words: int = 5) -> str:
    """
    Generate concise text for thumbnail
    
    Args:
        title: Full title
        max_words: Maximum words in thumbnail text
        
    Returns:
        Thumbnail text
    """
    words = title.split()[:max_words]
    return " ".join(words)

def generate_thumbnail_variants(title: str) -> List[Dict]:
    """
    Generate thumbnail text variants
    
    Args:
        title: Base title
        
    Returns:
        List of thumbnail text options
    """
    variants = []
    
    # Short version (3-5 words)
    short = generate_thumbnail_text(title, 5)
    variants.append({
        "text": short,
        "length": len(short),
        "style": "short"
    })
    
    # Ultra short (2-3 words)
    ultra_short = generate_thumbnail_text(title, 3)
    variants.append({
        "text": ultra_short,
        "length": len(ultra_short),
        "style": "ultra_short"
    })
    
    # With emoji
    if "🔥" not in title:
        variants.append({
            "text": f"🔥 {short}",
            "length": len(short) + 2,
            "style": "with_emoji"
        })
    
    return variants
