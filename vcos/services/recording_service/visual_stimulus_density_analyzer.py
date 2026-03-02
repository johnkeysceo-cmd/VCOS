"""
Recording Service - Visual Stimulus Density Analyzer
Analyzes visual pacing mathematically
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

def analyze_visual_stimulus_density(
    zoom_events: List[Dict],
    transition_events: List[Dict],
    subtitle_events: List[Dict],
    video_duration: float
) -> Dict:
    """
    Analyze visual stimulus density
    
    Args:
        zoom_events: List of zoom events with timestamps
        transition_events: List of transition events
        subtitle_events: List of subtitle flash events
        video_duration: Video duration in seconds
        
    Returns:
        Visual stimulus metrics
    """
    if video_duration == 0:
        return {
            "visual_events_per_minute": 0.0,
            "zoom_frequency": 0.0,
            "subtitle_flash_rate": 0.0,
            "motion_change_density": 0.0,
            "stimulus_score": 0.0
        }
    
    # Calculate frequencies
    zoom_frequency = len(zoom_events) / (video_duration / 60.0)  # per minute
    transition_frequency = len(transition_events) / (video_duration / 60.0)
    subtitle_flash_rate = len(subtitle_events) / (video_duration / 60.0)
    
    # Total visual events per minute
    total_events = len(zoom_events) + len(transition_events) + len(subtitle_events)
    visual_events_per_minute = total_events / (video_duration / 60.0)
    
    # Motion change density (transitions + zooms)
    motion_change_density = (len(zoom_events) + len(transition_events)) / video_duration
    
    # Stimulus score (0-1, optimal around 3-4 events/min)
    optimal_rate = 3.5
    if visual_events_per_minute < optimal_rate:
        stimulus_score = visual_events_per_minute / optimal_rate
    else:
        # Too many events can be overwhelming
        stimulus_score = 1.0 - ((visual_events_per_minute - optimal_rate) / optimal_rate * 0.3)
        stimulus_score = max(0.7, stimulus_score)
    
    return {
        "visual_events_per_minute": visual_events_per_minute,
        "zoom_frequency": zoom_frequency,
        "transition_frequency": transition_frequency,
        "subtitle_flash_rate": subtitle_flash_rate,
        "motion_change_density": motion_change_density,
        "stimulus_score": max(0.0, min(1.0, stimulus_score))
    }
