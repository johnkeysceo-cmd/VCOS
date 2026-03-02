"""
Hook Engine - Specificity Enhancer
Turns vague words into concrete ones
"""

import re
from typing import Dict

# Replacement mappings for specificity
SPECIFICITY_REPLACEMENTS = {
    "few days": "72 hours",
    "a few days": "72 hours",
    "couple days": "48 hours",
    "couple of days": "48 hours",
    "few hours": "3 hours",
    "a few hours": "3 hours",
    "couple hours": "2 hours",
    "couple of hours": "2 hours",
    "better": "30% faster",
    "much better": "50% faster",
    "faster": "2x faster",
    "quickly": "in 5 minutes",
    "soon": "in 24 hours",
    "many": "10",
    "several": "5",
    "some": "3",
    "a lot": "10x",
    "tons": "100+",
}

# Number enhancement patterns
NUMBER_PATTERNS = [
    (r'\b(\d+)\s*days?\b', lambda m: f"{int(m.group(1)) * 24} hours" if int(m.group(1)) <= 7 else m.group(0)),
    (r'\b(\d+)\s*weeks?\b', lambda m: f"{int(m.group(1)) * 7} days" if int(m.group(1)) <= 4 else m.group(0)),
]

def enhance_specificity(text: str) -> str:
    """
    Enhance specificity of text by replacing vague terms
    
    Args:
        text: Input text
        
    Returns:
        Enhanced text with specific terms
    """
    enhanced = text
    
    # Apply direct replacements (case-insensitive)
    for vague, specific in SPECIFICITY_REPLACEMENTS.items():
        # Case-insensitive replacement
        pattern = re.compile(re.escape(vague), re.IGNORECASE)
        enhanced = pattern.sub(specific, enhanced)
    
    # Apply number pattern enhancements
    for pattern, replacement_func in NUMBER_PATTERNS:
        enhanced = re.sub(pattern, replacement_func, enhanced, flags=re.IGNORECASE)
    
    return enhanced

def calculate_specificity_score(text: str) -> float:
    """
    Calculate how specific a text is (0.0 = vague, 1.0 = very specific)
    
    Args:
        text: Text to score
        
    Returns:
        Specificity score
    """
    score = 0.0
    
    # Check for specific numbers
    numbers = re.findall(r'\b\d+\b', text)
    if numbers:
        score += 0.4
    
    # Check for time units
    if re.search(r'\d+\s*(hours?|minutes?|seconds?|days?)', text, re.IGNORECASE):
        score += 0.3
    
    # Check for percentages
    if '%' in text or re.search(r'\d+\s*percent', text, re.IGNORECASE):
        score += 0.2
    
    # Check for multipliers
    if re.search(r'\d+x', text, re.IGNORECASE):
        score += 0.1
    
    # Penalty for vague words
    vague_words = ["few", "some", "many", "several", "a lot", "better", "quickly"]
    vague_count = sum(1 for word in vague_words if word in text.lower())
    score -= vague_count * 0.1
    
    return max(0.0, min(1.0, score))

def enhance_with_context(text: str, context: Dict = None) -> str:
    """
    Enhance specificity with additional context
    
    Args:
        text: Input text
        context: Optional context dictionary (e.g., {"timeframe": "3 days", "target": "Screen Studio"})
        
    Returns:
        Enhanced text
    """
    enhanced = enhance_specificity(text)
    
    if context:
        # Replace placeholders with context values
        for key, value in context.items():
            enhanced = enhanced.replace(f"{{{key}}}", str(value))
    
    return enhanced
