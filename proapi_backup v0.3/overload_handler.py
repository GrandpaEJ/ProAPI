"""
Graceful overload handler for ProAPI.

This module provides a request queue with backpressure to handle server overload
gracefully, preventing crashes and ensuring consistent performance under heavy load.
"""

import asyncio
import functools
import time
import threading
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, Deque

from .logging import app_logger

# Type variable for generic function
T = TypeVar('T')

# Default settings
DEFAULT_MAX_QUEUE_SIZE = 1000
DEFAULT_MAX_CONCURRENT_REQUESTS = 100
DEFAULT_REQUEST_TIMEOUT = 30.0  # seconds
DEFAULT_BACKPRESSURE_THRESHOLD = 0.8  # 80% of max queue size
DEFAULT_CIRCUIT_BREAKER_THRESHOLD = 0.95  # 95% of max queue size
DEFAULT_CIRCUIT_BREAKER_RESET_TIME = 5.0  # seconds

class RequestQueue:
    """
    Request queue with backpressure for handling server overload.
    
    This class provides a queue for handling requests with backpressure
    to prevent server overload and ensure consistent performance.
    """
    
    def __init__(self, 
                 max_size: int = DEFAULT_MAX_QUEUE_SIZE,
                 max_concurrent: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
                 request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
                 backpressure_threshold: float = DEFAULT_BACKPRESSURE_THRESHOLD,
                 circuit_breaker_threshold: float = DEFAULT_CIRCUIT_BREAKER_THRESHOLD,
                 circuit_breaker_reset_time: float = DEFAULT_CIRCUIT_BREAKER_RESET_TIME):
        """
        Initialize the request queue.
        
        Args:
            max_size: Maximum queue size
            max_concurrent: Maximum number of concurrent requests
            request_timeout: Request timeout in seconds
            backpressure_threshold: Threshold for applying backpressure (0.0-1.0)
            circuit_breaker_threshold: Threshold for tripping the circuit breaker (0.0-1.0)
            circuit_breaker_reset_time: Time in seconds before resetting the circuit breaker
        """
        self.max_size = max_size
        self.max_concurrent = max_concurrent
        self.request_timeout = request_timeout
        self.backpressure_threshold = backpressure_threshold
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_reset_time = circuit_breaker_reset_time
        
        # Queue and semaphore
        self.queue: Deque = deque()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Circuit breaker state
        self.circuit_open = False
        self.circuit_open_time = 0
        
        # Statistics
        self.total_requests = 0
        self.completed_requests = 0
        self.rejected_requests = 0
        self.timed_out_requests = 0
        self.current_load = 0.0
        self.peak_load = 0.0
        self.peak_queue_size = 0
        self.peak_concurrent_requests = 0
    
    async def add_request(self, handler: Callable, *args, **kwargs) -> Any:
        """
        Add a request to the queue and process it.
        
        Args:
            handler: Request handler function
            *args: Positional arguments for the handler
            **kwargs: Keyword arguments for the handler
            
        Returns:
            Handler result
            
        Raises:
            asyncio.TimeoutError: If the request times out
            RuntimeError: If the request is rejected due to overload
        """
        self.total_requests += 1
        
        # Check if the circuit breaker is open
        if self.circuit_open:
            # Check if it's time to reset the circuit breaker
            if time.time() - self.circuit_open_time > self.circuit_breaker_reset_time:
                app_logger.info("Resetting circuit breaker")
                self.circuit_open = False
                self.circuit_open_time = 0
            else:
                # Reject the request
                self.rejected_requests += 1
                app_logger.warning("Request rejected: circuit breaker open")
                raise RuntimeError("Server overloaded: circuit breaker open")
        
        # Check if the queue is full
        if len(self.queue) >= self.max_size:
            # Reject the request
            self.rejected_requests += 1
            app_logger.warning("Request rejected: queue full")
            raise RuntimeError("Server overloaded: queue full")
        
        # Check if we should apply backpressure
        queue_load = len(self.queue) / self.max_size
        self.current_load = queue_load
        self.peak_load = max(self.peak_load, queue_load)
        self.peak_queue_size = max(self.peak_queue_size, len(self.queue))
        
        if queue_load >= self.circuit_breaker_threshold:
            # Trip the circuit breaker
            app_logger.warning(f"Circuit breaker tripped: queue load {queue_load:.2f}")
            self.circuit_open = True
            self.circuit_open_time = time.time()
            
            # Reject the request
            self.rejected_requests += 1
            raise RuntimeError("Server overloaded: circuit breaker tripped")
        
        if queue_load >= self.backpressure_threshold:
            # Apply backpressure by adding a delay
            delay = (queue_load - self.backpressure_threshold) / (1.0 - self.backpressure_threshold)
            delay = min(delay * 0.5, 0.5)  # Max delay of 500ms
            
            app_logger.info(f"Applying backpressure: queue load {queue_load:.2f}, delay {delay:.2f}s")
            await asyncio.sleep(delay)
        
        # Create a future for the request result
        future = asyncio.get_event_loop().create_future()
        
        # Add the request to the queue
        self.queue.append((handler, args, kwargs, future, time.time()))
        
        # Process the queue
        asyncio.create_task(self._process_queue())
        
        # Wait for the result with timeout
        try:
            return await asyncio.wait_for(future, timeout=self.request_timeout)
        except asyncio.TimeoutError:
            self.timed_out_requests += 1
            app_logger.warning("Request timed out")
            raise
    
    async def _process_queue(self) -> None:
        """Process requests in the queue."""
        if not self.queue:
            return
        
        # Try to acquire the semaphore
        if not self.semaphore.locked() or self.semaphore._value > 0:
            async with self.semaphore:
                # Get the next request
                if not self.queue:
                    return
                
                handler, args, kwargs, future, start_time = self.queue.popleft()
                
                # Check if the request has already timed out
                if future.done():
                    return
                
                # Track concurrent requests
                concurrent_requests = self.max_concurrent - self.semaphore._value
                self.peak_concurrent_requests = max(self.peak_concurrent_requests, concurrent_requests)
                
                # Process the request
                try:
                    result = await handler(*args, **kwargs)
                    
                    # Set the result
                    if not future.done():
                        future.set_result(result)
                    
                    self.completed_requests += 1
                except Exception as e:
                    # Set the exception
                    if not future.done():
                        future.set_exception(e)
                    
                    app_logger.exception(f"Error processing request: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        return {
            "queue_size": len(self.queue),
            "max_size": self.max_size,
            "max_concurrent": self.max_concurrent,
            "current_load": self.current_load,
            "peak_load": self.peak_load,
            "peak_queue_size": self.peak_queue_size,
            "peak_concurrent_requests": self.peak_concurrent_requests,
            "total_requests": self.total_requests,
            "completed_requests": self.completed_requests,
            "rejected_requests": self.rejected_requests,
            "timed_out_requests": self.timed_out_requests,
            "circuit_open": self.circuit_open,
            "circuit_open_time": self.circuit_open_time
        }

