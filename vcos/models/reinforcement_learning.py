"""
ML Models - Reinforcement Learning
RL agent for learning optimal content strategies
"""

import os
import json
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
from models.viral_prediction_model import ReinforcementLearningAgent
from shared.objectives.viral_score import compute_viral_score_from_metrics
import logging

logger = logging.getLogger(__name__)

class ViralContentRLAgent:
    """
    Reinforcement Learning Agent for viral content optimization
    Learns optimal combinations of hooks, pacing, zoom, etc.
    """
    
    def __init__(self):
        self.agent = ReinforcementLearningAgent(state_size=47, action_size=10)
        self.episode_history = []
        self.training_enabled = True
    
    def select_content_strategy(self, current_state: List[float]) -> Dict:
        """
        Select content strategy using RL agent
        
        Args:
            current_state: Current feature vector (hook + retention + topic)
            
        Returns:
            Strategy dictionary with recommended actions
        """
        # Get action recommendations
        recommendations = self.agent.get_action_recommendations(current_state)
        
        # Map actions to actual strategy
        strategy = self._actions_to_strategy(recommendations)
        
        return strategy
    
    def _actions_to_strategy(self, recommendations: Dict) -> Dict:
        """Convert RL actions to content strategy"""
        if not recommendations.get("recommended_actions"):
            # Default strategy
            return {
                "hook_angle": "speed",
                "pacing_speed": 1.05,
                "zoom_density": "moderate",
                "subtitle_theme": "bold"
            }
        
        top_action = recommendations["recommended_actions"][0]
        action_name = top_action["action"]
        
        strategy = {}
        
        # Parse action name
        if "angle" in action_name:
            strategy["hook_angle"] = action_name.replace("_angle", "")
        elif "pacing" in action_name:
            speed_str = action_name.split("_")[1]
            strategy["pacing_speed"] = float(speed_str.replace("x", ""))
        elif "zoom" in action_name:
            strategy["zoom_density"] = action_name.split("_")[1]
        
        # Fill defaults
        strategy.setdefault("hook_angle", "speed")
        strategy.setdefault("pacing_speed", 1.05)
        strategy.setdefault("zoom_density", "moderate")
        strategy.setdefault("subtitle_theme", "bold")
        
        return strategy
    
    def learn_from_result(
        self,
        initial_state: List[float],
        action_taken: int,
        final_metrics: Dict,
        next_state: List[float]
    ):
        """
        Learn from content performance (RL update)
        
        Args:
            initial_state: State before content creation
            action_taken: Action that was taken
            final_metrics: Final performance metrics
            next_state: State after content performance
        """
        if not self.training_enabled:
            return
        
        # Compute reward from viral score
        viral_score = compute_viral_score_from_metrics(final_metrics)
        reward = viral_score.compute() * 10.0  # Scale reward (0-10)
        
        # Bonus for high performance
        if viral_score.compute() > 0.7:
            reward += 5.0
        if final_metrics.get("shares_per_1k", 0) > 10:
            reward += 3.0
        
        # Update Q-value
        self.agent.update_q_value(
            initial_state,
            action_taken,
            reward,
            next_state,
            done=False
        )
        
        # Record episode
        self.episode_history.append({
            "timestamp": datetime.now().isoformat(),
            "state": initial_state[:5],  # Store first 5 features
            "action": action_taken,
            "reward": reward,
            "viral_score": viral_score.compute()
        })
        
        logger.info(f"RL update: action={action_taken}, reward={reward:.2f}, viral_score={viral_score.compute():.2f}")
    
    def get_learning_statistics(self) -> Dict:
        """Get RL learning statistics"""
        if not self.episode_history:
            return {
                "episodes": 0,
                "avg_reward": 0.0,
                "avg_viral_score": 0.0
            }
        
        recent_episodes = self.episode_history[-50:]  # Last 50 episodes
        
        return {
            "total_episodes": len(self.episode_history),
            "recent_episodes": len(recent_episodes),
            "avg_reward": sum(e["reward"] for e in recent_episodes) / len(recent_episodes),
            "avg_viral_score": sum(e["viral_score"] for e in recent_episodes) / len(recent_episodes),
            "exploration_rate": self.agent.epsilon
        }

# Global RL agent
viral_rl_agent = ViralContentRLAgent()
