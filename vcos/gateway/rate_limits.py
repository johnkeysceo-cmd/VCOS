"""
VCOS Gateway - Rate limiting
Prevents abuse and manages request throttling
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Simple in-memory rate limiter
    In production, use Redis or similar for distributed systems
    """
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.default_limit = 100  # requests per window
        self.window_seconds = 60  # 1 minute window
    
    def is_allowed(self, identifier: str, limit: int = None) -> bool:
        """
        Check if request is allowed
        
        Args:
            identifier: Client identifier (IP, API key, etc.)
            limit: Optional custom limit
            
        Returns:
            True if request is allowed
        """
        limit = limit or self.default_limit
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= limit:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Record request
        self.requests[identifier].append(now)
        return True
    
    def reset(self, identifier: str):
        """Reset rate limit for an identifier"""
        if identifier in self.requests:
            del self.requests[identifier]
