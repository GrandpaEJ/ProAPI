"""
Multiprocess worker manager for ProAPI.

This module provides a multiprocess worker manager similar to Gunicorn,
with worker health monitoring and automatic restart on failure.
"""

import os
import signal
import subprocess
import sys
import time
import threading
import multiprocessing
from typing import Any, Callable, Dict, List, Optional, Union, Set

from .logging import app_logger

# Default settings
DEFAULT_WORKERS = max(2, multiprocessing.cpu_count())
DEFAULT_WORKER_TIMEOUT = 30  # seconds
DEFAULT_WORKER_MAX_REQUESTS = 1000
DEFAULT_WORKER_MAX_MEMORY_MB = 512  # MB
DEFAULT_WORKER_RESTART_DELAY = 3  # seconds

class Worker:
    """
    Worker process for handling requests.
    
    This class represents a worker process that handles requests.
    """
    
    def __init__(self, 
                 worker_id: int,
                 cmd: List[str],
                 timeout: int = DEFAULT_WORKER_TIMEOUT,
                 max_requests: int = DEFAULT_WORKER_MAX_REQUESTS,
                 max_memory_mb: int = DEFAULT_WORKER_MAX_MEMORY_MB):
        """
        Initialize the worker.
        
        Args:
            worker_id: Worker ID
            cmd: Command to run
            timeout: Worker timeout in seconds
            max_requests: Maximum number of requests before restart
            max_memory_mb: Maximum memory usage in MB before restart
        """
        self.worker_id = worker_id
        self.cmd = cmd
        self.timeout = timeout
        self.max_requests = max_requests
        self.max_memory_mb = max_memory_mb
        
        self.process = None
        self.pid = None
        self.start_time = 0
        self.last_heartbeat = 0
        self.requests_handled = 0
        self.memory_usage_mb = 0
        self.restarts = 0
        self.last_restart_time = 0
        self.state = "stopped"
    
    def start(self) -> bool:
        """
        Start the worker process.
        
        Returns:
            True if the worker was started successfully, False otherwise
        """
        if self.process and self.process.poll() is None:
            # Process is already running
            return True
        
        try:
            # Start the process
            self.process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=dict(os.environ, PROAPI_WORKER_ID=str(self.worker_id))
            )
            
            self.pid = self.process.pid
            self.start_time = time.time()
            self.last_heartbeat = time.time()
            self.state = "starting"
            
            app_logger.info(f"Worker {self.worker_id} started (PID: {self.pid})")
            
            return True
        except Exception as e:
            app_logger.exception(f"Error starting worker {self.worker_id}: {e}")
            self.state = "error"
            return False
    
    def stop(self, timeout: Optional[int] = None) -> bool:
        """
        Stop the worker process.
        
        Args:
            timeout: Timeout in seconds for graceful shutdown
            
        Returns:
            True if the worker was stopped successfully, False otherwise
        """
        if not self.process or self.process.poll() is not None:
            # Process is not running
            self.state = "stopped"
            return True
        
        timeout = timeout or self.timeout
        
        try:
            # Send SIGTERM for graceful shutdown
            self.process.terminate()
            
            # Wait for the process to terminate
            try:
                self.process.wait(timeout=timeout)
                self.state = "stopped"
                app_logger.info(f"Worker {self.worker_id} stopped gracefully")
                return True
            except subprocess.TimeoutExpired:
                # Process didn't terminate, send SIGKILL
                self.process.kill()
                self.process.wait()
                self.state = "killed"
                app_logger.warning(f"Worker {self.worker_id} killed after timeout")
                return True
        except Exception as e:
            app_logger.exception(f"Error stopping worker {self.worker_id}: {e}")
            self.state = "error"
            return False
    
    def restart(self, delay: Optional[float] = None) -> bool:
        """
        Restart the worker process.
        
        Args:
            delay: Delay in seconds before restarting
            
        Returns:
            True if the worker was restarted successfully, False otherwise
        """
        delay = delay or DEFAULT_WORKER_RESTART_DELAY
        
        # Stop the worker
        if not self.stop():
            return False
        
        # Wait before restarting
        if delay > 0:
            time.sleep(delay)
        
        # Start the worker
        result = self.start()
        
        if result:
            self.restarts += 1
            self.last_restart_time = time.time()
        
        return result
    
    def update_stats(self) -> None:
        """Update worker statistics."""
        if not self.process or self.process.poll() is not None:
            # Process is not running
            self.state = "stopped"
            return
        
        # Update heartbeat
        self.last_heartbeat = time.time()
        
        # Update state
        if self.state == "starting" and time.time() - self.start_time > 5:
            self.state = "running"
        
        # Update memory usage
        try:
            import psutil
            process = psutil.Process(self.pid)
            self.memory_usage_mb = process.memory_info().rss / (1024 * 1024)
        except (ImportError, psutil.NoSuchProcess):
            # psutil not available or process not found
            pass
    
    def is_healthy(self) -> bool:
        """
        Check if the worker is healthy.
        
        Returns:
            True if the worker is healthy, False otherwise
        """
        if not self.process or self.process.poll() is not None:
            # Process is not running
            return False
        
        # Check if the worker is responsive
        if time.time() - self.last_heartbeat > self.timeout:
            app_logger.warning(f"Worker {self.worker_id} is not responsive")
            return False
        
        # Check if the worker has handled too many requests
        if self.max_requests > 0 and self.requests_handled >= self.max_requests:
            app_logger.info(f"Worker {self.worker_id} has handled {self.requests_handled} requests, "
                           f"exceeding the limit of {self.max_requests}")
            return False
        
        # Check if the worker is using too much memory
        if self.max_memory_mb > 0 and self.memory_usage_mb > self.max_memory_mb:
            app_logger.warning(f"Worker {self.worker_id} is using {self.memory_usage_mb:.1f} MB of memory, "
                              f"exceeding the limit of {self.max_memory_mb} MB")
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get worker statistics.
        
        Returns:
            Dictionary with worker statistics
        """
        return {
            "worker_id": self.worker_id,
            "pid": self.pid,
            "state": self.state,
            "start_time": self.start_time,
            "uptime": time.time() - self.start_time if self.start_time > 0 else 0,
            "last_heartbeat": self.last_heartbeat,
            "requests_handled": self.requests_handled,
            "memory_usage_mb": self.memory_usage_mb,
            "restarts": self.restarts,
            "last_restart_time": self.last_restart_time,
            "healthy": self.is_healthy()
        }

class WorkerManager:
    """
    Multiprocess worker manager for ProAPI.
    
    This class manages multiple worker processes for handling requests,
    with health monitoring and automatic restart on failure.
    """
    
    def __init__(self, 
                 cmd: List[str],
                 num_workers: int = DEFAULT_WORKERS,
                 worker_timeout: int = DEFAULT_WORKER_TIMEOUT,
                 worker_max_requests: int = DEFAULT_WORKER_MAX_REQUESTS,
                 worker_max_memory_mb: int = DEFAULT_WORKER_MAX_MEMORY_MB,
                 worker_restart_delay: float = DEFAULT_WORKER_RESTART_DELAY):
        """
        Initialize the worker manager.
        
        Args:
            cmd: Command to run for each worker
            num_workers: Number of worker processes
            worker_timeout: Worker timeout in seconds
            worker_max_requests: Maximum number of requests before restart
            worker_max_memory_mb: Maximum memory usage in MB before restart
            worker_restart_delay: Delay in seconds before restarting a worker
        """
        self.cmd = cmd
        self.num_workers = num_workers
        self.worker_timeout = worker_timeout
        self.worker_max_requests = worker_max_requests
        self.worker_max_memory_mb = worker_max_memory_mb
        self.worker_restart_delay = worker_restart_delay
        
        self.workers: Dict[int, Worker] = {}
        self.monitor_thread = None
        self.running = False
        
        # Statistics
        self.start_time = 0
        self.total_restarts = 0
    
    def start(self) -> bool:
        """
        Start the worker manager.
        
        Returns:
            True if the worker manager was started successfully, False otherwise
        """
        if self.running:
            return True
        
        self.running = True
        self.start_time = time.time()
        
        # Start workers
        for i in range(self.num_workers):
            worker = Worker(
                worker_id=i,
                cmd=self.cmd,
                timeout=self.worker_timeout,
                max_requests=self.worker_max_requests,
                max_memory_mb=self.worker_max_memory_mb
            )
            
            self.workers[i] = worker
            worker.start()
        
        # Start monitor thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_workers,
            name="ProAPI-WorkerMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        
        app_logger.info(f"Started worker manager with {self.num_workers} workers")
        
        return True
    
    def stop(self, timeout: Optional[int] = None) -> bool:
        """
        Stop the worker manager.
        
        Args:
            timeout: Timeout in seconds for graceful shutdown
            
        Returns:
            True if the worker manager was stopped successfully, False otherwise
        """
        if not self.running:
            return True
        
        self.running = False
        
        # Stop workers
        for worker in self.workers.values():
            worker.stop(timeout)
        
        # Wait for monitor thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=timeout or 5.0)
        
        self.workers = {}
        self.monitor_thread = None
        
        app_logger.info("Stopped worker manager")
        
        return True
    
    def restart(self, worker_id: Optional[int] = None, delay: Optional[float] = None) -> bool:
        """
        Restart a worker or all workers.
        
        Args:
            worker_id: Worker ID to restart (None for all workers)
            delay: Delay in seconds before restarting
            
        Returns:
            True if the worker(s) were restarted successfully, False otherwise
        """
        delay = delay or self.worker_restart_delay
        
        if worker_id is not None:
            # Restart a specific worker
            if worker_id not in self.workers:
                app_logger.warning(f"Worker {worker_id} not found")
                return False
            
            result = self.workers[worker_id].restart(delay)
            
            if result:
                self.total_restarts += 1
            
            return result
        else:
            # Restart all workers
            success = True
            
            for i, worker in sorted(self.workers.items()):
                if not worker.restart(delay):
                    success = False
                else:
                    self.total_restarts += 1
                
                # Add a small delay between worker restarts
                if i < len(self.workers) - 1:
                    time.sleep(1.0)
            
            return success
    
    def _monitor_workers(self) -> None:
        """Monitor workers for health and restart if necessary."""
        while self.running:
            try:
                # Update worker statistics
                for worker in self.workers.values():
                    worker.update_stats()
                
                # Check worker health
                for worker_id, worker in self.workers.items():
                    if not worker.is_healthy():
                        app_logger.warning(f"Worker {worker_id} is unhealthy, restarting")
                        worker.restart(self.worker_restart_delay)
                        self.total_restarts += 1
            except Exception as e:
                app_logger.exception(f"Error in worker monitor: {e}")
            
            # Sleep before checking again
            time.sleep(5.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get worker manager statistics.
        
        Returns:
            Dictionary with worker manager statistics
        """
        return {
            "num_workers": self.num_workers,
            "running": self.running,
            "start_time": self.start_time,
            "uptime": time.time() - self.start_time if self.start_time > 0 else 0,
            "total_restarts": self.total_restarts,
            "workers": {i: worker.get_stats() for i, worker in self.workers.items()}
        }

