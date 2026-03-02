"""
Feedback Trainer - Confidence Weighting
Weight updates based on signal confidence (view count, sample size)
"""

from typing import Dict, List
import math
import logging

logger = logging.getLogger(__name__)

def compute_signal_confidence(views: int, shares: int, comments: int) -> float:
    """
    Compute confidence in performance signal based on sample size
    
    Args:
        views: Total views
        shares: Total shares
        comments: Total comments
        
    Returns:
        Confidence score (0.0 to 1.0)
    """
    # Base confidence on views (more views = more reliable)
    # Use logarithmic scale: log(views) / log(100000)
    if views <= 0:
        return 0.0
    
    # Confidence increases with views, but with diminishing returns
    view_confidence = min(1.0, math.log10(max(views, 1)) / 5.0)  # 100k views = 1.0
    
    # Engagement signals add confidence
    engagement_rate = (shares + comments) / max(views, 1)
    engagement_confidence = min(1.0, engagement_rate * 100)  # 1% engagement = full confidence
    
    # Combined confidence
    confidence = (view_confidence * 0.7) + (engagement_confidence * 0.3)
    
    return confidence

def compute_bayesian_update(
    prior_weight: float,
    observed_lift: float,
    confidence: float,
    learning_rate: float = 0.1
) -> float:
    """
    Bayesian weight update with confidence weighting
    
    Args:
        prior_weight: Current weight
        observed_lift: Observed performance lift
        confidence: Signal confidence (0.0 to 1.0)
        learning_rate: Base learning rate
        
    Returns:
        Updated weight
    """
    # Adjust learning rate by confidence
    effective_learning_rate = learning_rate * confidence
    
    # Compute update
    weight_adjustment = (observed_lift - 1.0) * effective_learning_rate
    
    # Update weight
    new_weight = prior_weight + weight_adjustment
    
    # Clamp to reasonable range
    new_weight = max(0.1, min(2.0, new_weight))
    
    return new_weight

def weight_update_with_confidence(
    template_name: str,
    observed_lift: float,
    views: int,
    shares: int = 0,
    comments: int = 0
) -> Dict:
    """
    Update weight with confidence weighting
    
    Args:
        template_name: Template to update
        observed_lift: Performance lift observed
        views: View count
        shares: Share count
        comments: Comment count
        
    Returns:
        Update result dictionary
    """
    from services.hook_engine.template_library import TEMPLATES, update_template_weight
    
    # Get current weight
    current_weight = 1.0
    for template in TEMPLATES:
        if template.structure == template_name:
            current_weight = template.weight
            break
    
    # Compute confidence
    confidence = compute_signal_confidence(views, shares, comments)
    
    # Bayesian update
    new_weight = compute_bayesian_update(current_weight, observed_lift, confidence)
    
    # Update
    update_template_weight(template_name, new_weight)
    
    logger.info(
        f"Updated {template_name}: {current_weight:.2f} -> {new_weight:.2f} "
        f"(lift: {observed_lift:.2f}, confidence: {confidence:.2f})"
    )
    
    return {
        "template": template_name,
        "old_weight": current_weight,
        "new_weight": new_weight,
        "confidence": confidence,
        "observed_lift": observed_lift
    }
