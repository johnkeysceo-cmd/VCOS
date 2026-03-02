"""
Retention Optimizer - Silence Detector
Remove pauses > 150ms (adaptive threshold based on pacing)
"""

try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    librosa = None
    np = None
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

def detect_silence(audio_file: str, threshold_ms: int = 150, adaptive: bool = True) -> List[Tuple[float, float]]:
    """
    Detect silence periods in audio
    
    Args:
        audio_file: Path to audio file
        threshold_ms: Silence threshold in milliseconds
        adaptive: Use adaptive threshold based on pacing
        
    Returns:
        List of (start_time, end_time) tuples for silence periods
    """
    if not LIBROSA_AVAILABLE:
        logger.warning("librosa not available, skipping silence detection. Install with: pip install librosa")
        return []
    
    try:
        # Load audio
        y, sr = librosa.load(audio_file, sr=None)
        
        # Calculate energy
        energy = np.abs(y)
        
        # Calculate threshold
        if adaptive:
            # Adaptive threshold: mean - 1 std dev
            mean_energy = np.mean(energy)
            std_energy = np.std(energy)
            threshold = mean_energy - std_energy
            threshold = max(threshold, np.min(energy) * 2)  # Minimum threshold
        else:
            # Fixed threshold
            threshold = np.mean(energy) * 0.5
        
        # Find silence regions
        silence_mask = energy < threshold
        
        # Convert to time-based segments
        silence_periods = []
        in_silence = False
        silence_start = 0
        
        frame_duration = 1.0 / sr
        
        for i, is_silent in enumerate(silence_mask):
            time = i * frame_duration
            
            if is_silent and not in_silence:
                silence_start = time
                in_silence = True
            elif not is_silent and in_silence:
                silence_duration = time - silence_start
                # Only include if duration > threshold
                if silence_duration * 1000 >= threshold_ms:
                    silence_periods.append((silence_start, time))
                in_silence = False
        
        # Handle silence at end
        if in_silence:
            silence_duration = len(energy) * frame_duration - silence_start
            if silence_duration * 1000 >= threshold_ms:
                silence_periods.append((silence_start, len(energy) * frame_duration))
        
        logger.info(f"Detected {len(silence_periods)} silence periods")
        
        return silence_periods
        
    except Exception as e:
        logger.error(f"Error detecting silence: {e}")
        return []
