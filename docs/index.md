# ProAPI Documentation

ProAPI is a lightweight, beginner-friendly yet powerful Python web framework. It provides a simple and intuitive API for building web applications and APIs.

## Features

- **Decorator-based routing** - Define routes with simple decorators like `@app.get()`, `@app.post()`, etc.
- **Simple template rendering** - Render templates with Jinja2
- **Easy server startup** - Start your server with a simple `app.run()`
- **Async support** - Optional async support for high-performance applications
- **Cython-based compilation** - Optional Cython-based compilation for speed
- **Minimal dependencies** - Keep your project lightweight
- **Built-in JSON support** - Automatic JSON serialization and deserialization
- **Middleware system** - Add middleware for request/response processing
- **Automatic API documentation** - Generate API documentation with Swagger UI
- **Structured logging** - Built-in logging with Loguru
- **CLI commands** - Command-line interface for common tasks

## Installation

```bash
pip install proapi
```

## Quick Start

```python
from proapi import ProAPI

app = ProAPI()

@app.get("/")
def index():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run()
```

## Documentation Sections

- [Getting Started](getting-started.md) - Basic usage and concepts
- [Routing](routing.md) - URL routing and path parameters
- [Request and Response](request-response.md) - Working with HTTP requests and responses
- [Templates](templates.md) - Template rendering with Jinja2
- [Middleware](middleware.md) - Using and creating middleware
- [API Documentation](api-docs.md) - Automatic API documentation
- [CLI](cli.md) - Command-line interface
- [Production Deployment](deployment.md) - Deploying to production
- [Advanced Features](advanced.md) - Advanced features and customization