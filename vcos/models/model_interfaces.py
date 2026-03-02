"""
ML Models - Model Interfaces
Interfaces for trained ML models
"""

from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)

class HookCTRModel:
    """Hook CTR prediction model interface"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), "hook_ctr_model.pkl")
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load trained model"""
        try:
            import pickle
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded hook CTR model from {self.model_path}")
            else:
                logger.warning(f"Model not found at {self.model_path}, using heuristic fallback")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def predict(self, feature_vector: List[float]) -> float:
        """
        Predict CTR for a hook
        
        Args:
            feature_vector: Hook feature vector
            
        Returns:
            Predicted CTR (0.0 to 1.0)
        """
        if self.model:
            try:
                return float(self.model.predict([feature_vector])[0])
            except Exception as e:
                logger.error(f"Model prediction error: {e}")
        
        # Fallback to heuristic
        return min(1.0, sum(feature_vector[:5]) / 5.0)

class RetentionForecastModel:
    """Retention forecasting model interface"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), "retention_forecast_model.pkl")
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load trained model"""
        try:
            import pickle
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded retention forecast model")
            else:
                logger.warning("Retention model not found, using heuristic fallback")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def predict(self, feature_vector: List[float]) -> float:
        """
        Predict retention score
        
        Args:
            feature_vector: Retention feature vector
            
        Returns:
            Predicted retention (0.0 to 1.0)
        """
        if self.model:
            try:
                return float(self.model.predict([feature_vector])[0])
            except Exception as e:
                logger.error(f"Model prediction error: {e}")
        
        # Fallback
        return 0.5

# Global model instances
hook_ctr_model = HookCTRModel()
retention_forecast_model = RetentionForecastModel()
