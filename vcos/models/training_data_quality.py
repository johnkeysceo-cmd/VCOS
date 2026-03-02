"""
ML Models - Training Data Quality
Validates and ensures quality of training data
"""

from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TrainingDataQualityValidator:
    """Validates training data quality before model training"""
    
    def __init__(self):
        self.min_samples = 100
        self.max_outlier_ratio = 0.1  # Max 10% outliers
        self.min_label_range = 0.2  # Labels should span at least 0.2 range
    
    def validate_training_data(
        self,
        feature_vectors: List[List[float]],
        labels: List[float]
    ) -> Dict:
        """
        Validate training data quality
        
        Args:
            feature_vectors: Feature vectors
            labels: Labels
            
        Returns:
            Validation result with quality metrics
        """
        if len(feature_vectors) < self.min_samples:
            return {
                "valid": False,
                "reason": f"Insufficient samples: {len(feature_vectors)} < {self.min_samples}",
                "quality_score": 0.0
            }
        
        # Check for missing values
        has_nan = any(
            any(np.isnan(val) or np.isinf(val) for val in features)
            for features in feature_vectors
        )
        
        if has_nan:
            return {
                "valid": False,
                "reason": "Contains NaN or Inf values",
                "quality_score": 0.0
            }
        
        # Check label distribution
        labels_array = np.array(labels)
        label_range = labels_array.max() - labels_array.min()
        
        if label_range < self.min_label_range:
            return {
                "valid": False,
                "reason": f"Labels too uniform: range={label_range:.3f} < {self.min_label_range}",
                "quality_score": 0.3
            }
        
        # Check for outliers
        outlier_ratio = self._detect_outliers(labels)
        
        if outlier_ratio > self.max_outlier_ratio:
            logger.warning(f"High outlier ratio: {outlier_ratio:.2%}")
        
        # Check feature variance
        feature_variance = self._check_feature_variance(feature_vectors)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            len(feature_vectors),
            label_range,
            outlier_ratio,
            feature_variance
        )
        
        return {
            "valid": quality_score >= 0.6,
            "quality_score": quality_score,
            "sample_count": len(feature_vectors),
            "label_range": label_range,
            "outlier_ratio": outlier_ratio,
            "feature_variance": feature_variance,
            "recommendations": self._get_quality_recommendations(
                quality_score,
                len(feature_vectors),
                label_range,
                outlier_ratio
            )
        }
    
    def _detect_outliers(self, labels: List[float]) -> float:
        """Detect outlier ratio using IQR method"""
        labels_array = np.array(labels)
        q1 = np.percentile(labels_array, 25)
        q3 = np.percentile(labels_array, 75)
        iqr = q3 - q1
        
        if iqr == 0:
            return 0.0
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = np.sum((labels_array < lower_bound) | (labels_array > upper_bound))
        return outliers / len(labels)
    
    def _check_feature_variance(self, feature_vectors: List[List[float]]) -> float:
        """Check feature variance (low variance = less informative)"""
        if not feature_vectors:
            return 0.0
        
        features_array = np.array(feature_vectors)
        variances = np.var(features_array, axis=0)
        
        # Average variance across features
        avg_variance = np.mean(variances)
        
        return float(avg_variance)
    
    def _calculate_quality_score(
        self,
        sample_count: int,
        label_range: float,
        outlier_ratio: float,
        feature_variance: float
    ) -> float:
        """Calculate overall quality score (0.0 to 1.0)"""
        # Sample count score (more is better, up to 1000)
        sample_score = min(1.0, sample_count / 1000.0)
        
        # Label range score (more range = better)
        range_score = min(1.0, label_range / 0.5)
        
        # Outlier score (fewer outliers = better)
        outlier_score = max(0.0, 1.0 - outlier_ratio / self.max_outlier_ratio)
        
        # Variance score (more variance = better, but not too much)
        variance_score = min(1.0, feature_variance * 10)
        
        # Weighted average
        quality_score = (
            sample_score * 0.3 +
            range_score * 0.3 +
            outlier_score * 0.2 +
            variance_score * 0.2
        )
        
        return quality_score
    
    def _get_quality_recommendations(
        self,
        quality_score: float,
        sample_count: int,
        label_range: float,
        outlier_ratio: float
    ) -> List[str]:
        """Get recommendations for improving data quality"""
        recommendations = []
        
        if sample_count < 200:
            recommendations.append(f"Collect more samples (currently {sample_count}, target: 200+)")
        
        if label_range < 0.3:
            recommendations.append(f"Labels too uniform (range={label_range:.3f}). Ensure diverse performance data.")
        
        if outlier_ratio > 0.15:
            recommendations.append(f"High outlier ratio ({outlier_ratio:.2%}). Consider outlier removal or investigation.")
        
        if quality_score < 0.6:
            recommendations.append("Overall data quality is low. Review data collection process.")
        
        if not recommendations:
            recommendations.append("Data quality is good. Ready for training.")
        
        return recommendations

# Global validator
training_data_validator = TrainingDataQualityValidator()
