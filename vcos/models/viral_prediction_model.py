"""
ML Models - Viral Prediction Model
Deep learning model to predict viral potential
"""

import os
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ViralPredictionModel:
    """
    Neural network model for viral prediction
    Uses multi-layer perceptron to predict viral score
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), "viral_prediction_model.pkl")
        self.model = None
        self.feature_scaler = None
        self._load_model()
    
    def _load_model(self):
        """Load trained model"""
        try:
            import pickle
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data.get("model")
                    self.feature_scaler = model_data.get("scaler")
                logger.info(f"Loaded viral prediction model from {self.model_path}")
            else:
                logger.info("Model not found, will train on first use")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def predict_viral_score(
        self,
        hook_features: List[float],
        retention_features: List[float],
        topic_features: List[float]
    ) -> Dict:
        """
        Predict viral score from combined features
        
        Args:
            hook_features: Hook feature vector (22 features)
            retention_features: Retention feature vector (13 features)
            topic_features: Topic feature vector (12 features)
            
        Returns:
            Prediction dictionary with viral score and components
        """
        # Combine all features
        combined_features = hook_features + retention_features + topic_features
        
        if self.model and self.feature_scaler:
            try:
                # Scale features
                features_scaled = self.feature_scaler.transform([combined_features])
                
                # Predict
                viral_score = float(self.model.predict(features_scaled)[0])
                
                # Get feature importance (if available)
                feature_importance = self._get_feature_importance(combined_features)
                
                return {
                    "viral_score": max(0.0, min(1.0, viral_score)),
                    "confidence": 0.9,
                    "feature_importance": feature_importance,
                    "model_used": "neural_network"
                }
            except Exception as e:
                logger.error(f"Model prediction error: {e}")
        
        # Fallback: heuristic prediction
        return self._heuristic_prediction(hook_features, retention_features, topic_features)
    
    def _heuristic_prediction(
        self,
        hook_features: List[float],
        retention_features: List[float],
        topic_features: List[float]
    ) -> Dict:
        """Heuristic fallback prediction"""
        # Simple weighted average
        hook_score = sum(hook_features[:5]) / 5.0 if hook_features else 0.5
        retention_score = sum(retention_features[:5]) / 5.0 if retention_features else 0.5
        topic_score = sum(topic_features[:5]) / 5.0 if topic_features else 0.5
        
        viral_score = (hook_score * 0.4 + retention_score * 0.4 + topic_score * 0.2)
        
        return {
            "viral_score": max(0.0, min(1.0, viral_score)),
            "confidence": 0.5,
            "feature_importance": {},
            "model_used": "heuristic"
        }
    
    def _get_feature_importance(self, features: List[float]) -> Dict:
        """Get feature importance (placeholder - would use SHAP or similar)"""
        return {
            "top_features": [
                {"index": i, "value": features[i]}
                for i in sorted(range(len(features)), key=lambda i: abs(features[i]), reverse=True)[:5]
            ]
        }

class ReinforcementLearningAgent:
    """
    Reinforcement Learning Agent for content optimization
    Uses Q-learning to learn optimal content strategies
    """
    
    def __init__(self, state_size: int = 47, action_size: int = 10):
        self.state_size = state_size  # Combined feature vector size
        self.action_size = action_size  # Number of possible actions (hook angles, pacing, etc.)
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploration rate
        self._load_q_table()
    
    def _load_q_table(self):
        """Load Q-table from disk"""
        q_table_path = os.path.join(os.path.dirname(__file__), "q_table.json")
        try:
            import json
            if os.path.exists(q_table_path):
                with open(q_table_path, 'r') as f:
                    self.q_table = json.load(f)
                logger.info(f"Loaded Q-table with {len(self.q_table)} states")
        except Exception as e:
            logger.warning(f"Could not load Q-table: {e}")
    
    def _save_q_table(self):
        """Save Q-table to disk"""
        q_table_path = os.path.join(os.path.dirname(__file__), "q_table.json")
        try:
            import json
            os.makedirs(os.path.dirname(q_table_path), exist_ok=True)
            with open(q_table_path, 'w') as f:
                json.dump(self.q_table, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving Q-table: {e}")
    
    def _state_to_key(self, state: List[float]) -> str:
        """Convert state vector to Q-table key"""
        # Discretize state for Q-learning
        discretized = [int(s * 10) / 10.0 for s in state[:10]]  # Use first 10 features
        return str(discretized)
    
    def select_action(self, state: List[float], explore: bool = True) -> int:
        """
        Select action using epsilon-greedy policy
        
        Args:
            state: Current state vector
            explore: Whether to explore (True) or exploit (False)
            
        Returns:
            Action index
        """
        state_key = self._state_to_key(state)
        
        # Initialize Q-values for this state if not seen
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.action_size
        
        # Epsilon-greedy: explore or exploit
        if explore and np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.randint(0, self.action_size)
        else:
            # Exploit: best known action
            q_values = self.q_table[state_key]
            return int(np.argmax(q_values))
    
    def update_q_value(
        self,
        state: List[float],
        action: int,
        reward: float,
        next_state: List[float],
        done: bool = False
    ):
        """
        Update Q-value using Q-learning
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)
        
        # Initialize if needed
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.action_size
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = [0.0] * self.action_size
        
        # Q-learning update
        current_q = self.q_table[state_key][action]
        max_next_q = max(self.q_table[next_state_key]) if not done else 0.0
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state_key][action] = new_q
        
        # Save periodically
        if len(self.q_table) % 10 == 0:
            self._save_q_table()
    
    def get_best_action(self, state: List[float]) -> int:
        """Get best action for a state (exploitation only)"""
        return self.select_action(state, explore=False)
    
    def get_action_recommendations(self, state: List[float]) -> Dict:
        """
        Get action recommendations with Q-values
        
        Args:
            state: Current state
            
        Returns:
            Action recommendations
        """
        state_key = self._state_to_key(state)
        
        if state_key not in self.q_table:
            return {"actions": [], "message": "No data for this state"}
        
        q_values = self.q_table[state_key]
        
        # Get top 3 actions
        top_actions = sorted(
            enumerate(q_values),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        action_names = [
            "speed_angle", "replacement_angle", "controversy_angle",
            "challenge_angle", "pacing_1.0x", "pacing_1.06x",
            "pacing_1.12x", "zoom_aggressive", "zoom_moderate", "zoom_subtle"
        ]
        
        return {
            "recommended_actions": [
                {
                    "action": action_names[idx],
                    "q_value": q_val,
                    "confidence": min(1.0, q_val / 10.0)  # Normalize
                }
                for idx, q_val in top_actions
            ],
            "exploration_rate": self.epsilon
        }

# Global model instances
viral_prediction_model = ViralPredictionModel()
rl_agent = ReinforcementLearningAgent()
