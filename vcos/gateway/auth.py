"""
VCOS Gateway - API authentication
Handles API tokens and authentication
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# In production, this should be loaded from environment or secure storage
INTERNAL_SECRET = os.getenv("VCOS_API_KEY", "internal-secret-change-in-production")

def validate_api_key(key: str) -> bool:
    """
    Validate API key
    
    Args:
        key: API key to validate
        
    Returns:
        True if valid
        
    Raises:
        Exception: If key is invalid
    """
    if not key:
        raise Exception("API key is required")
    
    if key != INTERNAL_SECRET:
        logger.warning(f"Invalid API key attempt: {key[:5]}...")
        raise Exception("Unauthorized: Invalid API key")
    
    return True

def get_api_key_from_header(header_value: Optional[str]) -> Optional[str]:
    """Extract API key from header value"""
    if not header_value:
        return None
    
    # Handle "Bearer <token>" format
    if header_value.startswith("Bearer "):
        return header_value[7:]
    
    return header_value
