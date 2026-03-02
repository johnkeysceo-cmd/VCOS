"""
Analytics Ingestion - Real-Time Analytics
Real-time analytics adaptation for platform algorithm changes
"""

from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RealTimeAnalyticsAdapter:
    """Adapts to real-time platform algorithm changes"""
    
    def __init__(self):
        self.algorithm_signals = {}
        self.adaptation_history = []
    
    def detect_algorithm_shift(self, platform: str, recent_metrics: List[Dict]) -> Dict:
        """
        Detect if platform algorithm has shifted
        
        Args:
            platform: Platform name
            recent_metrics: Recent analytics metrics
            
        Returns:
            Algorithm shift detection result
        """
        if len(recent_metrics) < 5:
            return {"shift_detected": False, "confidence": 0.0}
        
        # Compare recent vs historical averages
        recent_avg_retention = sum(m.get("retention_3s", 0) for m in recent_metrics[-5:]) / 5
        historical_avg_retention = sum(m.get("retention_3s", 0) for m in recent_metrics[:-5]) / max(len(recent_metrics) - 5, 1)
        
        retention_delta = recent_avg_retention - historical_avg_retention
        
        # Significant drop suggests algorithm shift
        shift_detected = abs(retention_delta) > 0.15
        confidence = min(1.0, abs(retention_delta) / 0.3)
        
        if shift_detected:
            logger.warning(
                f"Algorithm shift detected on {platform}: "
                f"retention delta = {retention_delta:.2f}"
            )
        
        return {
            "shift_detected": shift_detected,
            "confidence": confidence,
            "retention_delta": retention_delta,
            "recommendation": self._get_adaptation_recommendation(retention_delta)
        }
    
    def _get_adaptation_recommendation(self, retention_delta: float) -> str:
        """Get adaptation recommendation based on shift"""
        if retention_delta < -0.2:
            return "Major algorithm change - review hook strategy and content format"
        elif retention_delta < -0.1:
            return "Moderate shift - adjust pacing and visual stimulus"
        elif retention_delta > 0.1:
            return "Positive shift - current strategy working well"
        else:
            return "No significant change - continue current approach"
    
    def adapt_hook_strategy(self, platform: str, shift_result: Dict) -> Dict:
        """
        Adapt hook strategy based on algorithm shift
        
        Args:
            platform: Platform name
            shift_result: Algorithm shift detection result
            
        Returns:
            Adaptation strategy
        """
        if not shift_result["shift_detected"]:
            return {"action": "maintain", "changes": {}}
        
        retention_delta = shift_result["retention_delta"]
        
        # Adaptation strategies
        if retention_delta < -0.15:
            # Major drop - shift to different hook angles
            return {
                "action": "shift_angles",
                "changes": {
                    "preferred_angles": ["controversy", "challenge"],  # More engaging
                    "avoid_angles": ["authority", "proof"],  # Less engaging
                    "increase_specificity": True
                }
            }
        elif retention_delta < -0.1:
            # Moderate drop - adjust pacing
            return {
                "action": "adjust_pacing",
                "changes": {
                    "increase_pacing": True,
                    "target_wpm": 200,  # Faster
                    "increase_zoom_frequency": True
                }
            }
        else:
            return {"action": "maintain", "changes": {}}
    
    def get_platform_algorithm_state(self, platform: str) -> Dict:
        """Get current algorithm state for platform"""
        return self.algorithm_signals.get(platform, {
            "last_shift": None,
            "current_trend": "stable",
            "recommended_strategy": "maintain"
        })

# Global adapter instance
real_time_adapter = RealTimeAnalyticsAdapter()
