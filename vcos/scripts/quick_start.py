#!/usr/bin/env python3
"""
VCOS Quick Start - Complete Setup and Start
"""

import sys
import subprocess
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    print("=" * 60)
    print("VCOS Quick Start")
    print("=" * 60)
    print()
    
    # Step 1: Check dependencies
    print("[1/4] Checking dependencies...")
    result = subprocess.run(
        [sys.executable, "scripts/start_vcos.py", "--check-only"],
        cwd=Path(__file__).parent.parent
    )
    
    if result.returncode != 0:
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        print("Run: pip install -r requirements.txt")
        return 1
    
    # Step 2: Setup ScreenArc
    print("\n[2/4] Setting up ScreenArc...")
    result = subprocess.run(
        [sys.executable, "scripts/setup_screenarc.py"],
        cwd=Path(__file__).parent.parent
    )
    
    if result.returncode != 0:
        print("\n⚠️  ScreenArc setup had issues, but continuing...")
    
    # Step 3: Initialize databases
    print("\n[3/4] Initializing databases...")
    try:
        from services.topic_engine.topic_db import init_db
        from services.hook_engine.hook_db import init_db
        from services.analytics_ingestion.analytics_db import init_db
        print("✅ Databases initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    # Step 4: Start server
    print("\n[4/4] Starting VCOS API Server...")
    print("=" * 60)
    print("VCOS is starting on http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    from scripts.start_vcos import start_api_server
    start_api_server()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 VCOS stopped")
        sys.exit(0)
