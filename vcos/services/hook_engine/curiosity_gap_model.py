"""
Hook Engine - Curiosity Gap Model
Rates hooks by open loop intensity, incompleteness index, surprise delta
"""

import re
from typing import Dict

def calculate_curiosity_score(hook_text: str) -> float:
    """
    Calculate curiosity gap score for a hook
    
    Args:
        hook_text: The hook text
        
    Returns:
        Curiosity score (0.0 to 1.0)
    """
    score = 0.0
    
    # Open loop indicators (questions, incomplete statements)
    if "?" in hook_text:
        score += 0.3
    
    # Incomplete statements (ellipsis, "here's why", etc.)
    if "..." in hook_text or "here's why" in hook_text.lower():
        score += 0.25
    
    # Surprise indicators (unexpected numbers, contrasts)
    numbers = re.findall(r'\d+', hook_text)
    if numbers:
        # Specific numbers increase curiosity
        score += 0.2
    
    # Contrast words
    contrast_words = ["but", "however", "yet", "instead", "replaces"]
    if any(word in hook_text.lower() for word in contrast_words):
        score += 0.15
    
    # Specificity bonus (specific numbers/times)
    if re.search(r'\d+\s*(hours?|minutes?|days?|weeks?)', hook_text.lower()):
        score += 0.1
    
    # Cap at 1.0
    return min(1.0, score)

def calculate_incompleteness_index(hook_text: str) -> float:
    """
    Calculate how incomplete/informative the hook is
    
    Returns:
        Incompleteness index (0.0 = complete, 1.0 = very incomplete)
    """
    index = 0.0
    
    # Questions are incomplete
    if "?" in hook_text:
        index += 0.4
    
    # Promises without delivery
    if any(phrase in hook_text.lower() for phrase in ["here's", "here is", "this is", "let me show"]):
        index += 0.3
    
    # Ellipsis
    if "..." in hook_text:
        index += 0.2
    
    # Vague references
    if re.search(r'\b(it|this|that|they)\b', hook_text.lower()):
        index += 0.1
    
    return min(1.0, index)

def calculate_surprise_delta(hook_text: str) -> float:
    """
    Calculate surprise factor (unexpectedness)
    
    Returns:
        Surprise delta (0.0 to 1.0)
    """
    delta = 0.0
    
    # Unexpected timeframes
    if re.search(r'\d+\s*(hours?|minutes?)', hook_text.lower()):
        delta += 0.3
    
    # Extreme numbers
    extreme_numbers = re.findall(r'\b(\d{2,})\b', hook_text)
    if extreme_numbers and any(int(n) > 10 for n in extreme_numbers):
        delta += 0.2
    
    # Replacement/controversy words
    if any(word in hook_text.lower() for word in ["replaces", "outdated", "stopped", "problem"]):
        delta += 0.25
    
    # Challenge words
    if any(word in hook_text.lower() for word in ["challenge", "from scratch", "rebuild"]):
        delta += 0.2
    
    return min(1.0, delta)

def score_hook_curiosity(hook_text: str) -> Dict[str, float]:
    """
    Comprehensive curiosity scoring
    
    Returns:
        Dictionary with all curiosity metrics
    """
    return {
        "curiosity_score": calculate_curiosity_score(hook_text),
        "incompleteness_index": calculate_incompleteness_index(hook_text),
        "surprise_delta": calculate_surprise_delta(hook_text),
        "overall_score": (
            calculate_curiosity_score(hook_text) * 0.4 +
            calculate_incompleteness_index(hook_text) * 0.3 +
            calculate_surprise_delta(hook_text) * 0.3
        )
    }
