"""
Task scheduler for ProAPI.

This module provides a task scheduler for CPU and I/O bound operations,
with automatic detection and intelligent routing to appropriate executors.
"""

import asyncio
import concurrent.futures
import functools
import inspect
import time
import threading
import multiprocessing
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar

from .logging import app_logger

# Type variable for generic function
T = TypeVar('T')

# Default thread and process pool sizes
DEFAULT_THREAD_POOL_SIZE = min(32, (multiprocessing.cpu_count() or 1) * 4)
DEFAULT_PROCESS_POOL_SIZE = max(2, multiprocessing.cpu_count() or 1)

# Global executors
_thread_executor = None
_process_executor = None

# Lock for thread-safe initialization
_executor_lock = threading.RLock()

def get_thread_executor(max_workers: Optional[int] = None) -> concurrent.futures.ThreadPoolExecutor:
    """
    Get or create the thread pool executor.
    
    Args:
        max_workers: Maximum number of worker threads
        
    Returns:
        Thread pool executor
    """
    global _thread_executor
    
    if _thread_executor is None:
        with _executor_lock:
            if _thread_executor is None:
                workers = max_workers or DEFAULT_THREAD_POOL_SIZE
                _thread_executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=workers,
                    thread_name_prefix="ProAPI-Thread"
                )
                app_logger.debug(f"Created thread pool executor with {workers} workers")
    
    return _thread_executor

def get_process_executor(max_workers: Optional[int] = None) -> concurrent.futures.ProcessPoolExecutor:
    """
    Get or create the process pool executor.
    
    Args:
        max_workers: Maximum number of worker processes
        
    Returns:
        Process pool executor
    """
    global _process_executor
    
    if _process_executor is None:
        with _executor_lock:
            if _process_executor is None:
                workers = max_workers or DEFAULT_PROCESS_POOL_SIZE
                _process_executor = concurrent.futures.ProcessPoolExecutor(
                    max_workers=workers
                )
                app_logger.debug(f"Created process pool executor with {workers} workers")
    
    return _process_executor

def shutdown_executors(wait: bool = True) -> None:
    """
    Shutdown all executors.
    
    Args:
        wait: Wait for pending tasks to complete
    """
    global _thread_executor, _process_executor
    
    with _executor_lock:
        if _thread_executor is not None:
            app_logger.debug("Shutting down thread pool executor")
            _thread_executor.shutdown(wait=wait)
            _thread_executor = None
        
        if _process_executor is not None:
            app_logger.debug("Shutting down process pool executor")
            _process_executor.shutdown(wait=wait)
            _process_executor = None

def is_cpu_bound(func: Callable) -> bool:
    """
    Heuristically determine if a function is CPU-bound.
    
    This is a best-effort detection and may not be accurate in all cases.
    
    Args:
        func: Function to check
        
    Returns:
        True if the function is likely CPU-bound, False otherwise
    """
    # Get the source code if possible
    try:
        source = inspect.getsource(func)
        
        # Check for indicators of CPU-intensive operations
        cpu_indicators = [
            "for ", "while ", "math.", "numpy.", "np.", "calculate", "compute",
            "process", "transform", "sort", "filter", "map", "reduce", "sum(",
            "min(", "max(", "sorted(", "list(", "set(", "dict(", "tuple(",
            "comprehension", "generator", "factorial", "fibonacci", "prime",
            "encrypt", "decrypt", "hash", "compress", "decompress"
        ]
        
        # Check for indicators of I/O operations
        io_indicators = [
            "open(", "read(", "write(", "close(", "file", "socket", "connect",
            "request", "response", "http", "fetch", "download", "upload",
            "database", "query", "sql", "db.", "mongo", "redis", "cache",
            "sleep(", "wait(", "delay", "timeout", "requests.", "aiohttp",
            "urllib", "httpx", "boto3", "s3", "dynamodb", "sqs", "sns"
        ]
        
        # Count indicators
        cpu_count = sum(1 for indicator in cpu_indicators if indicator in source)
        io_count = sum(1 for indicator in io_indicators if indicator in source)
        
        # If there are more CPU indicators than I/O indicators, it's likely CPU-bound
        return cpu_count > io_count
    except (TypeError, OSError):
        # If we can't get the source, assume it's not CPU-bound
        return False

def run_in_thread(func: Callable[..., T]) -> Callable[..., asyncio.Future[T]]:
    """
    Run a function in a thread pool.
    
    Args:
        func: Function to run
        
    Returns:
        Async function that runs the original function in a thread pool
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        executor = get_thread_executor()
        return await loop.run_in_executor(
            executor,
            lambda: func(*args, **kwargs)
        )
    
    return wrapper

def run_in_process(func: Callable[..., T]) -> Callable[..., asyncio.Future[T]]:
    """
    Run a function in a process pool.
    
    Args:
        func: Function to run
        
    Returns:
        Async function that runs the original function in a process pool
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        executor = get_process_executor()
        
        # We need to create a partial function since we can't pass kwargs to run_in_executor
        pfunc = functools.partial(func, *args, **kwargs)
        
        return await loop.run_in_executor(executor, pfunc)
    
    return wrapper

