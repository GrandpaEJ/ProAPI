# Reliability and Performance Features in ProAPI

ProAPI includes advanced reliability and performance features to ensure your application runs smoothly under heavy load and handles failures gracefully.

## Event Loop Protection

ProAPI includes built-in protection against event loop blocking, which can cause performance issues in asynchronous applications.

### How It Works

The event loop protection system monitors the event loop for blocking operations and automatically offloads them to thread or process pools when necessary.

```python
from proapi import ProAPI

# Enable event loop protection (enabled by default)
app = ProAPI(protect_event_loop=True)
```

### Benefits

- Prevents long-running operations from blocking the event loop
- Automatically detects and logs slow callbacks
- Provides warnings and suggestions for improving performance
- Maintains responsiveness even under heavy load

## Intelligent Task Scheduler

ProAPI includes an intelligent task scheduler that automatically detects CPU-bound and I/O-bound operations and routes them to the appropriate executor.

### Using Task Decorators

```python
from proapi import ProAPI
from proapi.scheduler import thread_task, process_task, auto_task

app = ProAPI()

# Automatically determine the best executor
@app.get("/auto")
@auto_task
def auto_route(request):
    # This will be automatically routed to a thread or process pool
    # based on whether it's CPU-bound or I/O-bound
    return {"result": compute_something_heavy()}

# Explicitly use a thread pool for I/O-bound operations
@app.get("/thread")
@thread_task
def thread_route(request):
    # This will run in a thread pool
    return {"result": fetch_from_database()}

# Explicitly use a process pool for CPU-bound operations
@app.get("/process")
@process_task
def process_route(request):
    # This will run in a process pool
    return {"result": compute_heavy_calculation()}
```

### Benefits

- Automatically detects CPU-bound and I/O-bound operations
- Routes tasks to the appropriate executor for optimal performance
- Prevents blocking the event loop
- Improves overall application responsiveness

## Graceful Overload Handler

ProAPI includes a graceful overload handler that prevents server crashes under heavy load by implementing a queue with backpressure.

### How It Works

The overload handler uses a combination of queuing, backpressure, and circuit breaker patterns to ensure your application remains responsive even under extreme load.

```python
from proapi import ProAPI

# Configure overload protection
app = ProAPI(
    enable_overload_protection=True,  # Enabled by default
    max_concurrent_requests=100,      # Maximum concurrent requests
    request_queue_size=1000           # Maximum queue size
)
```

### Benefits

- Prevents server crashes under heavy load
- Implements backpressure to slow down clients when necessary
- Uses circuit breaker pattern to reject requests when overloaded
- Provides detailed statistics for monitoring

## Multiprocess Worker Manager

ProAPI includes a multiprocess worker manager similar to Gunicorn, with worker health monitoring and automatic restart on failure.

### How It Works

The worker manager creates and manages multiple worker processes, monitors their health, and automatically restarts them if they fail or become unresponsive.

```python
from proapi import ProAPI

# Enable auto-restart for workers
app = ProAPI(
    workers=4,                  # Number of worker processes
    auto_restart_workers=True   # Enable auto-restart (enabled by default)
)

# Run the application
app.run()
```

### Benefits

- Automatically restarts workers on failure
- Monitors worker health and resource usage
- Prevents memory leaks by recycling workers
- Improves overall application stability

## Safe Fallback for Blocking Routes

ProAPI includes automatic detection and handling of blocking routes, with fallback to synchronous mode for blocking operations.

### How It Works

The blocking handler automatically detects routes that block the event loop and offloads them to thread or process pools.

```python
from proapi import ProAPI
from proapi.blocking_handler import with_blocking_detection, safe_sync_fallback

app = ProAPI(auto_offload_blocking=True)  # Enabled by default

# Automatically detect and handle blocking routes
@app.get("/blocking")
@with_blocking_detection()
def blocking_route(request):
    # This will be automatically detected as blocking
    # and offloaded to a thread or process pool
    return {"result": compute_something_heavy()}

# Safely fall back to synchronous mode for async routes
@app.get("/fallback")
@safe_sync_fallback
async def fallback_route(request):
    # If this async route fails, it will safely fall back to sync mode
    return {"result": await async_operation()}
```

### Benefits

- Automatically detects blocking routes
- Offloads blocking operations to thread or process pools
- Provides safe fallback for async routes
- Improves overall application stability

## Auto-Restart on Failure

ProAPI includes automatic restart on failure for both the application and individual workers.

### How It Works

The auto-restart system monitors the application and worker processes and automatically restarts them if they fail or become unresponsive.

```python
from proapi import ProAPI

# Enable auto-restart for workers
app = ProAPI(auto_restart_workers=True)  # Enabled by default

# Run the application
app.run()
```

### Benefits

- Automatically restarts workers on failure
- Monitors worker health and resource usage
- Prevents memory leaks by recycling workers
- Improves overall application stability

## Combining Features

All these features work together to provide a robust, reliable, and high-performance application:

```python
from proapi import ProAPI
from proapi.scheduler import auto_task
from proapi.blocking_handler import with_blocking_detection

# Create a ProAPI application with all reliability features enabled
app = ProAPI(
    debug=True,
    fast_mode=True,
    protect_event_loop=True,
    auto_offload_blocking=True,
    enable_overload_protection=True,
    auto_restart_workers=True,
    workers=4,
    max_concurrent_requests=100,
    request_queue_size=1000
)

# Use the features in your routes
@app.get("/")
@auto_task
@with_blocking_detection()
def index(request):
    # This route is protected by all reliability features
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run()
```

## Monitoring and Statistics

ProAPI provides detailed statistics for monitoring the performance and reliability of your application:

```python
from proapi import ProAPI
from proapi.loop_protection import get_loop_stats
from proapi.overload_handler import get_overload_stats
from proapi.blocking_handler import get_blocking_routes

app = ProAPI()

@app.get("/stats")
def stats(request):
    return {
        "loop_stats": get_loop_stats(),
        "overload_stats": get_overload_stats(),
        "blocking_routes": get_blocking_routes()
    }
```

This endpoint will return detailed statistics about the event loop, overload handler, and blocking routes, which can be used for monitoring and debugging.
