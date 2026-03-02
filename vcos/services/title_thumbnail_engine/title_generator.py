"""
Title & Thumbnail Engine - Title Generator
Generates optimized titles per platform
"""

from services.title_thumbnail_engine.curiosity_density_model import calculate_curiosity_density
from services.title_thumbnail_engine.compression_efficiency_model import calculate_compression_efficiency
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Platform-specific title constraints
PLATFORM_CONSTRAINTS = {
    "tiktok": {
        "max_length": 150,
        "optimal_length": 80,
        "hashtag_support": True
    },
    "instagram": {
        "max_length": 125,
        "optimal_length": 70,
        "hashtag_support": True
    },
    "youtube": {
        "max_length": 100,
        "optimal_length": 60,
        "hashtag_support": False
    }
}

def generate_title(hook_text: str, platform: str = "tiktok") -> str:
    """
    Generate optimized title from hook
    
    Args:
        hook_text: Hook text
        platform: Target platform
        
    Returns:
        Optimized title
    """
    constraints = PLATFORM_CONSTRAINTS.get(platform, PLATFORM_CONSTRAINTS["tiktok"])
    
    # Use hook as base, optimize for platform
    title = hook_text
    
    # Truncate if too long
    if len(title) > constraints["max_length"]:
        title = title[:constraints["max_length"] - 3] + "..."
    
    # Add platform-specific optimizations
    if platform == "youtube" and len(title) < constraints["optimal_length"]:
        # YouTube titles can be longer, add context
        title = f"{title} | Tutorial"
    
    return title

def score_title(title: str, platform: str = "tiktok") -> Dict:
    """
    Score title for platform
    
    Args:
        title: Title text
        platform: Target platform
        
    Returns:
        Scoring dictionary
    """
    constraints = PLATFORM_CONSTRAINTS.get(platform, PLATFORM_CONSTRAINTS["tiktok"])
    
    curiosity = calculate_curiosity_density(title)
    compression = calculate_compression_efficiency(title, constraints["optimal_length"])
    
    # Calculate specificity (numbers, specific terms)
    specificity = 0.0
    import re
    if re.search(r'\d+', title):
        specificity += 0.3
    if any(word in title.lower() for word in ["hours", "minutes", "days", "replaces", "better"]):
        specificity += 0.2
    
    # Emotional polarity (positive/negative)
    positive_words = ["better", "amazing", "fast", "easy", "great"]
    negative_words = ["problem", "outdated", "stopped", "isn't"]
    
    emotional_polarity = 0.5  # Neutral
    if any(word in title.lower() for word in positive_words):
        emotional_polarity = 0.7
    elif any(word in title.lower() for word in negative_words):
        emotional_polarity = 0.3
    
    # Overall score
    score = (
        curiosity * 0.3 +
        compression * 0.2 +
        specificity * 0.3 +
        emotional_polarity * 0.2
    )
    
    return {
        "title": title,
        "specificity": specificity,
        "curiosity": curiosity,
        "emotional_polarity": emotional_polarity,
        "compression_efficiency": compression,
        "score": score,
        "platform": platform
    }

def generate_title_variants(hook_text: str, platform: str = "tiktok", count: int = 5) -> List[Dict]:
    """
    Generate multiple title variants
    
    Args:
        hook_text: Base hook text
        platform: Target platform
        count: Number of variants
        
    Returns:
        List of scored title variants
    """
    variants = []
    
    # Generate variations
    base_title = generate_title(hook_text, platform)
    variants.append(score_title(base_title, platform))
    
    # Add variations
    variations = [
        base_title,
        base_title.upper() if len(base_title) < 50 else base_title,
        f"🔥 {base_title}",
        f"{base_title} 💯",
    ]
    
    for var in variations[:count-1]:
        if var != base_title:
            variants.append(score_title(var, platform))
    
    # Sort by score
    variants.sort(key=lambda x: x["score"], reverse=True)
    
    return variants[:count]
