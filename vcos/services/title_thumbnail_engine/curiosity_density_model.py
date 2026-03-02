"""
Title & Thumbnail Engine - Curiosity Density Model
Measures curiosity density in text
"""

import re
from typing import Dict

def calculate_curiosity_density(text: str) -> float:
    """
    Calculate curiosity density (0.0 to 1.0)
    
    Args:
        text: Text to analyze
        
    Returns:
        Curiosity density score
    """
    score = 0.0
    
    # Questions
    if "?" in text:
        score += 0.3
    
    # Incomplete statements
    if "..." in text or "here's" in text.lower():
        score += 0.25
    
    # Numbers (specificity)
    if re.search(r'\d+', text):
        score += 0.2
    
    # Contrast words
    contrast = ["but", "however", "instead", "replaces", "vs"]
    if any(word in text.lower() for word in contrast):
        score += 0.15
    
    # Promise words
    promise = ["secret", "hidden", "nobody", "why", "how"]
    if any(word in text.lower() for word in promise):
        score += 0.1
    
    return min(1.0, score)
