"""
Hook Engine - Emotional Buckets
Categorizes hooks by emotional angle
"""

from typing import Dict, List

# Emotional angle definitions
EMOTIONAL_ANGLES = {
    "speed": {
        "description": "Emphasizes time/speed achievement",
        "keywords": ["hours", "minutes", "days", "fast", "quick", "rebuilt", "built"],
        "ctr_multiplier": 1.1
    },
    "replacement": {
        "description": "Frames as replacement for existing tool",
        "keywords": ["replaces", "instead", "better than", "stopped using"],
        "ctr_multiplier": 1.15
    },
    "controversy": {
        "description": "Creates controversy or challenge",
        "keywords": ["problem", "outdated", "isn't enough", "why"],
        "ctr_multiplier": 1.2
    },
    "challenge": {
        "description": "Frames as personal challenge",
        "keywords": ["challenge", "from scratch", "can I", "trying"],
        "ctr_multiplier": 1.05
    },
    "secret": {
        "description": "Reveals hidden knowledge",
        "keywords": ["secret", "nobody", "hidden", "unknown"],
        "ctr_multiplier": 1.0
    },
    "authority": {
        "description": "Establishes authority/expertise",
        "keywords": ["as a", "years", "learned", "expert"],
        "ctr_multiplier": 0.95
    },
    "proof": {
        "description": "Provides proof/evidence",
        "keywords": ["tested", "proof", "evidence", "results"],
        "ctr_multiplier": 1.0
    }
}

def get_angle_info(angle: str) -> Dict:
    """Get information about an emotional angle"""
    return EMOTIONAL_ANGLES.get(angle, {
        "description": "Unknown angle",
        "keywords": [],
        "ctr_multiplier": 1.0
    })

def detect_angle_from_text(text: str) -> str:
    """
    Detect emotional angle from text
    
    Args:
        text: Hook text
        
    Returns:
        Detected angle name
    """
    text_lower = text.lower()
    angle_scores = {}
    
    for angle, info in EMOTIONAL_ANGLES.items():
        score = sum(1 for keyword in info["keywords"] if keyword in text_lower)
        if score > 0:
            angle_scores[angle] = score
    
    if angle_scores:
        return max(angle_scores, key=angle_scores.get)
    
    return "secret"  # Default

def get_all_angles() -> List[str]:
    """Get all available emotional angles"""
    return list(EMOTIONAL_ANGLES.keys())

def get_emotional_bucket(hook_text: str, angle: str = None) -> str:
    """
    Get emotional bucket for a hook
    
    Args:
        hook_text: Hook text
        angle: Optional pre-determined angle
        
    Returns:
        Emotional bucket/angle name
    """
    if angle and angle in EMOTIONAL_ANGLES:
        return angle
    
    # Auto-detect angle from text
    return detect_angle_from_text(hook_text)
