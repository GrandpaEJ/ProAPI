# ProAPI Documentation

ProAPI is a lightweight, beginner-friendly yet powerful Python web framework designed to make web development simple and intuitive.

## Key Benefits

- **Simpler than Flask/FastAPI** with intuitive API design
- **Faster than FastAPI** with optimized routing and request handling
- **Stable like Flask** with robust error handling
- **Easy to use** with minimal boilerplate code
- **Optional Cython compilation** for even better performance

## Documentation Sections

### Core Concepts
- [Getting Started](getting-started.md) - Basic usage and concepts
- [Routing](routing.md) - URL routing and path parameters
- [Request and Response](request-response.md) - Working with HTTP requests and responses
- [Templates](templates.md) - Template rendering with Jinja2
- [Sessions](sessions.md) - Session management
- [Middleware](middleware.md) - Using and creating middleware

### Features
- [API Documentation](api-docs.md) - Automatic API documentation at /.docs
- [WebSockets](websockets.md) - Real-time communication with WebSockets
- [WebSockets Advanced](websockets_advanced.md) - Advanced WebSocket features

### Performance
- [Fast Mode](fast_mode.md) - Optimized request handling
- [Optimization](optimization.md) - Performance optimization techniques

### Tools and Deployment
- [CLI](cli.md) - Command-line interface
- [Production Deployment](deployment.md) - Deploying to production
- [Advanced Features](advanced.md) - Advanced features and customization

### Summary
- [Summary](summary.md) - Overview of ProAPI features and capabilities

## Installation

### Basic Installation

```bash
pip install proapi
```

### With Optional Features

```bash
# For Cloudflare port forwarding
pip install proapi[cloudflare]

# For Cython compilation
pip install proapi[cython]

# For all features
pip install proapi[full]
```

## Quick Start

```python
from proapi import ProAPI

# Create a ProAPI application with debug mode and fast mode enabled
app = ProAPI(debug=True, fast_mode=True)

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

@app.get("/hello/{name}")
def hello(name, request):
    return {"message": f"Hello, {name}!"}

# API documentation is automatically available at /.docs

if __name__ == "__main__":
    app.run()
```

### Creating a New Project

You can quickly create a new project using the CLI:

```bash
# Initialize in a new directory
proapi init myproject

# Initialize in the current directory
proapi init .
```

## Features

### Routing

ProAPI supports decorator-based routing:

```python
@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

@app.post("/users")
def create_user(request):
    return {"id": 1, **request.json}

@app.put("/users/{id}")
def update_user(id, request):
    return {"id": id, **request.json}

@app.delete("/users/{id}")
def delete_user(id, request):
    return {"message": f"User {id} deleted"}
```

### Path Parameters

ProAPI supports path parameters with optional type annotations:

```python
@app.get("/users/{id}")
def get_user(id, request):
    return {"id": id, "name": f"User {id}"}

@app.get("/users/{id:int}")
def get_user_by_id(id, request):
    # id will be converted to an integer
    return {"id": id, "name": f"User {id}"}

@app.get("/products/{id:int}/reviews/{review_id:int}")
def get_review(id, review_id, request):
    return {"product_id": id, "review_id": review_id}
```

### Request Object

The request object provides access to request data:

```python
@app.post("/echo")
def echo(request):
    return {
        "method": request.method,
        "path": request.path,
        "headers": {k: v for k, v in request.headers.items()},
        "query_params": request.query_params,
        "json": request.json,
        "form": request.form
    }
```

### Template Rendering

ProAPI supports template rendering with Jinja2:

```python
from proapi import ProAPI, render

app = ProAPI(template_dir="templates")

@app.get("/")
def index(request):
    return render("index.html",
                 title="Home",
                 message="Welcome to ProAPI!")
```

### Sessions

ProAPI supports session management for storing user-specific data across requests:

```python
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

### Middleware

ProAPI supports middleware for request/response processing:

```python
@app.use
def logging_middleware(request):
    print(f"Request: {request.method} {request.path}")
    return request

@app.use
def auth_middleware(request):
    from proapi.server import Response

    # Check for API key
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return Response(
            status=401,
            body={"error": "API key required"},
            content_type="application/json"
        )

    # Store user info on the request
    request.user = {"id": 1, "name": "Test User"}
    return request
```

### Async Support

ProAPI supports async request handlers:

```python
import asyncio

@app.get("/async")
async def async_route(request):
    await asyncio.sleep(1)
    return {"message": "Async route"}
```

### Static Files

ProAPI supports serving static files:

```python
app = ProAPI(static_dir="static", static_url="/static")
```

### Error Handling

ProAPI provides built-in error handling:

```python
@app.get("/error")
def error(request):
    # This will be caught and return a 500 response
    return 1 / 0
```

### CLI

ProAPI provides a powerful command-line interface:

```bash
# Run an application
proapi run app.py

