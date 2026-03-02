"""
Hook Engine - ML Hook Scorer
Uses trained ML models for hook scoring
"""

from models.viral_prediction_model import viral_prediction_model
from models.model_interfaces import hook_ctr_model
from shared.feature_definitions.canonical_feature_vector import HookFeatureVector
from services.hook_engine.curiosity_gap_model import score_hook_curiosity
from services.hook_engine.specificity_enhancer import calculate_specificity_score, enhance_specificity
from services.hook_engine.hook_db import get_historical_performance
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def score_hook_with_ml(hook_text: str, template_structure: str = None, angle: str = None) -> Dict:
    """
    Score hook using ML models
    
    Args:
        hook_text: Hook text
        template_structure: Template structure
        angle: Emotional angle
        
    Returns:
        Scored hook with ML predictions
    """
    # Enhance specificity
    enhanced_text = enhance_specificity(hook_text)
    
    # Build feature vector
    curiosity_metrics = score_hook_curiosity(enhanced_text)
    specificity = calculate_specificity_score(enhanced_text)
    historical_lift = get_historical_performance(template_structure) or 1.0
    
    # Angle features
    angles = ["speed", "replacement", "controversy", "challenge", "secret", "authority", "proof"]
    angle_features = [1.0 if angle == a else 0.0 for a in angles] if angle else [0.0] * 7
    
    hook_vector = HookFeatureVector(
        text_length=len(enhanced_text),
        word_count=len(enhanced_text.split()),
        question_mark="?" in enhanced_text,
        ellipsis="..." in enhanced_text,
        number_count=len([c for c in enhanced_text if c.isdigit()]),
        specific_timeframe=any(word in enhanced_text.lower() for word in ["hour", "minute", "day"]),
        angle_speed=angle_features[0],
        angle_replacement=angle_features[1],
        angle_controversy=angle_features[2],
        angle_challenge=angle_features[3],
        angle_secret=angle_features[4],
        angle_authority=angle_features[5],
        angle_proof=angle_features[6],
        specificity_score=specificity,
        has_percentage="%" in enhanced_text,
        has_multiplier=any(word in enhanced_text.lower() for word in ["x", "times"]),
        curiosity_score=curiosity_metrics["curiosity_score"],
        incompleteness_index=curiosity_metrics["incompleteness_index"],
        surprise_delta=curiosity_metrics["surprise_delta"],
        template_historical_lift=historical_lift,
        angle_historical_lift=1.0
    )
    
    # Predict CTR using ML model
    feature_list = hook_vector.to_list()
    predicted_ctr = hook_ctr_model.predict(feature_list)
    
    # Also get viral prediction (requires all features - use defaults for now)
    retention_features = [0.5] * 13  # Would be computed from video
    topic_features = [0.5] * 12  # Would be computed from topic
    
    viral_prediction = viral_prediction_model.predict_viral_score(
        hook_features=feature_list,
        retention_features=retention_features,
        topic_features=topic_features
    )
    
    return {
        "hook": enhanced_text,
        "predicted_ctr_score": predicted_ctr,
        "predicted_viral_score": viral_prediction["viral_score"],
        "viral_confidence": viral_prediction["confidence"],
        "angle": angle or "unknown",
        "curiosity_score": curiosity_metrics["curiosity_score"],
        "specificity_score": specificity,
        "historical_lift": historical_lift,
        "model_used": viral_prediction["model_used"]
    }
