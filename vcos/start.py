#!/usr/bin/env python3
"""
VCOS Quick Start
Simple startup script
"""

import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(Path(__file__).parent))

from scripts.start_vcos import main

if __name__ == "__main__":
    main()
