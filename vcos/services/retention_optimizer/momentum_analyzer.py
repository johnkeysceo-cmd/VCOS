"""
Retention Optimizer - Momentum Analyzer
Score each sentence: forward moving? repetitive? explanatory drag?
Cut low momentum lines automatically.
"""

import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Filler words that reduce momentum
FILLER_WORDS = ["um", "uh", "er", "ah", "like", "basically", "actually", "you know", "I mean"]

# Repetitive patterns
REPETITIVE_PATTERNS = [
    r"(.+?)\1{2,}",  # Repeated phrases
]

def score_sentence(sentence: str) -> float:
    """
    Score sentence momentum (0.0 = low momentum, 1.0 = high momentum)
    
    Args:
        sentence: Sentence text
        
    Returns:
        Momentum score
    """
    score = 1.0
    
    # Penalty for filler words
    sentence_lower = sentence.lower()
    filler_count = sum(1 for filler in FILLER_WORDS if filler in sentence_lower)
    score -= filler_count * 0.1
    
    # Penalty for repetition
    for pattern in REPETITIVE_PATTERNS:
        if re.search(pattern, sentence, re.IGNORECASE):
            score -= 0.2
    
    # Penalty for very short sentences (likely incomplete)
    if len(sentence.split()) < 3:
        score -= 0.15
    
    # Penalty for very long sentences (explanatory drag)
    if len(sentence.split()) > 25:
        score -= 0.1
    
    # Bonus for action words
    action_words = ["build", "create", "make", "do", "show", "see", "watch", "try"]
    if any(word in sentence_lower for word in action_words):
        score += 0.1
    
    # Bonus for specific numbers
    if re.search(r'\d+', sentence):
        score += 0.05
    
    return max(0.0, min(1.0, score))

def analyze_transcript_momentum(transcript: List[Dict], video_duration: float = 0) -> List[Dict]:
    """
    Analyze momentum for each sentence in transcript
    
    Args:
        transcript: List of sentence dicts with 'text' and 'timestamp'
        
    Returns:
        List with momentum scores added
    """
    analyzed = []
    
    for sentence_data in transcript:
        text = sentence_data.get("text", "")
        momentum_score = score_sentence(text)
        
        analyzed.append({
            **sentence_data,
            "momentum_score": momentum_score,
            "should_keep": momentum_score >= 0.5  # Threshold
        })
    
    # Log statistics
    keep_count = sum(1 for s in analyzed if s["should_keep"])
    logger.info(f"Momentum analysis: {keep_count}/{len(analyzed)} sentences kept")
    
    return analyzed

def filter_low_momentum(transcript: List[Dict], min_score: float = 0.5) -> List[Dict]:
    """
    Filter out low momentum sentences
    
    Args:
        transcript: Analyzed transcript with momentum scores
        min_score: Minimum momentum score to keep
        
    Returns:
        Filtered transcript
    """
    filtered = [s for s in transcript if s.get("momentum_score", 0) >= min_score]
    logger.info(f"Filtered {len(transcript) - len(filtered)} low momentum sentences")
    return filtered
