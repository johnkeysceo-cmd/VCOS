"""
Feedback Trainer - Weight Registry
Persistent storage for model weights
"""

import os
import json
from typing import Dict, Optional
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

WEIGHTS_FILE = os.path.join(settings.DATA_ROOT, "weights.json")

def load_weights() -> Dict:
    """Load weights from persistent storage"""
    if not os.path.exists(WEIGHTS_FILE):
        return {}
    
    try:
        with open(WEIGHTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading weights: {e}")
        return {}

def save_weights(weights: Dict):
    """Save weights to persistent storage"""
    os.makedirs(os.path.dirname(WEIGHTS_FILE), exist_ok=True)
    
    try:
        with open(WEIGHTS_FILE, 'w') as f:
            json.dump(weights, f, indent=2)
        logger.info(f"Saved weights to {WEIGHTS_FILE}")
    except Exception as e:
        logger.error(f"Error saving weights: {e}")

def get_template_weight(template_name: str) -> float:
    """Get weight for a template"""
    weights = load_weights()
    return weights.get("templates", {}).get(template_name, 1.0)

def update_template_weight(template_name: str, weight: float):
    """Update weight for a template"""
    weights = load_weights()
    
    if "templates" not in weights:
        weights["templates"] = {}
    
    weights["templates"][template_name] = weight
    save_weights(weights)

def get_angle_weight(angle: str) -> float:
    """Get weight for an emotional angle"""
    weights = load_weights()
    return weights.get("angles", {}).get(angle, 1.0)

def update_angle_weight(angle: str, weight: float):
    """Update weight for an emotional angle"""
    weights = load_weights()
    
    if "angles" not in weights:
        weights["angles"] = {}
    
    weights["angles"][angle] = weight
    save_weights(weights)
