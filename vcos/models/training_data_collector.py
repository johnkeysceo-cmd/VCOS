"""
ML Models - Training Data Collector
Collects and prepares training data from analytics
"""

import os
import json
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from services.analytics_ingestion.analytics_db import get_db_connection
from shared.feature_definitions.canonical_feature_vector import (
    HookFeatureVector, RetentionFeatureVector, TopicFeatureVector
)
from shared.objectives.viral_score import compute_viral_score_from_metrics
import logging

logger = logging.getLogger(__name__)

class TrainingDataCollector:
    """Collects training data from analytics database"""
    
    def __init__(self):
        self.min_samples = 50  # Minimum samples needed for training
    
    def collect_hook_training_data(self, min_videos: int = 100) -> Tuple[List[List[float]], List[float]]:
        """
        Collect hook feature vectors and labels from analytics
        
        Args:
            min_videos: Minimum number of videos needed
            
        Returns:
            (feature_vectors, labels) where labels are CTR scores
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get analytics with hook data
        cursor.execute("""
            SELECT 
                hook_type,
                emotional_angle,
                retention_3s,
                retention_50pct,
                completion_rate,
                shares_per_1k,
                comments_per_1k,
                velocity_30min,
                topic_cluster
            FROM analytics
            WHERE hook_type IS NOT NULL
            AND retention_3s IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        """, (min_videos * 2,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < min_videos:
            logger.warning(f"Only {len(rows)} samples available, need {min_videos}")
            return [], []
        
        feature_vectors = []
        labels = []
        
        for row in rows:
            hook_type = row[0]
            angle = row[1]
            retention_3s = row[2] or 0.0
            
            # Build hook feature vector
            hook_vector = self._build_hook_feature_vector(hook_type, angle)
            feature_vectors.append(hook_vector.to_list())
            
            # Use retention_3s as proxy for CTR (early retention = good hook)
            labels.append(retention_3s)
        
        logger.info(f"Collected {len(feature_vectors)} hook training samples")
        
        return feature_vectors, labels
    
    def collect_retention_training_data(self, min_videos: int = 100) -> Tuple[List[List[float]], List[float]]:
        """
        Collect retention feature vectors and labels
        
        Args:
            min_videos: Minimum number of videos needed
            
        Returns:
            (feature_vectors, labels) where labels are retention_50pct
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                length,
                retention_3s,
                retention_50pct,
                completion_rate,
                shares_per_1k,
                hook_type,
                emotional_angle,
                topic_cluster
            FROM analytics
            WHERE retention_50pct IS NOT NULL
            AND length IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        """, (min_videos * 2,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < min_videos:
            logger.warning(f"Only {len(rows)} samples available, need {min_videos}")
            return [], []
        
        feature_vectors = []
        labels = []
        
        for row in rows:
            video_length = row[0] or 60.0
            retention_50pct = row[2] or 0.0
            
            # Build retention feature vector
            retention_vector = self._build_retention_feature_vector(row, video_length)
            feature_vectors.append(retention_vector.to_list())
            
            labels.append(retention_50pct)
        
        logger.info(f"Collected {len(feature_vectors)} retention training samples")
        
        return feature_vectors, labels
    
    def collect_viral_training_data(self, min_videos: int = 100) -> Tuple[List[List[float]], List[float]]:
        """
        Collect combined feature vectors for viral prediction
        
        Args:
            min_videos: Minimum number of videos needed
            
        Returns:
            (feature_vectors, labels) where labels are viral scores
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                hook_type,
                emotional_angle,
                topic_cluster,
                retention_3s,
                retention_50pct,
                completion_rate,
                shares_per_1k,
                comments_per_1k,
                velocity_30min,
                length
            FROM analytics
            WHERE retention_50pct IS NOT NULL
            AND hook_type IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        """, (min_videos * 2,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < min_videos:
            logger.warning(f"Only {len(rows)} samples available, need {min_videos}")
            return [], []
        
        feature_vectors = []
        labels = []
        
        for row in rows:
            # Build combined feature vector
            hook_vector = self._build_hook_feature_vector(row[0], row[1])
            retention_vector = self._build_retention_feature_vector(row, row[9] or 60.0)
            topic_vector = self._build_topic_feature_vector(row[2])
            
            # Combine all features
            combined = hook_vector.to_list() + retention_vector.to_list() + topic_vector.to_list()
            feature_vectors.append(combined)
            
            # Compute viral score as label
            metrics = {
                "retention_50pct": row[4] or 0.0,
                "completion_rate": row[5] or 0.0,
                "shares_per_1k": row[6] or 0.0,
                "comment_velocity": row[7] or 0.0,
                "view_velocity": row[8] or 0.0
            }
            viral_score = compute_viral_score_from_metrics(metrics)
            labels.append(viral_score.compute())
        
        logger.info(f"Collected {len(feature_vectors)} viral prediction training samples")
        
        return feature_vectors, labels
    
    def _build_hook_feature_vector(self, hook_type: str, angle: str) -> HookFeatureVector:
        """Build hook feature vector from data"""
        from services.hook_engine.curiosity_gap_model import score_hook_curiosity
        from services.hook_engine.specificity_enhancer import calculate_specificity_score
        from services.hook_engine.hook_db import get_historical_performance
        
        hook_text = hook_type or ""
        curiosity_metrics = score_hook_curiosity(hook_text)
        specificity = calculate_specificity_score(hook_text)
        historical_lift = get_historical_performance(hook_type) or 1.0
        
        # Angle features (one-hot encoding)
        angles = ["speed", "replacement", "controversy", "challenge", "secret", "authority", "proof"]
        angle_features = [1.0 if angle == a else 0.0 for a in angles]
        
        return HookFeatureVector(
            text_length=len(hook_text),
            word_count=len(hook_text.split()),
            question_mark="?" in hook_text,
            ellipsis="..." in hook_text,
            number_count=len([c for c in hook_text if c.isdigit()]),
            specific_timeframe=any(word in hook_text.lower() for word in ["hour", "minute", "day"]),
            angle_speed=angle_features[0],
            angle_replacement=angle_features[1],
            angle_controversy=angle_features[2],
            angle_challenge=angle_features[3],
            angle_secret=angle_features[4],
            angle_authority=angle_features[5],
            angle_proof=angle_features[6],
            specificity_score=specificity,
            has_percentage="%" in hook_text,
            has_multiplier=any(word in hook_text.lower() for word in ["x", "times"]),
            curiosity_score=curiosity_metrics["curiosity_score"],
            incompleteness_index=curiosity_metrics["incompleteness_index"],
            surprise_delta=curiosity_metrics["surprise_delta"],
            template_historical_lift=historical_lift,
            angle_historical_lift=1.0  # Would compute from analytics
        )
    
    def _build_retention_feature_vector(self, row: tuple, video_length: float) -> RetentionFeatureVector:
        """Build retention feature vector from data"""
        # Simplified - would use actual video analysis in production
        return RetentionFeatureVector(
            video_length=video_length,
            pacing_wpm=180.0,  # Would compute from transcript
            silence_ratio=0.05,  # Would compute from audio
            zoom_frequency=2.0,  # Would compute from video
            transition_frequency=1.5,
            subtitle_flash_rate=3.0,
            motion_change_density=0.1,
            sentence_count=20,  # Would compute from transcript
            avg_sentence_length=15.0,
            momentum_score=0.7,
            idea_boundary_count=3,
            hook_curiosity=0.7,
            hook_specificity=0.6
        )
    
    def _build_topic_feature_vector(self, cluster: str) -> TopicFeatureVector:
        """Build topic feature vector from data"""
        from services.topic_engine.topic_db import get_cluster_metrics
        from services.prioritization_engine.momentum_predictor import predict_momentum
        
        metrics = get_cluster_metrics(cluster)
        momentum = predict_momentum(cluster)
        
        return TopicFeatureVector(
            cluster_authority_score=0.7,  # Would compute
            cluster_avg_retention=metrics.get("avg_retention", 0.5),
            cluster_avg_shares=metrics.get("avg_shares_per_1k", 0.1),
            cluster_video_count=metrics.get("video_count", 0),
            topic_length=20,
            topic_word_count=5,
            topic_has_number=False,
            topic_has_timeframe=False,
            cluster_momentum=momentum,
            cluster_velocity_trend=1.0,
            cluster_consistency_score=0.8,
            topic_entropy=0.3
        )

# Global collector instance
training_data_collector = TrainingDataCollector()
