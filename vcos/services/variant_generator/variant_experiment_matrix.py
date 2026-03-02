"""
Variant Generator - Variant Experiment Matrix
Formal A/B grid for variant testing
"""

from typing import List, Dict
from itertools import product
import logging

logger = logging.getLogger(__name__)

# Experiment dimensions
EXPERIMENT_DIMENSIONS = {
    "hook_angle": ["speed", "replacement", "controversy", "challenge"],
    "pacing": [1.0, 1.03, 1.06, 1.09, 1.12],
    "subtitle_theme": ["bold", "minimal", "colorful", "outline"],
    "zoom_density": ["aggressive", "moderate", "subtle", "minimal"]
}

def generate_experiment_matrix() -> List[Dict]:
    """
    Generate full experiment matrix
    
    Returns:
        List of all variant combinations
    """
    combinations = []
    
    for combo in product(
        EXPERIMENT_DIMENSIONS["hook_angle"],
        EXPERIMENT_DIMENSIONS["pacing"],
        EXPERIMENT_DIMENSIONS["subtitle_theme"],
        EXPERIMENT_DIMENSIONS["zoom_density"]
    ):
        combinations.append({
            "hook_angle": combo[0],
            "pacing": combo[1],
            "subtitle_theme": combo[2],
            "zoom_density": combo[3],
            "variant_id": f"{combo[0]}_{combo[1]}_{combo[2]}_{combo[3]}"
        })
    
    logger.info(f"Generated {len(combinations)} experiment combinations")
    
    return combinations

def select_top_variants(experiment_results: List[Dict], top_n: int = 20) -> List[Dict]:
    """
    Select top performing variants from experiment matrix
    
    Args:
        experiment_results: Results with viral_score
        top_n: Number of top variants to select
        
    Returns:
        Top performing variants
    """
    # Sort by viral score
    sorted_results = sorted(experiment_results, key=lambda x: x.get("viral_score", 0), reverse=True)
    
    return sorted_results[:top_n]
