"""
Title & Thumbnail Engine - Compression Efficiency Model
Measures how efficiently text uses character space
"""

def calculate_compression_efficiency(text: str, optimal_length: int = 80) -> float:
    """
    Calculate compression efficiency (0.0 to 1.0)
    
    Higher score = text is closer to optimal length and uses space efficiently
    
    Args:
        text: Text to analyze
        optimal_length: Optimal character length
        
    Returns:
        Compression efficiency score
    """
    length = len(text)
    
    # Calculate distance from optimal
    distance = abs(length - optimal_length)
    max_distance = optimal_length  # Worst case
    
    # Efficiency: closer to optimal = higher score
    efficiency = 1.0 - (distance / max_distance)
    
    # Bonus for using numbers (more information in fewer chars)
    import re
    if re.search(r'\d+', text):
        efficiency += 0.1
    
    # Penalty for very short (likely incomplete)
    if length < optimal_length * 0.5:
        efficiency -= 0.2
    
    return max(0.0, min(1.0, efficiency))
