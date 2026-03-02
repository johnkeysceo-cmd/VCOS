"""
Retention Optimizer - Pacing Controller
Controls words per minute and overall pacing
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Optimal pacing targets
OPTIMAL_WPM = 180  # Words per minute
MIN_WPM = 150
MAX_WPM = 220

def calculate_pacing(transcript: List[Dict], video_duration: float) -> Dict:
    """
    Calculate current pacing metrics
    
    Args:
        transcript: List of sentences with timestamps
        video_duration: Total video duration in seconds
        
    Returns:
        Pacing metrics dictionary
    """
    if not transcript or video_duration == 0:
        return {
            "wpm": 0,
            "sentence_count": 0,
            "avg_sentence_duration": 0,
            "pacing_score": 0.5
        }
    
    # Count total words
    total_words = sum(len(s.get("text", "").split()) for s in transcript)
    
    # Calculate WPM
    wpm = (total_words / video_duration) * 60
    
    # Calculate pacing score (0.0 to 1.0)
    if wpm < MIN_WPM:
        pacing_score = wpm / MIN_WPM * 0.5  # Too slow
    elif wpm > MAX_WPM:
        pacing_score = 1.0 - ((wpm - MAX_WPM) / (MAX_WPM * 0.5)) * 0.3  # Too fast
        pacing_score = max(0.7, pacing_score)
    else:
        # Optimal range
        pacing_score = 0.5 + ((wpm - MIN_WPM) / (MAX_WPM - MIN_WPM)) * 0.5
    
    return {
        "wpm": wpm,
        "sentence_count": len(transcript),
        "avg_sentence_duration": video_duration / len(transcript) if transcript else 0,
        "pacing_score": min(1.0, max(0.0, pacing_score))
    }

def adjust_pacing_speed(current_wpm: float) -> float:
    """
    Calculate speed multiplier to achieve optimal pacing
    
    Args:
        current_wpm: Current words per minute
        
    Returns:
        Speed multiplier (1.0 = normal, >1.0 = faster)
    """
    if current_wpm < MIN_WPM:
        # Speed up if too slow
        target_wpm = OPTIMAL_WPM
        multiplier = target_wpm / current_wpm if current_wpm > 0 else 1.1
        return min(1.12, max(1.0, multiplier))  # Cap at 1.12x
    elif current_wpm > MAX_WPM:
        # Slow down if too fast
        target_wpm = OPTIMAL_WPM
        multiplier = target_wpm / current_wpm
        return max(0.9, min(1.0, multiplier))  # Cap at 0.9x
    else:
        return 1.0  # Optimal
