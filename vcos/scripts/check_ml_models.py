#!/usr/bin/env python3
"""
Check ML Models Status
Shows which models are trained and available
"""

import sys
import os
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_models():
    """Check ML model status"""
    print("=" * 60)
    print("VCOS ML Models Status")
    print("=" * 60)
    print()
    
    models_dir = Path(__file__).parent.parent / "models"
    
    models = {
        "Hook CTR Model": "hook_ctr_model.pkl",
        "Retention Forecast Model": "retention_forecast_model.pkl",
        "Viral Prediction Model": "viral_prediction_model.pkl",
        "Q-Table (RL)": "q_table.json"
    }
    
    all_trained = True
    
    for model_name, filename in models.items():
        model_path = models_dir / filename
        if model_path.exists():
            size = model_path.stat().st_size / 1024  # KB
            print(f"✅ {model_name}: {size:.1f} KB")
        else:
            print(f"❌ {model_name}: Not trained")
            all_trained = False
    
    print()
    
    if all_trained:
        print("✅ All models are trained and ready!")
    else:
        print("⚠️  Some models are missing.")
        print("\nTo train models:")
        print("1. Collect training data: python scripts/collect_training_data.py")
        print("2. Train models: python scripts/train_models.py")
        print("3. Train RL agent: python scripts/run_rl_training.py")
    
    print("=" * 60)

if __name__ == "__main__":
    check_models()
