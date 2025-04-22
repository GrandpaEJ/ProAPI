"""
Event loop protection for ProAPI.

This module provides protection against event loop blocking by monitoring
the event loop and offloading blocking operations to thread or process pools.
"""

import asyncio
import functools
import inspect
import time
import threading
import warnings
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar

from .logging import app_logger
from .scheduler import run_in_thread, run_in_process, is_cpu_bound

# Type variable for generic function
T = TypeVar('T')

# Default settings
DEFAULT_SLOW_CALLBACK_DURATION = 0.1  # seconds
DEFAULT_MONITOR_INTERVAL = 0.5  # seconds
DEFAULT_WARNING_THRESHOLD = 0.2  # seconds
DEFAULT_CRITICAL_THRESHOLD = 1.0  # seconds

class EventLoopMonitor:
    """
    Monitor the event loop for blocking operations.
    
    This class monitors the event loop and logs warnings when callbacks
    take too long to execute, potentially blocking the event loop.
    """
    
    def __init__(self, 
                 warning_threshold: float = DEFAULT_WARNING_THRESHOLD,
                 critical_threshold: float = DEFAULT_CRITICAL_THRESHOLD,
                 monitor_interval: float = DEFAULT_MONITOR_INTERVAL):
        """
        Initialize the event loop monitor.
        
        Args:
            warning_threshold: Threshold in seconds for warning about slow callbacks
            critical_threshold: Threshold in seconds for critical warnings about slow callbacks
            monitor_interval: Interval in seconds for checking the event loop
        """
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.monitor_interval = monitor_interval
        
        self._monitoring = False
        self._monitor_thread = None
        self._loop = None
        
        # Statistics
        self.slow_callbacks = 0
        self.critical_callbacks = 0
        self.last_slow_callback_time = 0
        self.max_callback_duration = 0
    
    def start(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """
        Start monitoring the event loop.
        
        Args:
            loop: Event loop to monitor (default: current event loop)
        """
        if self._monitoring:
            return
        
        self._loop = loop or asyncio.get_event_loop()
        self._monitoring = True
        
        # Start the monitor thread
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="ProAPI-EventLoopMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        
        app_logger.debug(f"Started event loop monitor with warning threshold {self.warning_threshold}s "
                        f"and critical threshold {self.critical_threshold}s")
    
    def stop(self) -> None:
        """Stop monitoring the event loop."""
        if not self._monitoring:
            return
        
        self._monitoring = False
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
        
        self._monitor_thread = None
        self._loop = None
        
        app_logger.debug("Stopped event loop monitor")
    
    def _monitor_loop(self) -> None:
        """Monitor the event loop for blocking operations."""
        while self._monitoring:
            try:
                # Schedule a callback to check the time
                start_time = time.time()
                future = asyncio.run_coroutine_threadsafe(self._check_time(start_time), self._loop)
                
                # Wait for the callback to complete
                future.result(timeout=max(self.critical_threshold * 2, 2.0))
            except (asyncio.CancelledError, concurrent.futures.TimeoutError):
                # The callback was cancelled or timed out
                duration = time.time() - start_time
                
                if duration > self.critical_threshold:
                    self.critical_callbacks += 1
                    app_logger.warning(f"Event loop blocked for {duration:.2f}s - this is a critical issue "
                                      f"that may cause performance problems")
                    
                    # Suggest solutions
                    app_logger.warning("Consider using @auto_task, @thread_task, or @process_task decorators "
                                      "to offload blocking operations")
                elif duration > self.warning_threshold:
                    self.slow_callbacks += 1
                    app_logger.info(f"Event loop blocked for {duration:.2f}s - this may cause performance issues")
                
                self.last_slow_callback_time = time.time()
                self.max_callback_duration = max(self.max_callback_duration, duration)
            except Exception as e:
                app_logger.exception(f"Error in event loop monitor: {e}")
            
            # Sleep before checking again
            time.sleep(self.monitor_interval)
    
    async def _check_time(self, start_time: float) -> None:
        """
        Check the time it takes to schedule and run a callback.
        
        Args:
            start_time: Start time in seconds
        """
        duration = time.time() - start_time
        
        if duration > self.critical_threshold:
            self.critical_callbacks += 1
            app_logger.warning(f"Event loop delayed callback for {duration:.2f}s - this is a critical issue "
                              f"that may cause performance problems")
        elif duration > self.warning_threshold:
            self.slow_callbacks += 1
            app_logger.info(f"Event loop delayed callback for {duration:.2f}s - this may cause performance issues")
        
        if duration > self.warning_threshold:
            self.last_slow_callback_time = time.time()
            self.max_callback_duration = max(self.max_callback_duration, duration)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get monitoring statistics.
        
        Returns:
            Dictionary with monitoring statistics
        """
        return {
            "slow_callbacks": self.slow_callbacks,
            "critical_callbacks": self.critical_callbacks,
            "last_slow_callback_time": self.last_slow_callback_time,
            "max_callback_duration": self.max_callback_duration,
            "warning_threshold": self.warning_threshold,
            "critical_threshold": self.critical_threshold,
            "monitor_interval": self.monitor_interval,
            "monitoring": self._monitoring
        }

# Create a default event loop monitor
default_monitor = EventLoopMonitor()

def protect_loop(warning_threshold: float = DEFAULT_WARNING_THRESHOLD,
                critical_threshold: float = DEFAULT_CRITICAL_THRESHOLD) -> Callable:
    """
    Decorator to protect the event loop from blocking operations.
    
    This decorator monitors the execution time of the decorated function
    and offloads it to a thread or process pool if it takes too long.
    
    Args:
        warning_threshold: Threshold in seconds for warning about slow callbacks
        critical_threshold: Threshold in seconds for critical warnings about slow callbacks
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Skip if the function is already async
        if inspect.iscoroutinefunction(func):
            return func
        
        # Track execution times
        execution_times = []
        max_samples = 5
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if we have enough samples to make a decision
            if len(execution_times) >= max_samples:
                avg_time = sum(execution_times) / len(execution_times)
                
                # If the average execution time is above the critical threshold,
                # offload to a thread or process pool
                if avg_time > critical_threshold:
                    # Determine if the function is CPU-bound
                    if is_cpu_bound(func):
                        app_logger.warning(f"Function {func.__name__} is blocking the event loop "
                                          f"(avg time: {avg_time:.2f}s) - offloading to process pool")
                        return await run_in_process(func)(*args, **kwargs)
                    else:
                        app_logger.warning(f"Function {func.__name__} is blocking the event loop "
                                          f"(avg time: {avg_time:.2f}s) - offloading to thread pool")
                        return await run_in_thread(func)(*args, **kwargs)
                
                # If the average execution time is above the warning threshold,
                # log a warning but continue executing normally
                elif avg_time > warning_threshold:
                    app_logger.info(f"Function {func.__name__} may be blocking the event loop "
                                   f"(avg time: {avg_time:.2f}s) - consider using @thread_task or @process_task")
            
            # Execute the function and measure the time
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Update execution times
            execution_times.append(duration)
            if len(execution_times) > max_samples:
                execution_times.pop(0)
            
            # Log warnings for slow executions
            if duration > critical_threshold:
                app_logger.warning(f"Function {func.__name__} blocked the event loop for {duration:.2f}s - "
                                  f"this is a critical issue that may cause performance problems")
            elif duration > warning_threshold:
                app_logger.info(f"Function {func.__name__} blocked the event loop for {duration:.2f}s - "
                               f"this may cause performance issues")
            
            return result
        
        return wrapper
    
    return decorator

def start_loop_monitoring(loop: Optional[asyncio.AbstractEventLoop] = None,
                         warning_threshold: float = DEFAULT_WARNING_THRESHOLD,
                         critical_threshold: float = DEFAULT_CRITICAL_THRESHOLD,
                         monitor_interval: float = DEFAULT_MONITOR_INTERVAL) -> None:
    """
    Start monitoring the event loop for blocking operations.
    
    Args:
        loop: Event loop to monitor (default: current event loop)
        warning_threshold: Threshold in seconds for warning about slow callbacks
        critical_threshold: Threshold in seconds for critical warnings about slow callbacks
        monitor_interval: Interval in seconds for checking the event loop
    """
    global default_monitor
    
    # Create a new monitor with the specified settings
    default_monitor = EventLoopMonitor(
        warning_threshold=warning_threshold,
        critical_threshold=critical_threshold,
        monitor_interval=monitor_interval
    )
    
    # Start monitoring
    default_monitor.start(loop)

def stop_loop_monitoring() -> None:
    """Stop monitoring the event loop for blocking operations."""
    global default_monitor
    
    if default_monitor:
        default_monitor.stop()

def get_loop_stats() -> Dict[str, Any]:
    """
    Get event loop monitoring statistics.
    
    Returns:
        Dictionary with monitoring statistics
    """
    global default_monitor
    
    if default_monitor:
        return default_monitor.get_stats()
    else:
        return {
            "monitoring": False
        }

# Set up slow callback logging for asyncio
asyncio.get_event_loop().slow_callback_duration = DEFAULT_SLOW_CALLBACK_DURATION
