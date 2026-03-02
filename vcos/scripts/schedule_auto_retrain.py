#!/usr/bin/env python3
"""
VCOS Schedule Auto Retrain
Schedules automatic model retraining based on algorithm monitoring
"""

import sys
import time
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.auto_retrain_models import auto_retrain
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def schedule_retraining(interval_hours: int = 24):
    """
    Schedule automatic retraining
    
    Args:
        interval_hours: Hours between retraining checks
    """
    logger.info(f"Scheduling auto-retrain every {interval_hours} hours")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            logger.info("\n" + "=" * 60)
            logger.info(f"Running scheduled retraining check...")
            logger.info("=" * 60)
            
            auto_retrain()
            
            logger.info(f"\nNext check in {interval_hours} hours...")
            time.sleep(interval_hours * 3600)
            
    except KeyboardInterrupt:
        logger.info("\n\n👋 Auto-retrain scheduler stopped")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Schedule VCOS auto-retrain")
    parser.add_argument(
        "--interval",
        type=int,
        default=24,
        help="Hours between retraining checks (default: 24)"
    )
    
    args = parser.parse_args()
    
    schedule_retraining(args.interval)
