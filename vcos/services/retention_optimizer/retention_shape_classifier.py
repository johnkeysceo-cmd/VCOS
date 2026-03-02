"""
Retention Optimizer - Retention Shape Classifier
Classifies retention curves into behavioral patterns
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class RetentionShape:
    """Retention curve shape types"""
    FRONTLOADED_DROP = "frontloaded_drop"      # High start, rapid drop
    MID_COLLAPSE = "mid_collapse"              # Strong hook, weak middle
    STRONG_HOOK_WEAK_ENDING = "strong_hook_weak_ending"  # Good start/mid, bad end
    HIGH_COMPLETION = "high_completion"        # Strong throughout
    STEADY_DECLINE = "steady_decline"          # Gradual drop
    UNKNOWN = "unknown"

def classify_retention_curve(retention_data: List[float], video_duration: float) -> Dict:
    """
    Classify retention curve into behavioral pattern
    
    Args:
        retention_data: List of retention values at different timestamps
        video_duration: Total video duration
        
    Returns:
        Classification result
    """
    if not retention_data or len(retention_data) < 3:
        return {
            "shape": RetentionShape.UNKNOWN,
            "confidence": 0.0,
            "characteristics": {}
        }
    
    # Normalize to 0-1 retention values
    normalized = [min(1.0, max(0.0, r)) for r in retention_data]
    
    # Key points
    start_retention = normalized[0] if normalized else 0.0
    mid_retention = normalized[len(normalized) // 2] if normalized else 0.0
    end_retention = normalized[-1] if normalized else 0.0
    
    # Calculate drops
    start_to_mid_drop = start_retention - mid_retention
    mid_to_end_drop = mid_retention - end_retention
    total_drop = start_retention - end_retention
    
    # Classification logic
    shape = RetentionShape.UNKNOWN
    confidence = 0.0
    
    if start_retention > 0.8 and start_to_mid_drop > 0.4:
        # High start, rapid drop
        shape = RetentionShape.FRONTLOADED_DROP
        confidence = min(1.0, start_to_mid_drop / 0.5)
    elif start_retention > 0.7 and mid_retention < 0.4 and end_retention < 0.3:
        # Strong hook, weak middle
        shape = RetentionShape.MID_COLLAPSE
        confidence = 0.8
    elif start_retention > 0.7 and mid_retention > 0.6 and end_retention < 0.4:
        # Good start/mid, bad end
        shape = RetentionShape.STRONG_HOOK_WEAK_ENDING
        confidence = 0.8
    elif end_retention > 0.6:
        # Strong throughout
        shape = RetentionShape.HIGH_COMPLETION
        confidence = min(1.0, end_retention / 0.7)
    elif total_drop < 0.3 and start_retention < 0.7:
        # Gradual decline
        shape = RetentionShape.STEADY_DECLINE
        confidence = 0.7
    
    return {
        "shape": shape,
        "confidence": confidence,
        "characteristics": {
            "start_retention": start_retention,
            "mid_retention": mid_retention,
            "end_retention": end_retention,
            "start_to_mid_drop": start_to_mid_drop,
            "mid_to_end_drop": mid_to_end_drop,
            "total_drop": total_drop
        }
    }

def get_shape_recommendations(shape: str) -> List[str]:
    """
    Get recommendations based on retention shape
    
    Args:
        shape: Retention shape type
        
    Returns:
        List of recommendations
    """
    recommendations = {
        RetentionShape.FRONTLOADED_DROP: [
            "Improve hook quality - viewers leaving immediately",
            "Check if hook matches content",
            "Consider stronger opening visual"
        ],
        RetentionShape.MID_COLLAPSE: [
            "Add visual stimulus in middle section",
            "Increase pacing in middle",
            "Inject zoom effects at mid-point"
        ],
        RetentionShape.STRONG_HOOK_WEAK_ENDING: [
            "Strengthen ending - add call to action",
            "Preview outcome earlier",
            "Improve conclusion payoff"
        ],
        RetentionShape.HIGH_COMPLETION: [
            "This pattern is excellent - replicate",
            "Analyze what makes this work",
            "Use as template for future content"
        ],
        RetentionShape.STEADY_DECLINE: [
            "Increase dopamine rhythm frequency",
            "Add more visual transitions",
            "Improve overall pacing"
        ]
    }
    
    return recommendations.get(shape, ["Analyze retention curve patterns"])
