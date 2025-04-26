# ProAPI Documentation

ProAPI is a lightweight, beginner-friendly yet powerful Python web framework. It provides a simple and intuitive API for building web applications and APIs.

## Key Benefits

- **Simpler than Flask/FastAPI** with intuitive API design
- **Faster than FastAPI** with optimized routing and request handling
- **Stable like Flask** with robust error handling
- **Easy to use** with minimal boilerplate code
- **Optional Cython compilation** for even better performance

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

### Advanced Reliability Features
- **Performance optimizations** - Route caching, object pooling, and efficient request handling
- **Intelligent task scheduler** - Auto-detection and routing of CPU/IO-bound operations
- **Multiprocess worker management** - Multiple worker processes for better concurrency
- **WebSocket optimization** - Efficient WebSocket handling and connection management

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

# WebSocket example
@app.websocket("/ws")
async def websocket_handler(websocket):
    await websocket.accept()

    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Echo: {message}")

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

## Documentation Sections

### Core Concepts
- [Getting Started](getting-started.md) - Basic usage and concepts
- [Routing](routing.md) - URL routing and path parameters
- [Request and Response](request-response.md) - Working with HTTP requests and responses
- [Custom Responses](custom-responses.md) - Creating custom responses with different content types
- [Templates](templates.md) - Template rendering with Jinja2
- [Sessions](sessions.md) - Session management
- [Middleware](middleware.md) - Using and creating middleware

### Features
- [API Documentation](api-docs.md) - Automatic API documentation at /.docs
- [WebSockets](websockets.md) - Real-time communication with WebSockets
- [WebSockets Advanced](websockets_advanced.md) - Advanced WebSocket features

### Performance and Reliability
- [Fast Mode](fast_mode.md) - Optimized request handling
- [Optimization](optimization.md) - Performance optimization techniques
- [Performance](performance.md) - Performance benchmarks and test results
- [Reliability](reliability.md) - Advanced reliability features

### Tools and Deployment
- [CLI](cli.md) - Command-line interface
- [Production Deployment](deployment.md) - Deploying to production
- [Advanced Features](advanced.md) - Advanced features and customization

### Summary
- [Summary](summary.md) - Overview of ProAPI features and capabilities