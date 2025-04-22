# ProAPI Documentation

ProAPI is a lightweight, beginner-friendly yet powerful Python web framework designed to make web development simple and intuitive.

## Documentation Sections

- [Getting Started](getting-started.md) - Basic usage and concepts
- [Routing](routing.md) - URL routing and path parameters
- [Request and Response](request-response.md) - Working with HTTP requests and responses
- [Templates](templates.md) - Template rendering with Jinja2
- [Sessions](sessions.md) - Session management
- [Middleware](middleware.md) - Using and creating middleware
- [API Documentation](api-docs.md) - Automatic API documentation
- [CLI](cli.md) - Command-line interface
- [Production Deployment](deployment.md) - Deploying to production
- [Advanced Features](advanced.md) - Advanced features and customization

## Installation

```bash
pip install proapi
```

For full functionality:

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

ProAPI provides a command-line interface:

```bash
# Run an application
proapi run app.py

# Run a specific app instance from a module
proapi run module:app

# Run with specific port
proapi run app.py --port 5000
proapi run main:app --port 5500

# Run with host options
proapi run app.py --host local       # 127.0.0.1
proapi run app.py --host all         # 0.0.0.0
proapi run app.py --host 0.0.0.0     # All interfaces
proapi run main:app --host 0.0.0.0   # All interfaces

# Run with port forwarding (expose to the internet)
proapi run app.py --forward
proapi run app.py --forward --forward-type ngrok
proapi run app.py --forward --forward-type cloudflare
proapi run app.py --forward --forward-type localtunnel

# Run with Cloudflare authenticated tunnel
proapi run app.py --forward --forward-type cloudflare --cf-token YOUR_TOKEN

# Compile with Cython before running
proapi -c run app.py
proapi -c run main:app

# Run with other options
proapi run app.py --debug --port 8080 --workers 4

# Create a new project
proapi create myproject
```

#### CLI Command Reference

```
usage: proapi [-h] [-c] {run,create,version} ...

ProAPI command-line interface

options:
  -h, --help            show this help message and exit
  -c, --compile         Compile with Cython before running

commands:
  {run,create,version}  Command to run
    run                 Run a ProAPI application
    create              Create a new ProAPI project
    version             Show version information
```

#### Run Command

```
usage: proapi run [-h] [--host HOST] [--port PORT] [--debug] [--reload]
                  [--workers WORKERS] [--server SERVER]
                  app

positional arguments:
  app                  Application module or file, optionally with app instance
                       (module:app)

options:
  -h, --help           show this help message and exit
  --host HOST          Host to bind to (use 'local' for 127.0.0.1 or 'all' for
                       0.0.0.0)
  --port PORT          Port to bind to
  --debug              Enable debug mode
  --reload             Enable auto-reload
  --workers WORKERS    Number of worker processes
  --server SERVER      Server type (default, multiworker)
  --forward            Enable port forwarding to expose the app to the internet
  --forward-type {ngrok,cloudflare,localtunnel}
                       Port forwarding service to use (ngrok, cloudflare, or localtunnel)
  --cf-token CF_TOKEN  Cloudflare Tunnel token (for authenticated tunnels)
```

### Cython Compilation

ProAPI supports Cython compilation for improved performance:

```bash
# Run with Cython compilation
proapi -c run app.py
```

> **Note:** Cython compilation requires a C compiler and development tools to be installed on your system. On Windows, you'll need Visual Studio with C++ development tools. On Linux, you'll need gcc and Python development headers.

### Port Forwarding

ProAPI supports port forwarding to expose your local server to the internet:

```python
# Enable port forwarding in the app
app = ProAPI(enable_forwarding=True, forwarding_type="ngrok")

# Or enable it when running
app.run(forward=True, forward_type="ngrok")
```

You can also enable it from the CLI:

```bash
# Enable port forwarding with ngrok (default)
proapi run app.py --forward

# Use Cloudflare Tunnel
proapi run app.py --forward --forward-type cloudflare

# Use localtunnel
proapi run app.py --forward --forward-type localtunnel
```

#### Cloudflare Tunnel

ProAPI supports Cloudflare Tunnel for secure, authenticated tunnels:

```python
# Enable Cloudflare Tunnel in the app
app = ProAPI(enable_forwarding=True, forwarding_type="cloudflare")

# Run with an authenticated tunnel (requires Cloudflare account)
app.run(forward=True, forward_type="cloudflare", forward_kwargs={"token": "YOUR_TOKEN"})
```

From the CLI:

```bash
# Quick tunnel (no account required)
proapi run app.py --forward --forward-type cloudflare

# Authenticated tunnel (requires Cloudflare account)
proapi run app.py --forward --forward-type cloudflare --cf-token YOUR_TOKEN
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
    debug=False,
    template_dir="templates",
    static_dir="static",
    static_url="/static",
    enable_cors=False,
    enable_docs=False,
    docs_url="/docs",
    docs_title="API Documentation",
    enable_forwarding=False,
    forwarding_type="ngrok",
    enable_sessions=False,
    session_secret_key=None,
    session_cookie_name="session",
    session_max_age=3600,  # 1 hour
    session_secure=None,  # Based on environment
    session_http_only=True,
    session_same_site="Lax",
    session_backend="memory",
    json_encoder=None
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
    host="127.0.0.1",
    port=8000,
    server_type="default",
    workers=1,
    forward=None,  # Enable port forwarding (overrides enable_forwarding)
    forward_type=None,  # Type of port forwarding (overrides forwarding_type)
    **kwargs
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

#### Default Documentation

ProAPI automatically provides a default documentation endpoint at `/.docs` for all applications, regardless of whether you explicitly enable documentation. This makes it easy to quickly access API documentation without any additional configuration.

To access the default documentation, simply navigate to `/.docs` in your browser.

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
