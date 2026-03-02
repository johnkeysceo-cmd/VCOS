"""
Feedback Trainer - Reinforcement Loop
Main feedback training loop that updates all models
"""

from services.feedback_trainer.hook_weight_updater import update_weight
from services.feedback_trainer.angle_performance_ranker import rank_angles
from services.feedback_trainer.cluster_strength_model import update_cluster
from services.feedback_trainer.confidence_weighting import weight_update_with_confidence
from services.analytics_ingestion.analytics_db import get_db_connection
from services.analytics_ingestion.real_time_analytics import real_time_adapter
from shared.objectives.viral_score import compute_viral_score_from_metrics
import logging

logger = logging.getLogger(__name__)

async def run_reinforcement_loop():
    """
    Run the reinforcement learning loop
    Updates all models based on recent performance data
    """
    logger.info("Starting reinforcement loop...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get recent analytics (last 24 hours)
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
            video_id
        FROM analytics
        WHERE timestamp > datetime('now', '-1 day')
        ORDER BY timestamp DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        logger.info("No recent analytics data for training")
        return
    
    # Check for algorithm shifts
    recent_metrics = [
        {
            "retention_3s": r[3],
            "retention_50pct": r[4],
            "completion_rate": r[5],
            "shares_per_1k": r[6]
        }
        for r in results[:10]
    ]
    
    for platform in ["tiktok", "instagram", "youtube"]:
        shift_result = real_time_adapter.detect_algorithm_shift(platform, recent_metrics)
        if shift_result["shift_detected"]:
            adaptation = real_time_adapter.adapt_hook_strategy(platform, shift_result)
            logger.info(f"Algorithm shift on {platform}: {adaptation['action']}")
    
    # Update hook weights with confidence weighting
    for row in results:
        hook_type = row[0]
        if not hook_type:
            continue
        
        # Compute viral score
        metrics = {
            "retention_50pct": row[4] or 0.0,
            "completion_rate": row[5] or 0.0,
            "shares_per_1k": row[6] or 0.0,
            "comment_velocity": row[7] or 0.0,
            "view_velocity": row[8] or 0.0
        }
        
        viral_score = compute_viral_score_from_metrics(metrics)
        
        # Get view count (would be in analytics in production)
        views = 1000  # Placeholder
        
        # Update with confidence weighting
        weight_update_with_confidence(
            hook_type,
            viral_score / 0.5,  # Normalize to lift (0.5 baseline)
            views,
            shares=int(metrics["shares_per_1k"] * views / 1000),
            comments=int(metrics["comment_velocity"] * views / 1000)
        )
    
    # Rank angles
    angle_ranks = rank_angles()
    logger.info(f"Updated angle rankings: {angle_ranks}")
    
    # Update clusters
    for row in results:
        cluster = row[2]
        if cluster:
            metrics = {
                "retention_50pct": row[4] or 0.0,
                "completion_rate": row[5] or 0.0,
                "shares_per_1k": row[6] or 0.0
            }
            viral_score = compute_viral_score_from_metrics(metrics)
            update_cluster(cluster, viral_score)
    
    logger.info("Reinforcement loop completed")
