"""
Shared logging configuration
"""

import logging
import sys

def setup_logging(level=logging.INFO):
    """Setup application-wide logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
