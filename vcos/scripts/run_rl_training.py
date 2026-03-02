#!/usr/bin/env python3
"""
VCOS RL Training Script
Trains reinforcement learning agent from historical data
"""

import sys
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.reinforcement_learning import viral_rl_agent
from services.analytics_ingestion.analytics_db import get_db_connection
from models.training_data_collector import training_data_collector
from shared.objectives.viral_score import compute_viral_score_from_metrics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_rl_agent(min_episodes: int = 50):
    """
    Train RL agent from historical analytics data
    
    Args:
        min_episodes: Minimum number of episodes needed
    """
    logger.info("=" * 60)
    logger.info("RL Agent Training")
    logger.info("=" * 60)
    
    # Get historical data
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            hook_type,
            emotional_angle,
            topic_cluster,
            retention_50pct,
            completion_rate,
            shares_per_1k,
            comments_per_1k,
            velocity_30min
        FROM analytics
        WHERE hook_type IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT ?
    """, (min_episodes * 2,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) < min_episodes:
        logger.warning(f"Only {len(rows)} episodes available, need {min_episodes}")
        return False
    
    logger.info(f"Training RL agent on {len(rows)} episodes...")
    
    # Train on each episode
    for i, row in enumerate(rows):
        # Build state vector
        hook_vector = training_data_collector._build_hook_feature_vector(row[0], row[1])
        retention_vector = training_data_collector._build_retention_feature_vector(row, 60.0)
        topic_vector = training_data_collector._build_topic_feature_vector(row[2])
        
        state = hook_vector.to_list() + retention_vector.to_list() + topic_vector.to_list()
        
        # Select action (explore during training)
        action = viral_rl_agent.agent.select_action(state, explore=True)
        
        # Compute reward from metrics
        metrics = {
            "retention_50pct": row[3] or 0.0,
            "completion_rate": row[4] or 0.0,
            "shares_per_1k": row[5] or 0.0,
            "comment_velocity": row[6] or 0.0,
            "view_velocity": row[7] or 0.0
        }
        
        viral_score = compute_viral_score_from_metrics(metrics)
        reward = viral_score.compute() * 10.0
        
        # Next state (same for now - would be different in real scenario)
        next_state = state
        
        # Update Q-value
        viral_rl_agent.agent.update_q_value(state, action, reward, next_state)
        
        if (i + 1) % 10 == 0:
            logger.info(f"Trained on {i + 1}/{len(rows)} episodes")
    
    # Save Q-table
    viral_rl_agent.agent._save_q_table()
    
    # Get statistics
    stats = viral_rl_agent.get_learning_statistics()
    
    logger.info("\n" + "=" * 60)
    logger.info("RL Training Complete")
    logger.info("=" * 60)
    logger.info(f"Total episodes: {stats['total_episodes']}")
    logger.info(f"Average reward: {stats['avg_reward']:.2f}")
    logger.info(f"Average viral score: {stats['avg_viral_score']:.2f}")
    logger.info(f"Exploration rate: {stats['exploration_rate']:.2f}")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train VCOS RL agent")
    parser.add_argument(
        "--min-episodes",
        type=int,
        default=50,
        help="Minimum episodes needed (default: 50)"
    )
    
    args = parser.parse_args()
    
    success = train_rl_agent(args.min_episodes)
    sys.exit(0 if success else 1)
