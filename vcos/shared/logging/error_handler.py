"""
Shared Error Handler
Centralized error handling utilities
"""

import logging
import traceback
from typing import Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)

def log_error_with_context(func: Callable) -> Callable:
    """
    Decorator to log errors with full context
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error in {func.__name__}:\n"
                f"Args: {args}\n"
                f"Kwargs: {kwargs}\n"
                f"Error: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error in {func.__name__}:\n"
                f"Args: {args}\n"
                f"Kwargs: {kwargs}\n"
                f"Error: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise
    
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
