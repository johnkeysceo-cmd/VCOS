"""
ML Models - Training Pipeline
Infrastructure for training ML models
"""

import os
import json
import pickle
from typing import List, Dict, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def prepare_training_data(
    feature_vectors: List[List[float]],
    labels: List[float],
    test_split: float = 0.2
) -> Tuple[List[List[float]], List[float], List[List[float]], List[float]]:
    """
    Prepare training data with train/test split
    
    Args:
        feature_vectors: List of feature vectors
        labels: List of labels
        test_split: Test set proportion
        
    Returns:
        (X_train, y_train, X_test, y_test)
    """
    split_idx = int(len(feature_vectors) * (1 - test_split))
    
    X_train = feature_vectors[:split_idx]
    y_train = labels[:split_idx]
    X_test = feature_vectors[split_idx:]
    y_test = labels[split_idx:]
    
    logger.info(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
    
    return X_train, y_train, X_test, y_test

def train_hook_ctr_model(
    feature_vectors: List[List[float]],
    ctr_labels: List[float],
    model_type: str = "random_forest"
) -> Dict:
    """
    Train hook CTR prediction model
    
    Args:
        feature_vectors: Hook feature vectors
        ctr_labels: Actual CTR values
        model_type: Model type (random_forest, gradient_boosting, neural_network)
        
    Returns:
        Training result dictionary
    """
    try:
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.metrics import mean_squared_error, r2_score
        from sklearn.model_selection import cross_val_score
        
        # Prepare data
        X_train, y_train, X_test, y_test = prepare_training_data(feature_vectors, ctr_labels)
        
        # Train model
        if model_type == "random_forest":
            model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        elif model_type == "gradient_boosting":
            model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        
        model.fit(X_train, y_train)
        
        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        
        # Save model
        model_path = os.path.join(os.path.dirname(__file__), "hook_ctr_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Hook CTR model trained: R²={test_score:.3f}, MSE={mse:.4f}")
        
        return {
            "success": True,
            "model_type": model_type,
            "train_score": train_score,
            "test_score": test_score,
            "mse": mse,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "model_path": model_path
        }
        
    except ImportError:
        logger.error("scikit-learn not installed. Install with: pip install scikit-learn")
        return {"success": False, "error": "scikit-learn not installed"}
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return {"success": False, "error": str(e)}

def train_retention_forecast_model(
    feature_vectors: List[List[float]],
    retention_labels: List[float],
    model_type: str = "gradient_boosting"
) -> Dict:
    """
    Train retention forecast model
    
    Args:
        feature_vectors: Retention feature vectors
        retention_labels: Actual retention values
        model_type: Model type
        
    Returns:
        Training result dictionary
    """
    try:
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.metrics import mean_squared_error, r2_score
        
        X_train, y_train, X_test, y_test = prepare_training_data(feature_vectors, retention_labels)
        
        model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        model.fit(X_train, y_train)
        
        test_score = model.score(X_test, y_test)
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        
        model_path = os.path.join(os.path.dirname(__file__), "retention_forecast_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Retention forecast model trained: R²={test_score:.3f}, MSE={mse:.4f}")
        
        return {
            "success": True,
            "test_score": test_score,
            "mse": mse,
            "model_path": model_path
        }
        
    except Exception as e:
        logger.error(f"Error training retention model: {e}")
        return {"success": False, "error": str(e)}

def collect_training_data_from_analytics() -> Tuple[List[List[float]], List[float]]:
    """
    Collect training data from analytics database
    
    Returns:
        (feature_vectors, labels) for hook CTR model
    """
    from services.analytics_ingestion.analytics_db import get_db_connection
    from shared.feature_definitions.canonical_feature_vector import HookFeatureVector
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get analytics with hook data
    cursor.execute("""
        SELECT hook_type, emotional_angle, retention_3s, shares_per_1k, velocity_30min
        FROM analytics
        WHERE hook_type IS NOT NULL
        LIMIT 1000
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    feature_vectors = []
    labels = []
    
    for row in rows:
        # Build feature vector (simplified - would use full HookFeatureVector)
        # Use retention_3s as proxy for CTR
        hook_type = row[0]
        angle = row[1]
        retention = row[2]
        
        # Simple feature vector (would be full HookFeatureVector in production)
        features = [
            len(hook_type),  # text_length
            len(hook_type.split()),  # word_count
            1.0 if "?" in hook_type else 0.0,  # question_mark
            # ... more features
        ]
        
        feature_vectors.append(features)
        labels.append(retention)  # Use retention as label
    
    logger.info(f"Collected {len(feature_vectors)} training samples")
    
    return feature_vectors, labels
