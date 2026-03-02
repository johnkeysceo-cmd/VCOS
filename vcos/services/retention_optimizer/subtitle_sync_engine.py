"""
Retention Optimizer - Subtitle Sync Engine
Synchronizes subtitles with video and applies emphasis
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def sync_subtitles(transcript: List[Dict], video_duration: float) -> List[Dict]:
    """
    Synchronize subtitle timings with video
    
    Args:
        transcript: List of sentences with text
        video_duration: Video duration in seconds
        
    Returns:
        List of subtitle entries with start/end times
    """
    subtitles = []
    
    if not transcript:
        return subtitles
    
    # Distribute sentences evenly or use provided timestamps
    time_per_sentence = video_duration / len(transcript)
    
    for i, sentence_data in enumerate(transcript):
        start_time = sentence_data.get("timestamp", i * time_per_sentence)
        end_time = sentence_data.get("end_timestamp", start_time + time_per_sentence)
        
        text = sentence_data.get("text", "")
        
        subtitles.append({
            "start": start_time,
            "end": end_time,
            "text": text,
            "emphasis": sentence_data.get("emphasis", False)
        })
    
    logger.info(f"Synced {len(subtitles)} subtitle entries")
    
    return subtitles

def apply_subtitle_emphasis(subtitles: List[Dict], key_words: List[str] = None) -> List[Dict]:
    """
    Apply emphasis to important words in subtitles
    
    Args:
        subtitles: List of subtitle entries
        key_words: Optional list of keywords to emphasize
        
    Returns:
        Subtitles with emphasis markers
    """
    if not key_words:
        key_words = []
    
    emphasized = []
    
    for subtitle in subtitles:
        text = subtitle["text"]
        
        # Add emphasis tags around key words
        for word in key_words:
            if word.lower() in text.lower():
                text = text.replace(word, f"**{word}**")
        
        emphasized.append({
            **subtitle,
            "text": text,
            "has_emphasis": any(word.lower() in text.lower() for word in key_words)
        })
    
    return emphasized
