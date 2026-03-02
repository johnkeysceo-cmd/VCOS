"""
Recording Service - Error Handler
Enhanced error handling for recording operations
"""

import logging
import subprocess
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

def handle_recording_errors(func: Callable) -> Callable:
    """
    Decorator for handling recording service errors
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"File not found in {func.__name__}: {e}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Subprocess error in {func.__name__}: {e.stderr if hasattr(e, 'stderr') else str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"File not found in {func.__name__}: {e}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Subprocess error in {func.__name__}: {e.stderr if hasattr(e, 'stderr') else str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise
    
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