def run_with_workers(cmd: List[str],
                    num_workers: int = DEFAULT_WORKERS,
                    worker_timeout: int = DEFAULT_WORKER_TIMEOUT,
                    worker_max_requests: int = DEFAULT_WORKER_MAX_REQUESTS,
                    worker_max_memory_mb: int = DEFAULT_WORKER_MAX_MEMORY_MB,
                    worker_restart_delay: float = DEFAULT_WORKER_RESTART_DELAY) -> None:
    """
    Run a command with multiple worker processes.
    
    Args:
        cmd: Command to run for each worker
        num_workers: Number of worker processes
        worker_timeout: Worker timeout in seconds
        worker_max_requests: Maximum number of requests before restart
        worker_max_memory_mb: Maximum memory usage in MB before restart
        worker_restart_delay: Delay in seconds before restarting a worker
    """
    # Create worker manager
    manager = WorkerManager(
        cmd=cmd,
        num_workers=num_workers,
        worker_timeout=worker_timeout,
        worker_max_requests=worker_max_requests,
        worker_max_memory_mb=worker_max_memory_mb,
        worker_restart_delay=worker_restart_delay
    )
    
    # Start worker manager
    manager.start()
    
    # Handle signals
    def handle_signal(signum, frame):
        app_logger.info(f"Received signal {signum}, stopping worker manager")
        manager.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Wait for worker manager to finish
    try:
        while manager.running:
            time.sleep(1.0)
    except KeyboardInterrupt:
        app_logger.info("Received keyboard interrupt, stopping worker manager")
        manager.stop()
    
    app_logger.info("Worker manager finished")
