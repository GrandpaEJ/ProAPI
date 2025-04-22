"""
Safe fallback for blocking routes in ProAPI.

This module provides automatic detection and handling of blocking routes,
with fallback to synchronous mode for blocking operations.
"""

import asyncio
import functools
import inspect
import time
import threading
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, Set

from .logging import app_logger
from .scheduler import run_in_thread, run_in_process, is_cpu_bound

# Type variable for generic function
T = TypeVar('T')

# Default settings
DEFAULT_BLOCKING_THRESHOLD = 0.1  # seconds
DEFAULT_MAX_SAMPLES = 5
DEFAULT_AUTO_OFFLOAD = True

# Track blocking routes
_blocking_routes: Dict[str, Dict[str, Any]] = {}
_route_execution_times: Dict[str, List[float]] = {}
_lock = threading.RLock()

def detect_blocking_route(route_id: str, 
                         func: Callable,
                         execution_time: float,
                         threshold: float = DEFAULT_BLOCKING_THRESHOLD,
                         max_samples: int = DEFAULT_MAX_SAMPLES) -> bool:
    """
    Detect if a route is blocking based on execution time.
    
    Args:
        route_id: Route identifier
        func: Route handler function
        execution_time: Execution time in seconds
        threshold: Threshold in seconds for considering a route blocking
        max_samples: Maximum number of samples to consider
        
    Returns:
        True if the route is blocking, False otherwise
    """
    with _lock:
        # Initialize execution times for this route
        if route_id not in _route_execution_times:
            _route_execution_times[route_id] = []
        
        # Add execution time
        _route_execution_times[route_id].append(execution_time)
        
        # Keep only the last max_samples
        if len(_route_execution_times[route_id]) > max_samples:
            _route_execution_times[route_id] = _route_execution_times[route_id][-max_samples:]
        
        # Check if we have enough samples
        if len(_route_execution_times[route_id]) < max_samples:
            return False
        
        # Calculate average execution time
        avg_time = sum(_route_execution_times[route_id]) / len(_route_execution_times[route_id])
        
        # Check if the route is blocking
        is_blocking = avg_time > threshold
        
        if is_blocking and route_id not in _blocking_routes:
            # Mark the route as blocking
            _blocking_routes[route_id] = {
                "func": func,
                "avg_time": avg_time,
                "samples": len(_route_execution_times[route_id]),
                "cpu_bound": is_cpu_bound(func),
                "detected_at": time.time()
            }
            
            app_logger.warning(f"Detected blocking route: {route_id} "
                              f"(avg time: {avg_time:.2f}s, CPU-bound: {is_cpu_bound(func)})")
        
        return is_blocking

def handle_blocking_route(route_id: str, 
                         func: Callable[..., T],
                         auto_offload: bool = DEFAULT_AUTO_OFFLOAD) -> Callable[..., T]:
    """
    Handle a blocking route by offloading it to a thread or process pool.
    
    Args:
        route_id: Route identifier
        func: Route handler function
        auto_offload: Whether to automatically offload the route
        
    Returns:
        Wrapped function that handles blocking
    """
    # Check if the route is already known to be blocking
    if route_id in _blocking_routes and auto_offload:
        # Get route info
        route_info = _blocking_routes[route_id]
        
        # Offload to the appropriate executor
        if route_info["cpu_bound"]:
            app_logger.info(f"Offloading CPU-bound route {route_id} to process pool")
            return run_in_process(func)
        else:
            app_logger.info(f"Offloading I/O-bound route {route_id} to thread pool")
            return run_in_thread(func)
    
    # Return the original function
    return func

def with_blocking_detection(threshold: float = DEFAULT_BLOCKING_THRESHOLD,
                           max_samples: int = DEFAULT_MAX_SAMPLES,
                           auto_offload: bool = DEFAULT_AUTO_OFFLOAD) -> Callable:
    """
    Decorator to detect and handle blocking routes.
    
    Args:
        threshold: Threshold in seconds for considering a route blocking
        max_samples: Maximum number of samples to consider
        auto_offload: Whether to automatically offload blocking routes
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Generate a unique route ID
        route_id = f"{func.__module__}.{func.__qualname__}"
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check if the route is already known to be blocking
            wrapped_func = handle_blocking_route(route_id, func, auto_offload)
            
            # If the function is already async, we need to await it
            if inspect.iscoroutinefunction(wrapped_func):
                return await wrapped_func(*args, **kwargs)
            
            # Measure execution time
            start_time = time.time()
            
            try:
                # Execute the function
                result = wrapped_func(*args, **kwargs)
                return result
            finally:
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Detect if the route is blocking
                detect_blocking_route(route_id, func, execution_time, threshold, max_samples)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check if the route is already known to be blocking
            wrapped_func = handle_blocking_route(route_id, func, auto_offload)
            
            # If the function is async, we need to run it in the event loop
            if inspect.iscoroutinefunction(wrapped_func):
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(wrapped_func(*args, **kwargs))
            
            # Measure execution time
            start_time = time.time()
            
            try:
                # Execute the function
                result = wrapped_func(*args, **kwargs)
                return result
            finally:
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Detect if the route is blocking
                detect_blocking_route(route_id, func, execution_time, threshold, max_samples)
        
        # Return the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def get_blocking_routes() -> Dict[str, Dict[str, Any]]:
    """
    Get information about detected blocking routes.
    
    Returns:
        Dictionary with information about blocking routes
    """
    with _lock:
        return dict(_blocking_routes)

def clear_blocking_routes() -> None:
    """Clear information about detected blocking routes."""
    with _lock:
        _blocking_routes.clear()
        _route_execution_times.clear()

def configure_blocking_detection(threshold: float = DEFAULT_BLOCKING_THRESHOLD,
                               max_samples: int = DEFAULT_MAX_SAMPLES,
                               auto_offload: bool = DEFAULT_AUTO_OFFLOAD) -> None:
    """
    Configure blocking route detection.
    
    Args:
        threshold: Threshold in seconds for considering a route blocking
        max_samples: Maximum number of samples to consider
        auto_offload: Whether to automatically offload blocking routes
    """
    global DEFAULT_BLOCKING_THRESHOLD, DEFAULT_MAX_SAMPLES, DEFAULT_AUTO_OFFLOAD
    
    DEFAULT_BLOCKING_THRESHOLD = threshold
    DEFAULT_MAX_SAMPLES = max_samples
    DEFAULT_AUTO_OFFLOAD = auto_offload
    
    app_logger.info(f"Configured blocking detection with threshold={threshold}s, "
                   f"max_samples={max_samples}, auto_offload={auto_offload}")

# Decorator for safe fallback to sync mode
def safe_sync_fallback(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to safely fall back to synchronous mode for blocking routes.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    # Generate a unique route ID
    route_id = f"{func.__module__}.{func.__qualname__}"
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            # Try to run the function asynchronously
            return await func(*args, **kwargs)
        except Exception as e:
            # Log the error
            app_logger.exception(f"Error in async route {route_id}: {e}")
            app_logger.warning(f"Falling back to synchronous mode for route {route_id}")
            
            # Fall back to synchronous mode
            sync_func = run_in_thread(func)
            return await sync_func(*args, **kwargs)
    
    # Only wrap async functions
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return func
