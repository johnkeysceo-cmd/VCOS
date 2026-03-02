"""
Hook Engine - Emotional Resonance Analyzer
Analyzes emotional resonance and novelty of hooks
"""

from typing import Dict, List
from services.hook_engine.curiosity_gap_model import score_hook_curiosity
from services.hook_engine.emotional_buckets import get_emotional_bucket
import logging

logger = logging.getLogger(__name__)

def analyze_emotional_resonance(hook_text: str, angle: str = None) -> Dict:
    """
    Analyze emotional resonance of a hook
    
    Args:
        hook_text: Hook text
        angle: Emotional angle
        
    Returns:
        Emotional resonance analysis
    """
    # Get emotional bucket
    emotional_bucket = get_emotional_bucket(hook_text, angle)
    
    # Analyze novelty
    novelty_score = calculate_novelty_score(hook_text)
    
    # Analyze emotional intensity
    intensity_score = calculate_emotional_intensity(hook_text, emotional_bucket)
    
    # Analyze resonance potential
    resonance_score = (novelty_score * 0.4 + intensity_score * 0.6)
    
    return {
        "emotional_bucket": emotional_bucket,
        "novelty_score": novelty_score,
        "intensity_score": intensity_score,
        "resonance_score": resonance_score,
        "recommendation": get_resonance_recommendation(resonance_score)
    }

def calculate_novelty_score(hook_text: str) -> float:
    """
    Calculate novelty score (0.0 to 1.0)
    Higher = more novel/unique
    """
    from services.hook_engine.hook_db import get_historical_performance
    
    # Check if similar hooks exist
    historical_lift = get_historical_performance(hook_text) or 1.0
    
    # Novel hooks have no historical data (lift = 1.0)
    # But we want some novelty, not complete randomness
    if historical_lift == 1.0:
        # Check for unique words/phrases
        unique_indicators = ["never", "first", "only", "exclusive", "secret"]
        has_unique = any(word in hook_text.lower() for word in unique_indicators)
        return 0.8 if has_unique else 0.5
    else:
        # Existing hooks - novelty decreases with usage
        return max(0.2, 1.0 - (historical_lift - 1.0) * 0.3)

def calculate_emotional_intensity(hook_text: str, emotional_bucket: str) -> float:
    """
    Calculate emotional intensity (0.0 to 1.0)
    """
    intensity_words = {
        "fear": ["scary", "terrifying", "dangerous", "warning"],
        "curiosity": ["secret", "hidden", "unknown", "mystery"],
        "excitement": ["amazing", "incredible", "unbelievable", "wow"],
        "anger": ["outrageous", "unacceptable", "wrong", "bad"],
        "joy": ["amazing", "perfect", "love", "best"]
    }
    
    words = hook_text.lower().split()
    intensity_count = sum(
        1 for word in words
        if any(intensity_word in word for intensity_words_list in intensity_words.values() for intensity_word in intensity_words_list)
    )
    
    # Normalize by text length
    intensity_score = min(1.0, intensity_count / max(len(words), 1) * 3)
    
    return intensity_score

def get_resonance_recommendation(resonance_score: float) -> str:
    """Get recommendation based on resonance score"""
    if resonance_score >= 0.8:
        return "High resonance - strong viral potential"
    elif resonance_score >= 0.6:
        return "Moderate resonance - good potential with optimization"
    elif resonance_score >= 0.4:
        return "Low resonance - needs improvement"
    else:
        return "Very low resonance - consider different angle"
