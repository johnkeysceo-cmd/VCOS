"""
Analytics Ingestion - Algorithm Monitor
Monitors platform algorithm changes and triggers retraining
"""

from typing import Dict, List
from datetime import datetime, timedelta
from services.analytics_ingestion.real_time_analytics import real_time_adapter
import logging

logger = logging.getLogger(__name__)

class AlgorithmMonitor:
    """Monitors platform algorithms and triggers retraining"""
    
    def __init__(self):
        self.retraining_threshold = 0.15  # 15% performance drop triggers retraining
        self.monitoring_window = 7  # Days to monitor
        self.last_retraining = {}
        self.retraining_cooldown = 3  # Days between retraining
    
    def monitor_platforms(self) -> Dict:
        """
        Monitor all platforms for algorithm changes
        
        Returns:
            Monitoring results with retraining recommendations
        """
        platforms = ["tiktok", "instagram", "youtube"]
        results = {}
        
        for platform in platforms:
            result = self.monitor_platform(platform)
            results[platform] = result
        
        return results
    
    def monitor_platform(self, platform: str) -> Dict:
        """
        Monitor a single platform
        
        Args:
            platform: Platform name
            
        Returns:
            Monitoring result
        """
        from services.analytics_ingestion.analytics_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recent metrics
        cursor.execute("""
            SELECT 
                retention_3s,
                retention_50pct,
                completion_rate,
                shares_per_1k,
                timestamp
            FROM analytics
            WHERE platform = ?
            AND timestamp > datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        """, (platform, self.monitoring_window))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 10:
            return {
                "platform": platform,
                "status": "insufficient_data",
                "retraining_needed": False,
                "reason": f"Only {len(rows)} samples in last {self.monitoring_window} days"
            }
        
        # Split into recent vs historical
        split_idx = len(rows) // 2
        recent = rows[:split_idx]
        historical = rows[split_idx:]
        
        # Calculate average performance
        recent_avg = self._calculate_avg_performance(recent)
        historical_avg = self._calculate_avg_performance(historical)
        
        # Calculate drop
        performance_drop = (historical_avg - recent_avg) / max(historical_avg, 0.01)
        
        # Check if retraining needed
        retraining_needed = (
            performance_drop >= self.retraining_threshold and
            self._can_retrain(platform)
        )
        
        result = {
            "platform": platform,
            "status": "monitoring",
            "recent_avg_performance": recent_avg,
            "historical_avg_performance": historical_avg,
            "performance_drop": performance_drop,
            "retraining_needed": retraining_needed,
            "recommendation": self._get_recommendation(performance_drop, retraining_needed)
        }
        
        if retraining_needed:
            logger.warning(
                f"Algorithm change detected on {platform}: "
                f"performance drop={performance_drop:.2%}"
            )
        
        return result
    
    def _calculate_avg_performance(self, rows: List) -> float:
        """Calculate average performance from rows"""
        if not rows:
            return 0.0
        
        scores = []
        for row in rows:
            retention_50 = row[1] or 0.0
            completion = row[2] or 0.0
            shares = row[3] or 0.0
            
            # Simple performance score
            score = (retention_50 * 0.5 + completion * 0.3 + shares * 0.2)
            scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _can_retrain(self, platform: str) -> bool:
        """Check if retraining is allowed (cooldown)"""
        if platform not in self.last_retraining:
            return True
        
        days_since = (datetime.now() - self.last_retraining[platform]).days
        return days_since >= self.retraining_cooldown
    
    def _get_recommendation(self, performance_drop: float, retraining_needed: bool) -> str:
        """Get recommendation based on performance drop"""
        if retraining_needed:
            return f"Retraining recommended: {performance_drop:.1%} performance drop detected"
        elif performance_drop > 0.05:
            return f"Monitor closely: {performance_drop:.1%} performance drop"
        else:
            return "Performance stable - no action needed"
    
    def mark_retrained(self, platform: str):
        """Mark platform as retrained"""
        self.last_retraining[platform] = datetime.now()
        logger.info(f"Marked {platform} as retrained")

# Global monitor
algorithm_monitor = AlgorithmMonitor()
