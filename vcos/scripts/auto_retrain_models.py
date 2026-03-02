#!/usr/bin/env python3
"""
VCOS Auto Retrain Models
Automatically retrains models when algorithm changes detected
"""

import sys
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.analytics_ingestion.algorithm_monitor import algorithm_monitor
from models.train_models import train_all_models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def auto_retrain():
    """Auto-retrain models based on algorithm monitoring"""
    logger.info("=" * 60)
    logger.info("VCOS Auto Retrain")
    logger.info("=" * 60)
    
    # Monitor platforms
    logger.info("\nMonitoring platforms for algorithm changes...")
    monitoring_results = algorithm_monitor.monitor_platforms()
    
    retraining_needed = False
    
    for platform, result in monitoring_results.items():
        logger.info(f"\n{platform.upper()}:")
        logger.info(f"  Status: {result['status']}")
        
        if result.get("retraining_needed"):
            logger.warning(f"  ⚠️  Retraining needed: {result['recommendation']}")
            retraining_needed = True
        else:
            logger.info(f"  ✅ {result.get('recommendation', 'No action needed')}")
    
    if not retraining_needed:
        logger.info("\n✅ No retraining needed. All platforms stable.")
        return True
    
    # Retrain models
    logger.info("\n" + "=" * 60)
    logger.info("Retraining models...")
    logger.info("=" * 60)
    
    success = train_all_models(min_samples=50)  # Lower threshold for retraining
    
    if success:
        # Mark platforms as retrained
        for platform, result in monitoring_results.items():
            if result.get("retraining_needed"):
                algorithm_monitor.mark_retrained(platform)
        
        logger.info("\n✅ Models retrained successfully!")
        return True
    else:
        logger.error("\n❌ Model retraining failed")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-retrain VCOS models")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force retraining even if not needed"
    )
    
    args = parser.parse_args()
    
    if args.force:
        logger.info("Force retraining enabled")
        success = train_all_models(min_samples=50)
    else:
        success = auto_retrain()
    
    sys.exit(0 if success else 1)
