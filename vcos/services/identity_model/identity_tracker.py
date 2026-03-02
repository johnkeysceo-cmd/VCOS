"""
Identity Model - Identity Tracker
Tracks content consistency, topic entropy, and platform recognition strength
"""

from typing import Dict, List
from collections import Counter
import math
import logging

logger = logging.getLogger(__name__)

class IdentityTracker:
    """Tracks account identity consistency"""
    
    def __init__(self):
        self.topic_history: List[str] = []
        self.cluster_history: List[str] = []
        self.angle_history: List[str] = []
    
    def record_content(self, topic: str, cluster: str, angle: str):
        """Record a piece of content"""
        self.topic_history.append(topic)
        self.cluster_history.append(cluster)
        self.angle_history.append(angle)
    
    def compute_consistency_score(self) -> float:
        """
        Compute content consistency score (0.0 to 1.0)
        Higher = more consistent identity
        """
        if len(self.cluster_history) < 2:
            return 0.5  # Neutral if not enough data
        
        # Count cluster frequencies
        cluster_counts = Counter(self.cluster_history[-20:])  # Last 20 videos
        most_common_cluster = cluster_counts.most_common(1)[0]
        
        # Consistency = percentage of content in dominant cluster
        consistency = most_common_cluster[1] / len(self.cluster_history[-20:])
        
        return consistency
    
    def compute_topic_entropy(self) -> float:
        """
        Compute topic entropy (0.0 = very focused, 1.0 = very diverse)
        Lower entropy = stronger identity
        """
        if len(self.cluster_history) < 2:
            return 0.5
        
        cluster_counts = Counter(self.cluster_history[-20:])
        total = sum(cluster_counts.values())
        
        # Shannon entropy
        entropy = 0.0
        for count in cluster_counts.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Normalize to 0-1 (assuming max 5 clusters)
        max_entropy = math.log2(min(5, len(cluster_counts)))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        return normalized_entropy
    
    def compute_platform_recognition_strength(self, platform_cluster_scores: Dict[str, float]) -> float:
        """
        Compute how strongly platform recognizes this account's category
        
        Args:
            platform_cluster_scores: Scores per cluster from platform analytics
            
        Returns:
            Recognition strength (0.0 to 1.0)
        """
        if not platform_cluster_scores:
            return 0.0
        
        # Strongest cluster score = recognition strength
        max_score = max(platform_cluster_scores.values())
        
        return min(1.0, max_score)
    
    def get_identity_report(self) -> Dict:
        """Get comprehensive identity report"""
        return {
            "consistency_score": self.compute_consistency_score(),
            "topic_entropy": self.compute_topic_entropy(),
            "dominant_cluster": Counter(self.cluster_history[-20:]).most_common(1)[0][0] if self.cluster_history else None,
            "cluster_distribution": dict(Counter(self.cluster_history[-20:])),
            "total_content_count": len(self.cluster_history)
        }

# Global identity tracker instance
identity_tracker = IdentityTracker()