# Run with debug mode and auto-reload
proapi run app.py --debug --reload

# Run with fast mode for better performance
proapi run app.py --fast

# Run with Cloudflare port forwarding
proapi run app.py --forward

# Run a specific app instance from a module
proapi run mymodule:app

# Compile with Cython before running
proapi -c run app.py

# Initialize a new project
proapi init myproject

# Initialize in the current directory
proapi init .

# Show version information
proapi version
```

See the [CLI documentation](cli.md) for more details.

### Cython Compilation

ProAPI supports Cython compilation for improved performance:

```bash
# Install Cython support
pip install proapi[cython]

# Run with Cython compilation
proapi -c run app.py
```

> **Note:** Cython compilation requires a C compiler and development tools to be installed on your system. On Windows, you'll need Visual Studio with C++ development tools. On Linux, you'll need gcc and Python development headers.

### Port Forwarding with Cloudflare

ProAPI supports port forwarding to expose your local server to the internet using Cloudflare Tunnel:

```bash
# Install Cloudflare support
pip install proapi[cloudflare]
```

You can enable it when running your application:

```python
# Enable Cloudflare Tunnel when running
app.run(forward=True)
```

Or from the CLI:

```bash
# Use Cloudflare Tunnel
proapi run app.py --forward
```

#### Authenticated Tunnels

For more control, you can use authenticated tunnels:

```python
# Run with an authenticated tunnel (requires Cloudflare account)
app.run(forward=True, forward_kwargs={"token": "YOUR_TOKEN"})
```

From the CLI:

```bash
# Authenticated tunnel (requires Cloudflare account)
proapi run app.py --forward --cf-token YOUR_TOKEN
```

To create an authenticated tunnel:
1. Sign up for a Cloudflare account
2. Go to the Zero Trust dashboard: https://one.dash.cloudflare.com/
3. Create a tunnel and get the token
4. Use the token with the `--cf-token` option

## API Reference

### ProAPI

```python
ProAPI(
    debug=False,                # Enable debug mode for detailed error messages
    env="development",          # Environment: 'development', 'production', or 'testing'
    template_dir="templates",   # Directory for Jinja2 templates
    static_dir="static",       # Directory for static files
    static_url="/static",      # URL prefix for static files
    enable_cors=False,         # Enable CORS headers for cross-origin requests
    enable_docs=True,          # Enable API documentation at /.docs
    docs_url="/.docs",         # URL path for API documentation
    enable_sessions=False,     # Enable session support for user state
    session_secret_key=None,   # Secret key for signing session cookies
    fast_mode=False,           # Enable optimized request handling
    json_encoder=None          # Custom JSON encoder for response serialization
)
```

### Route Decorators

```python
@app.get(path, **kwargs)
@app.post(path, **kwargs)
@app.put(path, **kwargs)
@app.delete(path, **kwargs)
@app.patch(path, **kwargs)
```

### Middleware

```python
@app.use
def middleware(request):
    # Process request
    return request
```

### Run

```python
app.run(
    host=None,      # Host to bind to (default: 127.0.0.1 in development, 0.0.0.0 in production)
    port=8000,      # Port to bind to
    workers=None,   # Number of worker processes (default: 1, or 2+ in production)
    forward=False,  # Enable Cloudflare port forwarding
    use_reloader=None,  # Enable auto-reloading when code changes
    debug=None,     # Enable debug mode (overrides the instance setting)
    fast=None       # Enable fast mode with optimized request handling
)
```

### Template Rendering

```python
render(template_name, **context)
```

### Response

```python
from proapi.server import Response

Response(
    body=None,
    status=200,
    headers=None,
    content_type="text/html"
)
```

### API Documentation

ProAPI automatically generates API documentation for your application using Swagger UI:

```python
# Documentation is automatically available at /.docs
app = ProAPI()
```

You can customize the documentation URL and title if needed:

```python
app = ProAPI(
    enable_docs=True,       # Already true by default
    docs_url="/api-docs",   # Change from default /.docs
    docs_title="My API Documentation"  # Custom title for documentation
)
```

This makes interactive Swagger UI documentation available at the specified URL and OpenAPI specification at `{docs_url}/json`.

To access the documentation, simply navigate to `/.docs` (or your custom URL) in your browser.

#### Documentation Features

The documentation is automatically generated from your route handlers, including:

- Endpoint paths and methods
- Path parameters with types
- Request body schemas for POST/PUT/PATCH methods
- Response schemas
- Descriptions from docstrings

To improve the documentation, add detailed docstrings to your route handlers:

```python
@app.get("/users/{id:int}")
def get_user(id, request):
    """
    Get a user by ID.

    Returns a single user with the specified ID.
    """
    # Your code here
```

## Examples

See the [examples](../examples) directory for more examples.
