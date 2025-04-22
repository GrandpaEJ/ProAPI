# ProAPI

A lightweight, beginner-friendly yet powerful Python web framework.

## Features

- Decorator-based routing (`@app.get()`, `@app.post()`, etc.)
- Simple template rendering with Jinja2
- Easy server startup with `app.run()`
- Session management for user state
- Optional async support
- Optional Cython-based compilation for speed boost
- Minimal dependencies
- Built-in JSON support
- Middleware/plugin system
- Automatic API documentation
- Structured logging with Loguru
- Smart auto-reloader for development
- Port forwarding to expose apps to the internet
- CLI commands

## Installation

```bash
pip install proapi
```

This will install ProAPI with all core dependencies including:
- loguru (for logging)
- uvicorn (for ASGI server and auto-reloading)
- cython (for performance optimization)
- jinja2 (for templating)
- watchdog (for file monitoring)

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

ProAPI can automatically generate API documentation for your application using Swagger UI:

```python
app = ProAPI(
    debug=True,
    enable_docs=True,
    docs_url="/docs",
    docs_title="My API Documentation"
)
```

This will make interactive Swagger UI documentation available at `/docs` and OpenAPI specification at `/docs/json`.

Additionally, ProAPI automatically provides a default documentation endpoint at `/.docs` for all applications, regardless of whether you explicitly enable documentation. This makes it easy to quickly access API documentation without any additional configuration.

## Port Forwarding

ProAPI can automatically expose your local server to the internet:

```python
# Enable port forwarding in the app
app = ProAPI(enable_forwarding=True)

# Or enable it when running
app.run(forward=True)

# Use Cloudflare Tunnel
app.run(forward=True, forward_type="cloudflare")

# Use localtunnel
app.run(forward=True, forward_type="localtunnel")
```

You can also enable it from the CLI:

```bash
# Use ngrok (default)
proapi run app.py --forward

# Use Cloudflare Tunnel
proapi run app.py --forward --forward-type cloudflare

# Use Cloudflare with an authenticated tunnel
proapi run app.py --forward --forward-type cloudflare --cf-token YOUR_TOKEN

# Use localtunnel
proapi run app.py --forward --forward-type localtunnel
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

Create a new project:

```bash
proapi create myproject
```

Run an application:

```bash
proapi run app.py --debug --reload
```

## Performance Optimization

ProAPI can be compiled with Cython for better performance:

```bash
proapi run app.py --compile
```

## License

MIT
