"""
Title & Thumbnail Engine - A/B Test Registry
Tracks A/B tests for titles and thumbnails
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from shared.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def register_ab_test(video_id: str, variant_a: Dict, variant_b: Dict) -> str:
    """
    Register an A/B test
    
    Args:
        video_id: Video ID
        variant_a: Variant A (title/thumbnail)
        variant_b: Variant B (title/thumbnail)
        
    Returns:
        Test ID
    """
    test_id = f"ab_test_{video_id}_{int(datetime.now().timestamp())}"
    
    test_data = {
        "test_id": test_id,
        "video_id": video_id,
        "variant_a": variant_a,
        "variant_b": variant_b,
        "created_at": datetime.now().isoformat(),
        "results": None
    }
    
    os.makedirs(settings.DATA_ROOT, exist_ok=True)
    test_path = os.path.join(settings.DATA_ROOT, "ab_tests", f"{test_id}.json")
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    
    with open(test_path, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    logger.info(f"Registered A/B test: {test_id}")
    
    return test_id

def update_ab_test_results(test_id: str, results: Dict):
    """Update A/B test results"""
    test_path = os.path.join(settings.DATA_ROOT, "ab_tests", f"{test_id}.json")
    
    if os.path.exists(test_path):
        with open(test_path, 'r') as f:
            test_data = json.load(f)
        
        test_data["results"] = results
        test_data["completed_at"] = datetime.now().isoformat()
        
        with open(test_path, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        logger.info(f"Updated A/B test results: {test_id}")
