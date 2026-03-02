"""
Topic Engine - Meme Dynamics Tracker
Tracks meme dynamics and cultural shifts for better timing
"""

from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MemeDynamicsTracker:
    """Tracks meme dynamics and cultural shifts"""
    
    def __init__(self):
        self.meme_lifecycle = {}  # Track meme lifecycle stages
        self.cultural_shifts = []  # Track cultural shift events
    
    def analyze_meme_lifecycle(self, topic: str, cluster: str) -> Dict:
        """
        Analyze where a topic/meme is in its lifecycle
        
        Returns:
            Lifecycle analysis with recommendations
        """
        # Check if topic is in early, peak, or decline phase
        # This would integrate with trend APIs in production
        
        # Early phase: High novelty, low saturation
        # Peak phase: High engagement, high saturation
        # Decline phase: Low novelty, high saturation
        
        # Placeholder logic - would use actual trend data
        topic_lower = topic.lower()
        
        # Detect lifecycle indicators
        early_indicators = ["new", "just", "first", "introducing", "launched"]
        peak_indicators = ["viral", "trending", "everyone", "all over"]
        decline_indicators = ["old", "outdated", "replaced", "better than"]
        
        early_score = sum(1 for word in early_indicators if word in topic_lower)
        peak_score = sum(1 for word in peak_indicators if word in topic_lower)
        decline_score = sum(1 for word in decline_indicators if word in topic_lower)
        
        if early_score > peak_score and early_score > decline_score:
            phase = "early"
            opportunity_score = 0.9
            saturation_risk = 0.2
        elif peak_score > decline_score:
            phase = "peak"
            opportunity_score = 0.7
            saturation_risk = 0.6
        else:
            phase = "decline"
            opportunity_score = 0.3
            saturation_risk = 0.9
        
        return {
            "phase": phase,
            "opportunity_score": opportunity_score,
            "saturation_risk": saturation_risk,
            "recommendation": self._get_lifecycle_recommendation(phase)
        }
    
    def _get_lifecycle_recommendation(self, phase: str) -> str:
        """Get recommendation based on lifecycle phase"""
        recommendations = {
            "early": "High opportunity - create content now before saturation",
            "peak": "Moderate opportunity - differentiate strongly or wait for decline",
            "decline": "Low opportunity - consider pivoting to new angle or topic"
        }
        return recommendations.get(phase, "Unknown phase")
    
    def detect_cultural_shift(self, recent_topics: List[str]) -> Dict:
        """
        Detect cultural shifts from topic patterns
        
        Args:
            recent_topics: List of recent topics
            
        Returns:
            Cultural shift detection result
        """
        if len(recent_topics) < 10:
            return {"shift_detected": False, "confidence": 0.0}
        
        # Analyze topic diversity and novelty
        unique_words = set()
        for topic in recent_topics:
            unique_words.update(topic.lower().split())
        
        diversity_score = len(unique_words) / (len(recent_topics) * 5)  # Normalize
        
        # High diversity = potential cultural shift
        shift_detected = diversity_score > 0.6
        confidence = min(1.0, diversity_score)
        
        if shift_detected:
            logger.info(f"Cultural shift detected: diversity_score={diversity_score:.2f}")
        
        return {
            "shift_detected": shift_detected,
            "confidence": confidence,
            "diversity_score": diversity_score,
            "recommendation": "Explore new angles" if shift_detected else "Continue current strategy"
        }

# Global tracker
meme_dynamics_tracker = MemeDynamicsTracker()
