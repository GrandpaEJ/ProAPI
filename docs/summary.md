# ProAPI Documentation Summary

This document provides a summary of the ProAPI documentation.

## Core Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](getting-started.md) | Introduction to ProAPI, installation, and basic usage |
| [Routing](routing.md) | Defining routes, path parameters, and URL patterns |
| [Request and Response](request-response.md) | Working with HTTP requests and responses |
| [Templates](templates.md) | Template rendering with Jinja2 |
| [Middleware](middleware.md) | Using and creating middleware |
| [API Documentation](api-docs.md) | Automatic API documentation with Swagger UI |
| [CLI](cli.md) | Command-line interface for running and creating applications |
| [Deployment](deployment.md) | Deploying applications to production |
| [Advanced Features](advanced.md) | Advanced features and customization options |

## Key Features

### Routing

ProAPI provides a simple and intuitive routing system using decorators:

```python
@app.get("/")
def index():
    return {"message": "Hello, World!"}

@app.get("/users/{user_id:int}")
def get_user(user_id):
    return {"user_id": user_id, "name": f"User {user_id}"}
```

### Request Handling

Access request data easily:

```python
@app.post("/echo")
def echo(request):
    return {
        "method": request.method,
        "path": request.path,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "json": request.json
    }
```

### Response Handling

Return various types of responses:

```python
# Return JSON
@app.get("/json")
def json_response():
    return {"message": "This is JSON"}

# Return HTML
@app.get("/html")
def html_response():
    return "<h1>Hello, World!</h1>"

# Return a custom response
@app.get("/custom")
def custom_response():
    from proapi.server import Response
    return Response(
        body="Custom response",
        status=200,
        headers={"X-Custom-Header": "Value"},
        content_type="text/plain"
    )
```

### Template Rendering

Render templates with Jinja2:

```python
from proapi import ProAPI, render

app = ProAPI(template_dir="templates")

@app.get("/")
def index():
    return render("index.html", 
                 title="ProAPI Example",
                 message="Welcome to ProAPI!")
```

### Middleware

Add middleware for request/response processing:

```python
@app.use
def logging_middleware(request):
    print(f"Request: {request.method} {request.path}")
    return request
```

### API Documentation

Generate API documentation automatically:

```python
app = ProAPI(
    enable_docs=True,
    docs_url="/docs",
    docs_title="My API Documentation"
)
```

### CLI

Use the command-line interface:

```bash
# Run an application
python -m proapi run app.py

# Create a new project
python -m proapi create myproject
```

### Async Support

Use async route handlers:

```python
@app.get("/async")
async def async_route():
    import asyncio
    await asyncio.sleep(0.1)
    return {"message": "Async route"}
```

## Quick Reference

### Application Configuration

```python
app = ProAPI(
    debug=True,                  # Enable debug mode
    env="development",           # Environment ('development', 'production', or 'testing')
    template_dir="templates",    # Directory for templates
    static_dir="static",         # Directory for static files
    static_url="/static",        # URL prefix for static files
    enable_cors=False,           # Enable CORS headers
    enable_docs=True,            # Enable API documentation
    docs_url="/docs",            # URL path for API documentation
    docs_title="API Documentation", # Title for API documentation
    log_level="INFO",            # Logging level
    log_file=None,               # Path to log file
    workers=1,                   # Number of worker processes (for production)
    request_timeout=30,          # Request timeout in seconds (for production)
    max_request_size=1024*1024,  # Maximum request size in bytes (for production)
    trusted_hosts=None,          # List of trusted hosts for production security
    use_reloader=None            # Enable auto-reloading when code changes
)
```

### Running the Application

```python
app.run(
    host="127.0.0.1",            # Host to bind to
    port=8000,                   # Port to bind to
    server_type="default",       # Server type ('default', 'uvicorn', 'gunicorn', 'multiworker')
    workers=1,                   # Number of worker processes
    forward=False,               # Enable port forwarding
    forward_type="ngrok",        # Type of port forwarding
    use_reloader=True            # Enable auto-reloading
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