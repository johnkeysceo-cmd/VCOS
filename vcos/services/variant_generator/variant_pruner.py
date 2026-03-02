"""
Variant Generator - Variant Pruner
Prunes low-performing variants before production
"""

from typing import List, Dict
from models.viral_prediction_model import viral_prediction_model
from models.model_interfaces import hook_ctr_model
from shared.objectives.viral_score import compute_viral_score_from_metrics
import logging

logger = logging.getLogger(__name__)

class VariantPruner:
    """Prunes variants based on predicted performance"""
    
    def __init__(self):
        self.min_viral_score = 0.5  # Minimum predicted viral score
        self.min_ctr_score = 0.4  # Minimum predicted CTR
        self.max_variants_to_keep = 20  # Maximum variants to keep
    
    def prune_variants(
        self,
        variants: List[Dict],
        base_features: Dict = None
    ) -> List[Dict]:
        """
        Prune variants based on predicted performance
        
        Args:
            variants: List of variant configurations
            base_features: Base feature vector for predictions
            
        Returns:
            Pruned list of high-performing variants
        """
        if not variants:
            return []
        
        scored_variants = []
        
        for variant in variants:
            # Predict performance
            prediction = self._predict_variant_performance(variant, base_features)
            
            if prediction["keep"]:
                scored_variants.append({
                    **variant,
                    "predicted_viral_score": prediction["viral_score"],
                    "predicted_ctr": prediction["ctr_score"],
                    "prune_score": prediction["prune_score"]
                })
        
        # Sort by prune score (higher = better)
        scored_variants.sort(key=lambda x: x["prune_score"], reverse=True)
        
        # Keep top N
        pruned = scored_variants[:self.max_variants_to_keep]
        
        logger.info(f"Pruned {len(variants)} variants to {len(pruned)} high-performing variants")
        
        return pruned
    
    def _predict_variant_performance(
        self,
        variant: Dict,
        base_features: Dict = None
    ) -> Dict:
        """
        Predict variant performance
        
        Returns:
            Prediction with keep/discard decision
        """
        # Extract variant features
        hook_features = variant.get("hook_features", [0.5] * 22)
        retention_features = variant.get("retention_features", [0.5] * 13)
        topic_features = variant.get("topic_features", [0.5] * 12)
        
        # Predict viral score
        viral_prediction = viral_prediction_model.predict_viral_score(
            hook_features=hook_features,
            retention_features=retention_features,
            topic_features=topic_features
        )
        
        viral_score = viral_prediction["viral_score"]
        
        # Predict CTR
        ctr_score = hook_ctr_model.predict(hook_features)
        
        # Combined prune score
        prune_score = (viral_score * 0.6 + ctr_score * 0.4)
        
        # Decision: keep if above thresholds
        keep = (
            viral_score >= self.min_viral_score and
            ctr_score >= self.min_ctr_score
        )
        
        return {
            "keep": keep,
            "viral_score": viral_score,
            "ctr_score": ctr_score,
            "prune_score": prune_score
        }
    
    def set_thresholds(
        self,
        min_viral_score: float = None,
        min_ctr_score: float = None,
        max_variants: int = None
    ):
        """Update pruning thresholds"""
        if min_viral_score is not None:
            self.min_viral_score = min_viral_score
        if min_ctr_score is not None:
            self.min_ctr_score = min_ctr_score
        if max_variants is not None:
            self.max_variants_to_keep = max_variants
        
        logger.info(
            f"Updated thresholds: viral_score>={self.min_viral_score}, "
            f"ctr>={self.min_ctr_score}, max_variants={self.max_variants_to_keep}"
        )

# Global pruner
variant_pruner = VariantPruner()
