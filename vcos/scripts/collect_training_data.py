#!/usr/bin/env python3
"""
VCOS Training Data Collection
Collects training data from analytics and exports for model training
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.training_data_collector import training_data_collector
from shared.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_and_export_data():
    """Collect training data and export to files"""
    logger.info("Collecting training data from analytics...")
    
    # Collect data
    hook_features, hook_labels = training_data_collector.collect_hook_training_data(10)
    retention_features, retention_labels = training_data_collector.collect_retention_training_data(10)
    viral_features, viral_labels = training_data_collector.collect_viral_training_data(10)
    
    # Export to JSON files
    output_dir = Path(settings.TRAINING_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    datasets = {
        "hook_ctr": {
            "features": hook_features,
            "labels": hook_labels,
            "count": len(hook_features)
        },
        "retention": {
            "features": retention_features,
            "labels": retention_labels,
            "count": len(retention_features)
        },
        "viral_prediction": {
            "features": viral_features,
            "labels": viral_labels,
            "count": len(viral_features)
        }
    }
    
    # Save each dataset
    for name, data in datasets.items():
        output_file = output_dir / f"{name}_training_data.json"
        
        export_data = {
            "dataset": name,
            "collected_at": datetime.now().isoformat(),
            "sample_count": data["count"],
            "features": data["features"],
            "labels": data["labels"]
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported {data['count']} samples to {output_file}")
    
    # Summary
    total_samples = sum(d["count"] for d in datasets.values())
    logger.info(f"\nTotal training samples collected: {total_samples}")
    
    if total_samples < 100:
        logger.warning(f"⚠️  Low sample count ({total_samples}). Need at least 100 for reliable training.")
        logger.warning("Create more content batches and collect analytics to increase sample size.")
    
    return total_samples

if __name__ == "__main__":
    collect_and_export_data()
