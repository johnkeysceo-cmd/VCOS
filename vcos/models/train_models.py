"""
ML Models - Model Training Script
Main script to train all ML models
"""

import os
import sys
import argparse
import logging
from models.training_data_collector import training_data_collector
from models.training_pipeline import (
    train_hook_ctr_model,
    train_retention_forecast_model
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_all_models(min_samples: int = 100, validate_quality: bool = True):
    """
    Train all ML models
    
    Args:
        min_samples: Minimum number of training samples required
    """
    logger.info("=" * 60)
    logger.info("VCOS Model Training Pipeline")
    logger.info("=" * 60)
    
    # 1. Collect training data
    logger.info("\n[1/4] Collecting training data...")
    
    hook_features, hook_labels = training_data_collector.collect_hook_training_data(min_samples)
    retention_features, retention_labels = training_data_collector.collect_retention_training_data(min_samples)
    viral_features, viral_labels = training_data_collector.collect_viral_training_data(min_samples)
    
    if not hook_features or not retention_features:
        logger.error(f"Insufficient training data. Need at least {min_samples} samples.")
        logger.error(f"Found: Hook={len(hook_features)}, Retention={len(retention_features)}")
        logger.error("\nTo collect data:")
        logger.error("1. Run the system and create content batches")
        logger.error("2. Wait for analytics to be collected")
        logger.error("3. Re-run training")
        return False
    
    # 2. Validate data quality
    if validate_quality:
        logger.info("\n[2/4] Validating training data quality...")
        from models.training_data_quality import training_data_validator
        
        hook_validation = training_data_validator.validate_training_data(hook_features, hook_labels)
        retention_validation = training_data_validator.validate_training_data(retention_features, retention_labels)
        
        logger.info(f"Hook data quality: {hook_validation['quality_score']:.2f}")
        if hook_validation.get("recommendations"):
            for rec in hook_validation["recommendations"]:
                logger.info(f"  - {rec}")
        
        logger.info(f"Retention data quality: {retention_validation['quality_score']:.2f}")
        if retention_validation.get("recommendations"):
            for rec in retention_validation["recommendations"]:
                logger.info(f"  - {rec}")
        
        if not hook_validation.get("valid") or not retention_validation.get("valid"):
            logger.warning("⚠️  Data quality issues detected. Training may produce poor models.")
            logger.warning("Consider collecting more diverse data before training.")
    
    # 3. Train hook CTR model
    logger.info("\n[3/4] Training Hook CTR Model...")
    hook_result = train_hook_ctr_model(hook_features, hook_labels, model_type="gradient_boosting")
    
    if hook_result.get("success"):
        logger.info(f"✅ Hook CTR Model: R²={hook_result['test_score']:.3f}, MSE={hook_result['mse']:.4f}")
    else:
        logger.error(f"❌ Hook CTR Model failed: {hook_result.get('error')}")
    
    # 4. Train retention forecast model
    logger.info("\n[4/4] Training Retention Forecast Model...")
    retention_result = train_retention_forecast_model(
        retention_features,
        retention_labels,
        model_type="gradient_boosting"
    )
    
    if retention_result.get("success"):
        logger.info(f"✅ Retention Model: R²={retention_result['test_score']:.3f}, MSE={retention_result['mse']:.4f}")
    else:
        logger.error(f"❌ Retention Model failed: {retention_result.get('error')}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Training Summary")
    logger.info("=" * 60)
    logger.info(f"Hook CTR Model: {'✅ Trained' if hook_result.get('success') else '❌ Failed'}")
    logger.info(f"Retention Model: {'✅ Trained' if retention_result.get('success') else '❌ Failed'}")
    
    if hook_result.get("success") and retention_result.get("success"):
        logger.info("\n✅ All models trained successfully!")
        logger.info("Models are now available for predictions.")
        return True
    else:
        logger.warning("\n⚠️ Some models failed to train. Check errors above.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Train VCOS ML models")
    parser.add_argument(
        "--min-samples",
        type=int,
        default=100,
        help="Minimum number of training samples required (default: 100)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force training even with fewer samples"
    )
    
    args = parser.parse_args()
    
    if args.force:
        args.min_samples = 10  # Lower threshold
    
    success = train_all_models(args.min_samples)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
