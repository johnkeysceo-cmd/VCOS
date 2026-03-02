#!/usr/bin/env python3
"""
VCOS Startup Script
Starts the entire VCOS system
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gateway.api_server import app
from services.recording_service.screenarc_wrapper import screenarc_wrapper
from shared.logging.logger import setup_logging
import uvicorn

def check_dependencies():
    """Check all system dependencies"""
    print("=" * 60)
    print("VCOS System Check")
    print("=" * 60)
    
    issues = []
    
    # Check Python dependencies
    try:
        import fastapi
        print("✅ FastAPI")
    except ImportError:
        print("❌ FastAPI - Install with: pip install fastapi uvicorn")
        issues.append("fastapi")
    
    try:
        import librosa
        print("✅ librosa (audio processing)")
    except ImportError:
        print("⚠️  librosa - Install with: pip install librosa")
    
    try:
        import cv2
        print("✅ OpenCV (video processing)")
    except ImportError:
        print("⚠️  opencv-python - Install with: pip install opencv-python")
    
    try:
        import sklearn
        print("✅ scikit-learn (ML models)")
    except ImportError:
        print("⚠️  scikit-learn - Install with: pip install scikit-learn")
        issues.append("scikit-learn")
    
    # Check ScreenArc
    print("\nScreenArc Status:")
    screenarc_status = screenarc_wrapper.check_screenarc_setup()
    
    if screenarc_status["screenarc_exists"]:
        print("✅ ScreenArc directory exists")
    else:
        print("❌ ScreenArc directory not found")
        issues.append("screenarc")
    
    if screenarc_status["node_available"]:
        print("✅ Node.js available")
    else:
        print("❌ Node.js not found - Install Node.js")
        issues.append("nodejs")
    
    if screenarc_status["dependencies_installed"]:
        print("✅ ScreenArc dependencies installed")
    else:
        print("⚠️  ScreenArc dependencies not installed")
        print("   Run: cd generation_content/screenarc && npm install")
    
    if screenarc_status["ready"]:
        print("✅ ScreenArc ready")
    else:
        print("⚠️  ScreenArc not fully ready")
    
    # Check data directories
    print("\nData Directories:")
    from shared.config.settings import settings
    
    for dir_name, dir_path in [
        ("Raw Videos", settings.RAW_VIDEOS_DIR),
        ("Optimized", settings.OPTIMIZED_VIDEOS_DIR),
        ("Variants", settings.VARIANTS_DIR),
        ("Analytics", settings.ANALYTICS_DIR)
    ]:
        if os.path.exists(dir_path):
            print(f"✅ {dir_name}: {dir_path}")
        else:
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ {dir_name}: Created {dir_path}")
    
    # Check databases
    print("\nDatabases:")
    from services.topic_engine.topic_db import init_db
    from services.hook_engine.hook_db import init_db
    from services.analytics_ingestion.analytics_db import init_db
    
    print("✅ Databases initialized")
    
    print("\n" + "=" * 60)
    
    if issues:
        print(f"⚠️  Issues found: {', '.join(issues)}")
        print("Install missing dependencies before starting.")
        return False
    else:
        print("✅ All checks passed!")
        return True

def start_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server"""
    print(f"\n🚀 Starting VCOS API Server on http://{host}:{port}")
    print("Press Ctrl+C to stop\n")
    
    setup_logging()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

def main():
    parser = argparse.ArgumentParser(description="Start VCOS System")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check dependencies, don't start server"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip dependency checks"
    )
    
    args = parser.parse_args()
    
    if not args.skip_checks:
        if not check_dependencies():
            if not args.check_only:
                sys.exit(1)
            else:
                sys.exit(0)
    
    if args.check_only:
        print("\n✅ System check complete")
        return
    
    # Start server
    try:
        start_api_server(args.host, args.port)
    except KeyboardInterrupt:
        print("\n\n👋 VCOS stopped")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
