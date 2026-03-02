#!/usr/bin/env python3
"""
ScreenArc Setup Script
Sets up ScreenArc dependencies and verifies installation
"""

import sys
import subprocess
from pathlib import Path

# Add vcos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recording_service.screenarc_wrapper import screenarc_wrapper

def setup_screenarc():
    """Setup ScreenArc dependencies"""
    print("=" * 60)
    print("ScreenArc Setup")
    print("=" * 60)
    
    status = screenarc_wrapper.check_screenarc_setup()
    
    if not status["screenarc_exists"]:
        print("❌ ScreenArc directory not found at generation_content/screenarc")
        print("   Ensure ScreenArc is in the correct location.")
        return False
    
    if not status["node_available"]:
        print("❌ Node.js not found")
        print("   Install Node.js from https://nodejs.org/")
        return False
    
    if not status["dependencies_installed"]:
        print("\n📦 Installing ScreenArc dependencies...")
        print("   This may take a few minutes...\n")
        
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(screenarc_wrapper.screenarc_root),
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print("\n✅ ScreenArc dependencies installed successfully!")
            else:
                print("\n❌ Failed to install dependencies")
                return False
        except Exception as e:
            print(f"\n❌ Error installing dependencies: {e}")
            return False
    else:
        print("✅ ScreenArc dependencies already installed")
    
    # Verify CLI
    if screenarc_wrapper.cli_path.exists():
        print("✅ ScreenArc CLI script found")
    else:
        print("⚠️  ScreenArc CLI script not found")
    
    print("\n" + "=" * 60)
    print("✅ ScreenArc setup complete!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = setup_screenarc()
    sys.exit(0 if success else 1)
