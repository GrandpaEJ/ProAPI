# ProAPI Documentation

ProAPI is a lightweight, beginner-friendly yet powerful Python web framework. It provides a simple and intuitive API for building web applications and APIs.

## Features

- **Decorator-based routing** - Define routes with simple decorators like `@app.get()`, `@app.post()`, etc.
- **Simple template rendering** - Render templates with Jinja2
- **Easy server startup** - Start your server with a simple `app.run()`
- **Session management** - Built-in support for user sessions
- **Async support** - Optional async support for high-performance applications
- **Cython-based compilation** - Optional Cython-based compilation for speed
- **Minimal dependencies** - Keep your project lightweight
- **Built-in JSON support** - Automatic JSON serialization and deserialization
- **Middleware system** - Add middleware for request/response processing
- **Automatic API documentation** - Generate API documentation with Swagger UI
- **Structured logging** - Built-in logging with Loguru
- **CLI commands** - Command-line interface for common tasks
- **WebSocket support** - Built-in WebSocket support with room management and broadcasting
- **Fast mode** - Optimized request handling with route caching and object pooling
- **Response compression** - Automatic response compression for better performance

## Installation

```bash
pip install proapi
```

## Quick Start

```python
from proapi import ProAPI

app = ProAPI(debug=True)

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

# WebSocket example
@app.websocket("/ws")
async def websocket_handler(websocket):
    await websocket.accept()

    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Echo: {message}")

if __name__ == "__main__":
    # Run with fast mode for better performance
    app.run(fast=True)
```

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