def auto_offload(func: Callable[..., T]) -> Callable[..., Union[T, asyncio.Future[T]]]:
    """
    Automatically offload a function to the appropriate executor based on its characteristics.
    
    Args:
        func: Function to offload
        
    Returns:
        Function that runs in the appropriate executor
    """
    # Check if the function is already async
    if inspect.iscoroutinefunction(func):
        return func
    
    # Determine if the function is CPU-bound
    if is_cpu_bound(func):
        app_logger.debug(f"Auto-offloading CPU-bound function {func.__name__} to process pool")
        return run_in_process(func)
    else:
        app_logger.debug(f"Auto-offloading I/O-bound function {func.__name__} to thread pool")
        return run_in_thread(func)

class TaskScheduler:
    """
    Task scheduler for ProAPI.
    
    This class provides methods for scheduling tasks to run in thread or process pools,
    with automatic detection of the appropriate executor.
    """
    
    def __init__(self, 
                 thread_workers: Optional[int] = None, 
                 process_workers: Optional[int] = None):
        """
        Initialize the task scheduler.
        
        Args:
            thread_workers: Maximum number of worker threads
            process_workers: Maximum number of worker processes
        """
        self.thread_workers = thread_workers or DEFAULT_THREAD_POOL_SIZE
        self.process_workers = process_workers or DEFAULT_PROCESS_POOL_SIZE
        
        # Initialize executors
        self._thread_executor = None
        self._process_executor = None
    
    @property
    def thread_executor(self) -> concurrent.futures.ThreadPoolExecutor:
        """Get the thread pool executor."""
        if self._thread_executor is None:
            self._thread_executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.thread_workers,
                thread_name_prefix="ProAPI-Thread"
            )
        return self._thread_executor
    
    @property
    def process_executor(self) -> concurrent.futures.ProcessPoolExecutor:
        """Get the process pool executor."""
        if self._process_executor is None:
            self._process_executor = concurrent.futures.ProcessPoolExecutor(
                max_workers=self.process_workers
            )
        return self._process_executor
    
    def run_in_thread(self, func: Callable[..., T], *args, **kwargs) -> asyncio.Future[T]:
        """
        Run a function in a thread pool.
        
        Args:
            func: Function to run
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Future for the function result
        """
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(
            self.thread_executor,
            lambda: func(*args, **kwargs)
        )
    
    def run_in_process(self, func: Callable[..., T], *args, **kwargs) -> asyncio.Future[T]:
        """
        Run a function in a process pool.
        
        Args:
            func: Function to run
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Future for the function result
        """
        loop = asyncio.get_event_loop()
        
        # We need to create a partial function since we can't pass kwargs to run_in_executor
        pfunc = functools.partial(func, *args, **kwargs)
        
        return loop.run_in_executor(self.process_executor, pfunc)
    
    def auto_offload(self, func: Callable[..., T], *args, **kwargs) -> Union[T, asyncio.Future[T]]:
        """
        Automatically offload a function to the appropriate executor based on its characteristics.
        
        Args:
            func: Function to offload
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result or future for the function result
        """
        # Check if the function is already async
        if inspect.iscoroutinefunction(func):
            return func(*args, **kwargs)
        
        # Determine if the function is CPU-bound
        if is_cpu_bound(func):
            app_logger.debug(f"Auto-offloading CPU-bound function {func.__name__} to process pool")
            return self.run_in_process(func, *args, **kwargs)
        else:
            app_logger.debug(f"Auto-offloading I/O-bound function {func.__name__} to thread pool")
            return self.run_in_thread(func, *args, **kwargs)
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown all executors.
        
        Args:
            wait: Wait for pending tasks to complete
        """
        if self._thread_executor is not None:
            app_logger.debug("Shutting down thread pool executor")
            self._thread_executor.shutdown(wait=wait)
            self._thread_executor = None
        
        if self._process_executor is not None:
            app_logger.debug("Shutting down process pool executor")
            self._process_executor.shutdown(wait=wait)
            self._process_executor = None

# Create a default task scheduler
default_scheduler = TaskScheduler()

# Decorator for offloading functions to thread pool
def thread_task(func):
    """
    Decorator to run a function in a thread pool.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await run_in_thread(func)(*args, **kwargs)
    
    return wrapper

# Decorator for offloading functions to process pool
def process_task(func):
    """
    Decorator to run a function in a process pool.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await run_in_process(func)(*args, **kwargs)
    
    return wrapper

# Decorator for auto-offloading functions
def auto_task(func):
    """
    Decorator to automatically offload a function to the appropriate executor.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        offloaded = auto_offload(func)
        if inspect.iscoroutinefunction(offloaded):
            return await offloaded(*args, **kwargs)
        else:
            return await offloaded(*args, **kwargs)
    
    return wrapper
