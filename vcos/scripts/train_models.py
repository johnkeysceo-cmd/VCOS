#!/usr/bin/env python3
"""
VCOS Model Training Script
Trains all ML models from analytics data
"""

import sys
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.train_models import train_all_models
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train VCOS ML models")
    parser.add_argument(
        "--min-samples",
        type=int,
        default=100,
        help="Minimum training samples (default: 100)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force training with fewer samples"
    )
    
    args = parser.parse_args()
    
    success = train_all_models(args.min_samples if not args.force else 10)
    sys.exit(0 if success else 1)
