"""
Feedback Trainer - Hook Weight Updater
Updates hook template weights based on performance
"""

from services.hook_engine.template_library import update_template_weight
import logging

logger = logging.getLogger(__name__)

def update_weight(template_name: str, lift: float, learning_rate: float = 0.1):
    """
    Update template weight based on performance lift
    
    Args:
        template_name: Template structure string
        lift: Performance lift (1.0 = baseline, >1.0 = better)
        learning_rate: Learning rate for weight updates
    """
    # Calculate weight adjustment
    weight_adjustment = (lift - 1.0) * learning_rate
    
    # Get current weight and update
    from services.hook_engine.template_library import TEMPLATES
    current_weight = 1.0
    
    for template in TEMPLATES:
        if template.structure == template_name:
            current_weight = template.weight
            break
    
    new_weight = current_weight + weight_adjustment
    new_weight = max(0.5, min(2.0, new_weight))  # Clamp between 0.5 and 2.0
    
    update_template_weight(template_name, new_weight)
    logger.info(f"Updated weight for {template_name}: {current_weight:.2f} -> {new_weight:.2f} (lift: {lift:.2f})")
