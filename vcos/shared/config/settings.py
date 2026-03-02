"""
VCOS Configuration Settings
"""

import os
from typing import List

class Settings:
    """Application settings"""
    
    # API Configuration
    API_KEY = os.getenv("VCOS_API_KEY", "internal-secret-change-in-production")
    API_PORT = int(os.getenv("VCOS_API_PORT", "8000"))
    
    # Data Directories
    DATA_ROOT = os.getenv("VCOS_DATA_ROOT", "data")
    RAW_VIDEOS_DIR = os.path.join(DATA_ROOT, "raw")
    OPTIMIZED_VIDEOS_DIR = os.path.join(DATA_ROOT, "optimized")
    VARIANTS_DIR = os.path.join(DATA_ROOT, "variants")
    ANALYTICS_DIR = os.path.join(DATA_ROOT, "analytics")
    TRAINING_DIR = os.path.join(DATA_ROOT, "training")
    
    # Database
    DATABASE_URL = os.getenv("VCOS_DATABASE_URL", "sqlite:///vcos.db")
    
    # Retention Optimizer Settings
    SILENCE_THRESHOLD_MS = 150
    MIN_MOMENTUM_SCORE = 0.5
    DOPAMINE_STIMULUS_INTERVAL = 3.0  # seconds
    
    # Variant Generator Settings
    DEFAULT_VARIANT_COUNT = 20
    PLAYBACK_SPEED_MIN = 1.0
    PLAYBACK_SPEED_MAX = 1.12
    
    # Platform Settings
    SUPPORTED_PLATFORMS: List[str] = ["tiktok", "instagram", "youtube"]
    
    # Analytics Pull Frequency (seconds)
    ANALYTICS_PULL_15MIN = 900
    ANALYTICS_PULL_1HR = 3600
    ANALYTICS_PULL_24HR = 86400

settings = Settings()
