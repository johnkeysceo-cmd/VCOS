"""
Orchestration - Experiment Manager
Manages A/B tests and experiments
"""

import os
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def create_experiment(config: Dict) -> str:
    """
    Create a new experiment
    
    Args:
        config: Experiment configuration
        
    Returns:
        Experiment ID
    """
    experiment_id = f"exp_{int(os.time())}"
    logger.info(f"Created experiment: {experiment_id}")
    return experiment_id

def get_experiment_results(experiment_id: str) -> Dict:
    """Get experiment results"""
    import os
    from shared.config.settings import settings
    
    experiment_path = os.path.join(settings.DATA_ROOT, "ab_tests", f"{experiment_id}.json")
    
    if not os.path.exists(experiment_path):
        return {"error": "Experiment not found"}
    
    import json
    with open(experiment_path, 'r') as f:
        experiment_data = json.load(f)
    
    return {
        "experiment_id": experiment_id,
        "results": experiment_data.get("results"),
        "variant_a": experiment_data.get("variant_a"),
        "variant_b": experiment_data.get("variant_b"),
        "created_at": experiment_data.get("created_at"),
        "completed_at": experiment_data.get("completed_at")
    }
