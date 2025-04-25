# Request and Response Handling in ProAPI

This guide explains how to work with HTTP requests and responses in ProAPI.

## The Request Object

The request object is passed to your route handlers and contains information about the HTTP request.

### Basic Request Properties

```python
@app.get("/example")
def example(request):
    # Access request properties
    method = request.method          # HTTP method (GET, POST, etc.)
    path = request.path              # URL path
    headers = request.headers        # HTTP headers
    query_params = request.query_params  # URL query parameters
    body = request.body              # Raw request body
    remote_addr = request.remote_addr  # Client IP address
    
    return {
        "method": method,
        "path": path,
        "headers": dict(headers),
        "query_params": dict(query_params),
        "remote_addr": remote_addr
    }
```

### Working with Query Parameters

```python
@app.get("/search")
def search(request):
    # Get a single query parameter
    query = request.get_query_param("q")
    
    # Get a query parameter with a default value
    limit = request.get_query_param("limit", 10)
    
    # Convert to appropriate type
    page = int(request.get_query_param("page", 1))
    
    return {
        "query": query,
        "limit": limit,
        "page": page
    }
```

### Working with Headers

```python
@app.get("/headers")
def headers_example(request):
    # Get a specific header
    user_agent = request.get_header("User-Agent")
    
    # Get a header with a default value
    content_type = request.get_header("Content-Type", "text/plain")
    
    return {
        "user_agent": user_agent,
        "content_type": content_type
    }
```

### Working with JSON Data

```python
@app.post("/json")
def json_example(request):
    # Access JSON data
    data = request.json
    
    # Process the data
    name = data.get("name")
    age = data.get("age")
    
    return {
        "received": {
            "name": name,
            "age": age
        }
    }
```

### Working with Form Data

```python
@app.post("/form")
def form_example(request):
    # Access form data
    data = request.form
    
    # Process the data
    name = data.get("name")
    email = data.get("email")
    
    return {
        "received": {
            "name": name,
            "email": email
        }
    }
```

## The Response Object

ProAPI automatically converts your return values to appropriate HTTP responses:

- Dictionaries are converted to JSON responses
- Strings are returned as HTML
- Custom Response objects give you full control

### Returning JSON

```python
@app.get("/json")
def json_response():
    return {
        "message": "This is JSON",
        "items": [1, 2, 3]
    }
```

### Returning HTML

```python
@app.get("/html")
def html_response():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ProAPI Example</title>
    </head>
    <body>
        <h1>ProAPI Example</h1>
        <p>This is a simple HTML response.</p>
    </body>
    </html>
    """
```

### Custom Responses

For more control, you can create a Response object:

```python
@app.get("/custom")
def custom_response():
    from proapi.server import Response
    
    return Response(
        body="Custom response body",
        status=200,
        headers={"X-Custom-Header": "Value"},
        content_type="text/plain"
    )
```

### Setting Cookies

```python
@app.get("/cookie")
def cookie_example():
    from proapi.server import Response
    
    response = Response(body="Cookie set!")
    response.set_cookie(
        name="session",
        value="abc123",
        max_age=3600,  # 1 hour
        path="/",
        secure=True,
        http_only=True
    )
    
    return response
```

### Status Codes

```python
@app.get("/status")
def status_example():
    from proapi.server import Response
    
    return Response(
        body={"message": "Created successfully"},
        status=201  # Created
    )
```

### Redirects

```python
@app.get("/redirect")
def redirect_example():
    from proapi.server import Response
    
    return Response(
        status=302,  # Found
        headers={"Location": "/destination"}
    )
```

### File Downloads

```python
@app.get("/download")
def download_example():
    from proapi.server import Response
    
    # Read file content
    with open("example.txt", "rb") as f:
        content = f.read()
    
    return Response(
        body=content,
        content_type="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=example.txt"
        }
    )
```

## Error Handling

```python
@app.get("/error")
def error_example():
    from proapi.server import Response
    
    # Return an error response
    return Response(
        body={"error": "Something went wrong"},
        status=500,
        content_type="application/json"
    )
```

### Common HTTP Status Codes

- 200: OK
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 405: Method Not Allowed
- 500: Internal Server Error