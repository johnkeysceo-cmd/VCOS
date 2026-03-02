"""
Hook Engine - Hook Scorer
Scores predicted CTR probability
"""

from services.hook_engine.template_library import HookTemplate
from services.hook_engine.curiosity_gap_model import score_hook_curiosity
from services.hook_engine.specificity_enhancer import calculate_specificity_score, enhance_specificity
from services.hook_engine.emotional_buckets import get_angle_info, detect_angle_from_text
from services.hook_engine.hook_db import get_historical_performance
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

def score_hook(hook_text: str, template: HookTemplate = None, angle: str = None) -> Dict:
    """
    Score a hook for predicted CTR
    
    Args:
        hook_text: The hook text
        template: Optional template used
        angle: Optional emotional angle
        
    Returns:
        Dictionary with scoring details
    """
    # Enhance specificity first
    enhanced_text = enhance_specificity(hook_text)
    
    # Detect angle if not provided
    if not angle:
        angle = detect_angle_from_text(enhanced_text)
    
    # Get angle info
    angle_info = get_angle_info(angle)
    
    # Calculate curiosity metrics
    curiosity_metrics = score_hook_curiosity(enhanced_text)
    
    # Calculate specificity
    specificity_score = calculate_specificity_score(enhanced_text)
    
    # Get historical performance
    historical_lift = 1.0
    if template:
        historical_lift = get_historical_performance(template.structure) or 1.0
        # Also use template weight
        historical_lift *= template.weight
    
    # Calculate base CTR score
    base_score = (
        curiosity_metrics["overall_score"] * 0.4 +
        specificity_score * 0.3 +
        (historical_lift - 1.0) * 0.3
    )
    
    # Apply angle multiplier
    angle_multiplier = angle_info["ctr_multiplier"]
    predicted_ctr_score = base_score * angle_multiplier
    
    # Cap at 1.0
    predicted_ctr_score = min(1.0, predicted_ctr_score)
    
    return {
        "hook": enhanced_text,
        "predicted_ctr_score": predicted_ctr_score,
        "angle": angle,
        "curiosity_score": curiosity_metrics["curiosity_score"],
        "specificity_score": specificity_score,
        "historical_lift": historical_lift,
        "base_score": base_score,
        "angle_multiplier": angle_multiplier
    }

async def generate_hooks_for_topic(topic: str, count: int = 10, use_ml: bool = True) -> List[Dict]:
    """
    Generate and score multiple hooks for a topic
    
    Args:
        topic: Topic text
        count: Number of hooks to generate
        
    Returns:
        List of scored hooks, sorted by predicted CTR
    """
    from services.hook_engine.template_library import get_all_templates
    
    templates = get_all_templates()
    scored_hooks = []
    
    # Generate hooks from templates
    for template in templates[:count * 2]:  # Generate more, then filter
        try:
            # Simple formatting (in production, use NLP to extract entities)
            hook_text = template.format(
                target=topic,
                timeframe="72 hours",
                count="10",
                role="developer"
            )
            
            # Score the hook (use ML if available)
            if use_ml:
                try:
                    from services.hook_engine.ml_hook_scorer import score_hook_with_ml
                    score_result = score_hook_with_ml(hook_text, template.structure, template.angle)
                    
                    # Add emotional resonance analysis
                    from services.hook_engine.emotional_resonance_analyzer import analyze_emotional_resonance
                    resonance = analyze_emotional_resonance(hook_text, template.angle)
                    score_result["emotional_resonance"] = resonance["resonance_score"]
                    score_result["novelty_score"] = resonance["novelty_score"]
                    
                except Exception as e:
                    logger.warning(f"ML scoring failed, using heuristic: {e}")
                    score_result = score_hook(hook_text, template, template.angle)
            else:
                score_result = score_hook(hook_text, template, template.angle)
            scored_hooks.append(score_result)
        except Exception as e:
            logger.warning(f"Error generating hook from template {template.structure}: {e}")
            continue
    
    # Sort by predicted CTR score
    scored_hooks.sort(key=lambda x: x["predicted_ctr_score"], reverse=True)
    
    # Return top N
    return scored_hooks[:count]
