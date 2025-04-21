# API Documentation in ProAPI

ProAPI includes built-in support for generating API documentation using OpenAPI and Swagger UI. This guide explains how to enable and customize API documentation.

## Enabling API Documentation

API documentation is enabled by default at the `/docs` endpoint. You can customize this when creating your application:

```python
from proapi import ProAPI

app = ProAPI(
    enable_docs=True,       # Enable API documentation
    docs_url="/api-docs",   # URL path for API documentation
    docs_title="My API Documentation"  # Title for API documentation
)
```

## Accessing API Documentation

Once your application is running, you can access the API documentation at the configured URL (default: `/docs`). This will display a Swagger UI interface with your API endpoints.

ProAPI also provides a default documentation endpoint at `/.docs` that is always available, even if you disable the main documentation endpoint.

## Documenting Endpoints

ProAPI automatically generates documentation for your endpoints based on:

1. Route paths and HTTP methods
2. Function docstrings
3. Parameter types
4. Return values

### Using Docstrings

Use docstrings to provide descriptions for your endpoints:

```python
@app.get("/users/{user_id:int}")
def get_user(user_id):
    """
    Get a user by ID.
    
    Returns user information for the specified user ID.
    """
    return {"user_id": user_id, "name": f"User {user_id}"}
```

The first line of the docstring is used as the summary, and the entire docstring is used as the description.

### Path Parameters

Path parameters are automatically documented based on the route path:

```python
@app.get("/items/{item_id:int}")
def get_item(item_id):
    """Get an item by ID."""
    return {"item_id": item_id}
```

The documentation will show that `item_id` is an integer parameter.

### Request Bodies

For POST, PUT, and PATCH methods, the documentation automatically includes a request body:

```python
@app.post("/users")
def create_user(request):
    """
    Create a new user.
    
    Accepts user information and creates a new user.
    """
    return {"id": 1, **request.json}
```

### Response Schemas

The documentation includes default response schemas for common status codes:

- 200: Successful response
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Customizing Documentation

You can customize the documentation by providing additional information:

### Route Options

```python
@app.get("/users", name="list_users", description="Get a list of all users")
def get_users():
    return {"users": []}
```

### Security Schemes

The documentation includes a default API key security scheme:

```
X-API-Key: your-api-key
```

## OpenAPI Specification

ProAPI generates an OpenAPI 3.0.0 specification for your API. You can access the raw specification at `{docs_url}/json` (default: `/docs/json`).

The specification includes:

- API information (title, version, description)
- Server information
- Path information (endpoints, methods, parameters)
- Component schemas
- Security schemes

## Swagger UI

ProAPI uses Swagger UI to display the API documentation. The UI provides:

- Interactive documentation
- Request/response examples
- Try-it-out functionality
- Authentication support

## Disabling Documentation in Production

For security reasons, you might want to disable the public API documentation in production:

```python
from proapi import ProAPI

# Disable docs in production
app = ProAPI(
    env="production",
    enable_docs=False  # Docs will be disabled in production by default
)
```

Even with `enable_docs=False`, the default documentation at `/.docs` will still be available.

## Custom Documentation Middleware

You can create custom documentation middleware for more advanced use cases:

```python
from proapi.docs import DocsMiddleware

# Create custom docs middleware
custom_docs = DocsMiddleware(app, "/custom-docs", "Custom API Documentation")

# Add the middleware
app.use(custom_docs)
```

## Documentation Best Practices

1. Write clear and concise docstrings for all endpoints
2. Use typed path parameters to improve documentation
3. Consider security implications of exposing API documentation
4. Test the documentation to ensure it accurately represents your API
5. Keep documentation up-to-date as your API evolves