"""
Retry Utilities

Retry mechanisms for handling transient failures.
"""

import time
import random
from typing import Callable, TypeVar, Optional, List
from functools import wraps

T = TypeVar('T')


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    jitter: bool = True
):
    """
    Decorator to retry a function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch and retry
        jitter: Whether to add random jitter to delay
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        # Calculate delay with optional jitter
                        actual_delay = current_delay
                        if jitter:
                            actual_delay += random.uniform(0, current_delay * 0.1)
                        
                        time.sleep(actual_delay)
                        current_delay *= backoff
                    else:
                        raise
            
            # Should never reach here, but type checker needs it
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry failed unexpectedly")
        
        return wrapper
    return decorator