# Create a default request queue
default_queue = RequestQueue()

def with_overload_protection(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to add overload protection to a request handler.
    
    Args:
        func: Request handler function
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await default_queue.add_request(func, *args, **kwargs)
    
    return wrapper

def configure_overload_handler(max_size: int = DEFAULT_MAX_QUEUE_SIZE,
                              max_concurrent: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
                              request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
                              backpressure_threshold: float = DEFAULT_BACKPRESSURE_THRESHOLD,
                              circuit_breaker_threshold: float = DEFAULT_CIRCUIT_BREAKER_THRESHOLD,
                              circuit_breaker_reset_time: float = DEFAULT_CIRCUIT_BREAKER_RESET_TIME) -> None:
    """
    Configure the default overload handler.
    
    Args:
        max_size: Maximum queue size
        max_concurrent: Maximum number of concurrent requests
        request_timeout: Request timeout in seconds
        backpressure_threshold: Threshold for applying backpressure (0.0-1.0)
        circuit_breaker_threshold: Threshold for tripping the circuit breaker (0.0-1.0)
        circuit_breaker_reset_time: Time in seconds before resetting the circuit breaker
    """
    global default_queue
    
    default_queue = RequestQueue(
        max_size=max_size,
        max_concurrent=max_concurrent,
        request_timeout=request_timeout,
        backpressure_threshold=backpressure_threshold,
        circuit_breaker_threshold=circuit_breaker_threshold,
        circuit_breaker_reset_time=circuit_breaker_reset_time
    )
    
    app_logger.info(f"Configured overload handler with max_size={max_size}, "
                   f"max_concurrent={max_concurrent}, request_timeout={request_timeout}s")

def get_overload_stats() -> Dict[str, Any]:
    """
    Get overload handler statistics.
    
    Returns:
        Dictionary with overload handler statistics
    """
    global default_queue
    
    return default_queue.get_stats()
