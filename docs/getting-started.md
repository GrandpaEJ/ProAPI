# Getting Started with ProAPI

This guide will help you get started with ProAPI, a lightweight Python web framework.

## Installation

Install ProAPI using pip:

```bash
pip install proapi
```

## Creating Your First Application

Create a new file called `app.py` with the following content:

```python
from proapi import ProAPI

# Create a new ProAPI application
app = ProAPI(debug=True)

# Define a route
@app.get("/")
def index():
    return {"message": "Hello, World!"}

# Run the application
if __name__ == "__main__":
    app.run()
```

## Running Your Application

Run your application with:

```bash
python app.py
```

Your application will be available at http://127.0.0.1:8000.

## Using the CLI

ProAPI comes with a command-line interface (CLI) that you can use to run your application:

```bash
python -m proapi run app.py
```

You can also create a new project with:

```bash
python -m proapi create myproject
```

## Application Configuration

When creating a ProAPI application, you can configure various options:

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

## Basic Routing

Define routes using decorators:

```python
# Basic route
@app.get("/")
def index():
    return {"message": "Welcome to ProAPI!"}

# Route with path parameter
@app.get("/hello/{name}")
def hello(name):
    return {"message": f"Hello, {name}!"}

# Route with typed path parameter
@app.get("/users/{user_id:int}")
def get_user(user_id):
    # user_id will be converted to an integer
    return {"user_id": user_id, "name": f"User {user_id}"}

# POST route with JSON body
@app.post("/echo")
def echo(request):
    return request.json
```

## Returning Responses

You can return various types of responses:

```python
# Return a dictionary (automatically converted to JSON)
@app.get("/json")
def json_example():
    return {"message": "This is JSON"}

# Return a string (automatically converted to HTML)
@app.get("/html")
def html_example():
    return "<h1>Hello, World!</h1>"

# Return a custom response
@app.get("/custom")
def custom_example():
    from proapi.server import Response
    return Response(
        body="Custom response",
        status=200,
        headers={"X-Custom-Header": "Value"},
        content_type="text/plain"
    )
```

## Next Steps

- Learn more about [routing](routing.md)
- Explore [request and response handling](request-response.md)
- Discover [template rendering](templates.md)
- Understand [middleware](middleware.md)