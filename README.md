# ProAPI

A lightweight, beginner-friendly yet powerful Python web framework - simpler than Flask, faster than FastAPI.

## Details 
[💝Read The Full Docs](docs/README.md)

## Features

- **Simpler than Flask/FastAPI** with intuitive API design
- **Faster than FastAPI** with optimized routing and request handling
- **Stable like Flask** with robust error handling
- Decorator-based routing (`@app.get()`, `@app.post()`, etc.)
- Simple template rendering with Jinja2
- Easy server startup with `app.run()`
- Session management for user state
- Optional async support
- Optional Cython-based compilation for speed boost
- Minimal dependencies
- Built-in JSON support
- Middleware/plugin system
- Automatic API documentation at `/.docs`
- Structured logging with Loguru
- Smart auto-reloader for development
- Port forwarding with Cloudflare to expose apps to the internet
- CLI commands

### Advanced Reliability Features
- **Built-in protection against event-loop blocking**
- **Intelligent task scheduler** for heavy CPU/I/O operations
- **Graceful overload handler** with queue and backpressure system
- **Multiprocess worker manager** with health monitoring
- **Safe fallback to sync mode** for blocking routes
- **Auto-restart on failure** for workers

## Installation

```bash
pip install proapi
```

This will install ProAPI with all core dependencies including:
- loguru (for structured logging)
- uvicorn (for ASGI server and auto-reloading)
- jinja2 (for templating)
- watchdog (for file monitoring)
- pydantic (for data validation)

For development tools:

```bash
pip install proapi[dev]
```

For production extras:

```bash
pip install proapi[prod]
```

For Cloudflare Tunnel support:

```bash
pip install proapi[cloudflare]
```

For Cython compilation support:

```bash
pip install proapi[cython]
```

For all features:

```bash
pip install proapi[full]
```

## Quick Start

```python
from proapi import ProAPI

app = ProAPI(debug=True)

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

@app.get("/hello/{name}")
def hello(name, request):
    return {"message": f"Hello, {name}!"}

if __name__ == "__main__":
    app.run()
```

## API Documentation

ProAPI automatically generates API documentation for your application using Swagger UI at `/.docs`:

```python
# Documentation is enabled by default at /.docs
app = ProAPI()

# You can customize the docs URL if needed
app = ProAPI(
    enable_docs=True,  # Already true by default
    docs_url="/api-docs"  # Change from default /.docs
)
```

This makes interactive Swagger UI documentation available at the specified URL and OpenAPI specification at `{docs_url}/json`.

The automatic documentation makes it easy to explore and test your API without any additional configuration.

## Port Forwarding with Cloudflare

ProAPI can automatically expose your local server to the internet using Cloudflare Tunnel:

```python
# Enable Cloudflare Tunnel when running
app.run(forward=True)
```

You can also enable it from the CLI:

```bash
# Use Cloudflare Tunnel
proapi run app.py --forward

# Use Cloudflare with an authenticated tunnel
proapi run app.py --forward --cf-token YOUR_TOKEN
```

Note: You need to install the Cloudflare support package first:

```bash
pip install proapi[cloudflare]
```

## Template Rendering

```python
from proapi import ProAPI, render

app = ProAPI()

@app.get("/")
def index():
    return render("index.html", title="Home", message="Welcome!")
```

## Async Support

```python
from proapi import ProAPI

app = ProAPI()

@app.get("/async-example")
async def async_example():
    # Perform async operations
    await some_async_function()
    return {"result": "Async operation completed"}
```

## Session Management

```python
from proapi import ProAPI

app = ProAPI(
    enable_sessions=True,
    session_secret_key="your-secret-key-here"
)

@app.get("/")
def index(request):
    # Get visit count from session
    visit_count = request.session.get("visit_count", 0)

    # Increment and store in session
    request.session["visit_count"] = visit_count + 1

    return {"visit_count": visit_count + 1}
```

## Middleware

```python
from proapi import ProAPI

app = ProAPI()

@app.use
def logging_middleware(request):
    print(f"Request: {request.method} {request.path}")
    return request

@app.get("/")
def index():
    return {"message": "Hello, World!"}
```

## Logging with Loguru

ProAPI integrates with Loguru for structured logging:

