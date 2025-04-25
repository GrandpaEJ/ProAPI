# API Documentation in ProAPI

ProAPI includes built-in support for generating API documentation using OpenAPI and Swagger UI. This guide explains how to use and customize API documentation.

## Automatic API Documentation

API documentation is enabled by default at the `/.docs` endpoint. You don't need to do anything special to enable it:

```python
from proapi import ProAPI

# Documentation is automatically available at /.docs
app = ProAPI()
```

You can customize the documentation URL and title if needed:

```python
from proapi import ProAPI

app = ProAPI(
    enable_docs=True,       # Already true by default
    docs_url="/api-docs",   # Change from default /.docs
    docs_title="My API Documentation"  # Custom title for documentation
)
```

## Accessing API Documentation

Once your application is running, you can access the API documentation at the configured URL (default: `/.docs`). This will display a Swagger UI interface with your API endpoints.

The documentation URL is shown in the console when you start your application:

```
ProAPI server starting at http://127.0.0.1:8000
Environment: DEVELOPMENT
Debug mode: ON
Fast mode: ON
Workers: 1
API Documentation: http://127.0.0.1:8000/.docs
```

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

ProAPI generates an OpenAPI 3.0.0 specification for your API. You can access the raw specification at `{docs_url}/json` (default: `/.docs/json`).

This JSON specification can be used with other OpenAPI tools and clients.

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

## Documentation in Production

By default, API documentation is enabled in all environments, including production. This makes it easy for developers to explore and understand your API.

If you want to disable documentation in production for security reasons:

```python
from proapi import ProAPI

# Disable docs in production
app = ProAPI(
    env="production",
    enable_docs=False  # Explicitly disable documentation
)
```

You can also protect the documentation with authentication middleware to ensure only authorized users can access it.

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