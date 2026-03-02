"""
Canonical Feature Vector Definition
Unified feature space for all ML models
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class HookFeatureVector:
    """Feature vector for hook prediction"""
    # Text features
    text_length: int
    word_count: int
    question_mark: bool
    ellipsis: bool
    number_count: int
    specific_timeframe: bool  # Has "hours", "minutes", etc.
    
    # Emotional angle features
    angle_speed: float
    angle_replacement: float
    angle_controversy: float
    angle_challenge: float
    angle_secret: float
    angle_authority: float
    angle_proof: float
    
    # Specificity features
    specificity_score: float
    has_percentage: bool
    has_multiplier: bool  # "2x", "10x"
    
    # Curiosity features
    curiosity_score: float
    incompleteness_index: float
    surprise_delta: float
    
    # Historical features
    template_historical_lift: float
    angle_historical_lift: float
    
    def to_list(self) -> List[float]:
        """Convert to list for ML models"""
        return [
            float(self.text_length),
            float(self.word_count),
            float(self.question_mark),
            float(self.ellipsis),
            float(self.number_count),
            float(self.specific_timeframe),
            self.angle_speed,
            self.angle_replacement,
            self.angle_controversy,
            self.angle_challenge,
            self.angle_secret,
            self.angle_authority,
            self.angle_proof,
            self.specificity_score,
            float(self.has_percentage),
            float(self.has_multiplier),
            self.curiosity_score,
            self.incompleteness_index,
            self.surprise_delta,
            self.template_historical_lift,
            self.angle_historical_lift
        ]

@dataclass
class RetentionFeatureVector:
    """Feature vector for retention prediction"""
    # Video features
    video_length: float
    pacing_wpm: float
    silence_ratio: float  # Ratio of silence to total duration
    
    # Visual features
    zoom_frequency: float  # Zooms per minute
    transition_frequency: float
    subtitle_flash_rate: float
    motion_change_density: float
    
    # Content features
    sentence_count: int
    avg_sentence_length: float
    momentum_score: float
    idea_boundary_count: int
    
    # Hook features (from hook vector)
    hook_curiosity: float
    hook_specificity: float
    
    def to_list(self) -> List[float]:
        """Convert to list for ML models"""
        return [
            self.video_length,
            self.pacing_wpm,
            self.silence_ratio,
            self.zoom_frequency,
            self.transition_frequency,
            self.subtitle_flash_rate,
            self.motion_change_density,
            float(self.sentence_count),
            self.avg_sentence_length,
            self.momentum_score,
            float(self.idea_boundary_count),
            self.hook_curiosity,
            self.hook_specificity
        ]

@dataclass
class TopicFeatureVector:
    """Feature vector for topic performance prediction"""
    # Cluster features
    cluster_authority_score: float
    cluster_avg_retention: float
    cluster_avg_shares: float
    cluster_video_count: int
    
    # Topic features
    topic_length: int
    topic_word_count: int
    topic_has_number: bool
    topic_has_timeframe: bool
    
    # Momentum features
    cluster_momentum: float
    cluster_velocity_trend: float  # Recent velocity vs historical
    
    # Identity features
    cluster_consistency_score: float
    topic_entropy: float  # How different from usual topics
    
    def to_list(self) -> List[float]:
        """Convert to list for ML models"""
        return [
            self.cluster_authority_score,
            self.cluster_avg_retention,
            self.cluster_avg_shares,
            float(self.cluster_video_count),
            float(self.topic_length),
            float(self.topic_word_count),
            float(self.topic_has_number),
            float(self.topic_has_timeframe),
            self.cluster_momentum,
            self.cluster_velocity_trend,
            self.cluster_consistency_score,
            self.topic_entropy
        ]
