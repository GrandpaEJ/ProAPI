# Middleware in ProAPI

Middleware allows you to process requests and responses before and after they reach your route handlers. This guide explains how to use and create middleware in ProAPI.

## What is Middleware?

Middleware functions are executed in the order they are added to the application. Each middleware can:

1. Process the request and pass it to the next middleware
2. Short-circuit the request by returning a response
3. Add hooks to process the response after it's generated

## Adding Middleware

Use the `use` decorator to add middleware to your application:

```python
from proapi import ProAPI

app = ProAPI()

@app.use
def logging_middleware(request):
    print(f"Request: {request.method} {request.path}")
    return request
```

## Middleware Order

Middleware is executed in the order it's added to the application. The first middleware added is the first to process the request and the last to process the response.

## Built-in Middleware

ProAPI includes several built-in middleware functions:

### CORS Middleware

```python
from proapi.middleware import cors_middleware

app = ProAPI()

# Add CORS middleware
app.use(cors_middleware(
    allowed_origins="*",  # or ["https://example.com", "https://api.example.com"]
    allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowed_headers=["Content-Type", "Authorization"]
))
```

### Logging Middleware

```python
from proapi.middleware import logging_middleware

app = ProAPI()

# Add logging middleware
app.use(logging_middleware(
    log_format="[{time}] {method} {path} - {status} ({duration:.3f}s)",
    level="INFO"
))
```

### Static Files Middleware

```python
from proapi.middleware import static_files_middleware

app = ProAPI()

# Add static files middleware
app.use(static_files_middleware(
    static_dir="static",
    url_prefix="/static"
))
```

### Compression Middleware

```python
from proapi.middleware import compression_middleware

app = ProAPI()

# Add compression middleware
app.use(compression_middleware(
    min_size=1024,  # Minimum size for compression (bytes)
    level=6         # Compression level (1-9)
))
```

## Creating Custom Middleware

You can create custom middleware to add functionality to your application:

### Simple Middleware

```python
@app.use
def timing_middleware(request):
    import time
    
    # Store start time
    request.start_time = time.time()
    
    # Continue with request processing
    return request
```

### Middleware with Response Processing

```python
@app.use
def timing_middleware(request):
    import time
    
    # Store start time
    request.start_time = time.time()
    
    # Define a function to process the response
    def process_response(response):
        # Calculate request duration
        duration = time.time() - request.start_time
        
        # Add a custom header
        response.headers['X-Response-Time'] = f"{duration:.6f}s"
        
        return response
    
    # Store the function on the request object
    request.process_response = process_response
    
    # Continue with request processing
    return request
```

### Middleware that Short-circuits

```python
@app.use
def auth_middleware(request):
    from proapi.server import Response
    
    # Check for API key
    api_key = request.headers.get('X-API-Key')
    
    # Skip auth for public endpoints
    if request.path.startswith('/public'):
        return request
    
    # Require API key for other endpoints
    if not api_key:
        return Response(
            status=401,
            body={"error": "API key required"},
            content_type="application/json"
        )
    
    # Validate API key (simplified example)
    if api_key != "valid-api-key":
        return Response(
            status=403,
            body={"error": "Invalid API key"},
            content_type="application/json"
        )
    
    # Store user info on the request
    request.user = {"id": 1, "name": "API User"}
    
    # Continue with request processing
    return request
```

## Middleware Factory Pattern

You can create middleware factories that return middleware functions with specific configurations:

```python
def rate_limit_middleware(requests_per_minute=60, window_seconds=60):
    """
    Rate limiting middleware factory.
    
    Args:
        requests_per_minute: Maximum requests per minute
        window_seconds: Time window in seconds
    
    Returns:
        Middleware function
    """
    import time
    from collections import deque
    
    # Store request timestamps for each client
    client_requests = {}
    
    def middleware(request):
        from proapi.server import Response
        
        # Get client IP
        client_ip = request.remote_addr
        
        # Get current time
        current_time = time.time()
        
        # Initialize client request queue if needed
        if client_ip not in client_requests:
            client_requests[client_ip] = deque()
        
        # Remove old requests
        while (client_requests[client_ip] and 
               client_requests[client_ip][0] < current_time - window_seconds):
            client_requests[client_ip].popleft()
        
        # Check if client has exceeded rate limit
        if len(client_requests[client_ip]) >= requests_per_minute:
            return Response(
                status=429,
                body={"error": "Rate limit exceeded"},
                content_type="application/json",
                headers={
                    "Retry-After": str(window_seconds)
                }
            )
        
        # Add current request timestamp
        client_requests[client_ip].append(current_time)
        
        # Continue with request processing
        return request
    
    return middleware

# Usage
app.use(rate_limit_middleware(requests_per_minute=30))
```

## Combining Middleware

You can combine multiple middleware functions to create complex request processing pipelines:

```python
# Add middleware in the desired order
app.use(logging_middleware())
app.use(cors_middleware())
app.use(auth_middleware())
app.use(rate_limit_middleware())
app.use(compression_middleware())
```

## Middleware Best Practices

1. Keep middleware functions focused on a single responsibility
2. Order middleware carefully based on dependencies
3. Use middleware factories for configurable middleware
4. Document middleware behavior and requirements
5. Handle errors gracefully in middleware
6. Be mindful of performance implications