```python
from proapi import ProAPI, app_logger

# Configure logging in the app
app = ProAPI(
    debug=True,
    log_level="DEBUG",
    log_format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    log_file="logs/app.log"
)

@app.get("/")
def index(request):
    app_logger.info(f"User accessed the home page")
    return {"message": "Hello, World!"}

# Use structured logging with context
@app.get("/users/{user_id}")
def get_user(user_id, request):
    # Add context to logs
    logger = app_logger.bind(user_id=user_id)
    logger.info("User details requested")

    # Log different levels
    if not user_id.isdigit():
        logger.warning("Invalid user ID format")
        return {"error": "Invalid user ID"}

    return {"id": user_id, "name": "Example User"}
```

## Auto-Reloader

ProAPI includes auto-reloading for development that automatically restarts the server when code changes are detected. It uses uvicorn's reloader for maximum reliability:

```python
from proapi import ProAPI

# Enable auto-reloader in the app
app = ProAPI(
    debug=True,
    use_reloader=True  # Requires uvicorn: pip install uvicorn
)

@app.get("/")
def index():
    return {"message": "Edit this file and save to see auto-reload in action!"}

if __name__ == "__main__":
    app.run()
```

You can also enable it when running:

```python
app.run(use_reloader=True)
```

Or from the CLI:

```bash
proapi run app.py --reload
```

Note: Auto-reloading is powered by uvicorn, which is now included as a core dependency.

## CLI Commands

ProAPI comes with a powerful command-line interface for creating and running applications.

### Initialize a new project

```bash
# Initialize in a new directory
proapi init myproject

# Initialize in the current directory
proapi init .

# Initialize with a specific template
proapi init myproject --template api
```

Available templates:
- `basic` - Simple app with basic routes (default)
- `api` - REST API with modular structure and example endpoints
- `web` - Web application with Jinja2 templates and static files

### Run an application

```bash
# Basic run
proapi run app.py

# Run with debug mode and auto-reload
proapi run app.py --debug --reload

# Run with fast mode for better performance
proapi run app.py --fast

# Run with Cloudflare port forwarding
proapi run app.py --forward

# Run a specific app instance from a module
proapi run mymodule:app

# Compile with Cython before running (requires proapi[cython])
proapi -c run app.py
```

### Check version and dependencies

```bash
# Show version information
proapi version

# Or use the shorthand
proapi -v
```

This will display the ProAPI version, Python version, platform information, and the status of optional dependencies.

## Performance Optimization

ProAPI offers two ways to optimize performance:

### Fast Mode

Enable fast mode for optimized request handling and routing:

```python
# Enable fast mode when creating the app
app = ProAPI(fast_mode=True)

# Or enable it when running
app.run(fast=True)
```

From the CLI:

```bash
proapi run app.py --fast
```

### Cython Compilation

For even better performance, you can compile your app with Cython:

```bash
# First install Cython support
pip install proapi[cython]

# Then compile and run
proapi run app.py --compile
```

## Reliability Features

ProAPI includes advanced reliability features to ensure your application runs smoothly under heavy load and handles failures gracefully.

### Event Loop Protection

```python
from proapi import ProAPI

# Enable event loop protection (enabled by default)
app = ProAPI(protect_event_loop=True)
```

### Intelligent Task Scheduler

```python
from proapi import ProAPI
from proapi.scheduler import thread_task, process_task, auto_task

app = ProAPI()

# Automatically determine the best executor
@app.get("/auto")
@auto_task
def auto_route(request):
    # This will be automatically routed to a thread or process pool
    return {"result": compute_something_heavy()}
```

### Graceful Overload Handler

```python
from proapi import ProAPI

# Configure overload protection
app = ProAPI(
    enable_overload_protection=True,  # Enabled by default
    max_concurrent_requests=100,      # Maximum concurrent requests
    request_queue_size=1000           # Maximum queue size
)
```

### Worker Auto-Restart

```python
from proapi import ProAPI

# Enable auto-restart for workers
app = ProAPI(
    workers=4,                  # Number of worker processes
    auto_restart_workers=True    # Enable auto-restart (enabled by default)
)

# Run the application
app.run()
```
[💝Read The Full Docs](docs/README.md)

See the [Reliability Documentation](docs/reliability.md) for more details.

## License
[MIT](LICENSE)
