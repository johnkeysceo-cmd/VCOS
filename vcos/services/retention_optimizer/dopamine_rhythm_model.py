"""
Retention Optimizer - Dopamine Rhythm Modulator
Controls micro stimulus frequency (zoom, transitions, subtitle animations)
"""

from dataclasses import dataclass
from typing import List
import logging

logger = logging.getLogger(__name__)

@dataclass
class RhythmProfile:
    """Dopamine rhythm profile"""
    zoom_freq: float  # Zooms per minute
    word_rate: int  # Words per minute
    transition_freq: float  # Visual transitions per minute
    subtitle_animation_freq: float  # Subtitle animations per minute
    stimulus_interval: float  # Target seconds between stimuli

# Predefined rhythm profiles
HIGH_RETENTION = RhythmProfile(
    zoom_freq=3.0,  # 3 zooms per minute
    word_rate=180,
    transition_freq=2.0,
    subtitle_animation_freq=4.0,
    stimulus_interval=3.0  # Micro stimulus every 3 seconds
)

MODERATE_RETENTION = RhythmProfile(
    zoom_freq=2.0,
    word_rate=160,
    transition_freq=1.5,
    subtitle_animation_freq=3.0,
    stimulus_interval=4.0
)

LOW_RETENTION = RhythmProfile(
    zoom_freq=1.0,
    word_rate=140,
    transition_freq=1.0,
    subtitle_animation_freq=2.0,
    stimulus_interval=6.0
)

def calculate_stimulus_schedule(video_duration: float, profile: RhythmProfile = HIGH_RETENTION) -> List[float]:
    """
    Calculate when to inject stimuli based on rhythm profile
    
    Args:
        video_duration: Video duration in seconds
        profile: Rhythm profile to use
        
    Returns:
        List of timestamps for stimuli
    """
    stimuli = []
    current_time = profile.stimulus_interval
    
    while current_time < video_duration:
        stimuli.append(current_time)
        current_time += profile.stimulus_interval
    
    logger.info(f"Calculated {len(stimuli)} stimulus points for {video_duration:.1f}s video")
    
    return stimuli

def apply_rhythm_profile(video_metadata: Dict, profile: RhythmProfile = HIGH_RETENTION) -> Dict:
    """
    Apply rhythm profile to video processing
    
    Args:
        video_metadata: Video metadata dictionary
        profile: Rhythm profile
        
    Returns:
        Updated metadata with rhythm settings
    """
    video_duration = video_metadata.get("duration", 0)
    
    return {
        **video_metadata,
        "rhythm_profile": {
            "zoom_freq": profile.zoom_freq,
            "word_rate": profile.word_rate,
            "transition_freq": profile.transition_freq,
            "subtitle_animation_freq": profile.subtitle_animation_freq,
            "stimulus_interval": profile.stimulus_interval,
            "stimulus_schedule": calculate_stimulus_schedule(video_duration, profile)
        }
    }
