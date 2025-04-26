# Custom Response Handling in ProAPI

ProAPI provides flexible ways to return different types of responses from your route handlers. This guide explains how to create and use custom responses for various content types.

## Basic Response Types

By default, ProAPI automatically converts your return values to appropriate HTTP responses:

- **Dictionaries** are converted to JSON responses with `Content-Type: application/json`
- **Strings** are returned as HTML with `Content-Type: text/html`
- **Custom Response objects** give you full control over the response

## Creating Custom Responses

For more control over your responses, you can use the `Response` class from `proapi.server`:

```python
from proapi.server import Response

@app.get("/custom")
def custom_response(request):
    return Response(
        body="Custom response body",
        status=200,
        headers={"X-Custom-Header": "Value"},
        content_type="text/plain"
    )
```

## Common Response Types

### HTML Response

There are two ways to return HTML content from your route handlers:

#### Method 1: Direct String Return

The simplest way is to return an HTML string directly:

```python
@app.get("/html")
def html_response(request):
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

#### Method 2: Using Response Class

For more control over the response, you can use the Response class with an explicit content type:

```python
@app.get("/html")
def html_response(request):
    from proapi.server import Response

    html = """
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

    return Response(body=html, content_type="text/html")
```

#### Important Note on Path Names

Some path names may have special handling in the framework. For example, the "/register" path has been observed to have issues when returning HTML content directly. In such cases, you have two options:

1. Use the Response class with an explicit content_type:

```python
@app.get("/register")
def register_page(request):
    from proapi.server import Response

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register</title>
    </head>
    <body>
        <h1>Register</h1>
        <form method="post" action="/register">
            <!-- Form fields -->
        </form>
    </body>
    </html>
    """

    return Response(body=html, content_type="text/html")
```

2. Use a slightly different path name:

```python
@app.get("/signup")  # Alternative to "/register"
def signup_page(request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register</title>
    </head>
    <body>
        <h1>Register</h1>
        <form method="post" action="/register">
            <!-- Form fields -->
        </form>
    </body>
    </html>
    """
```

### Plain Text Response

```python
@app.get("/text")
def text_response(request):
    from proapi.server import Response

    return Response(
        body="This is a plain text response from ProAPI.",
        content_type="text/plain"
    )
```

### JSON Response

While dictionaries are automatically converted to JSON, you can also create a JSON response explicitly:

```python
@app.get("/json")
def json_response(request):
    from proapi.server import Response

    return Response(
        body={"message": "This is JSON"},
        content_type="application/json"
    )
```

Or use the `jsonify` helper function:

```python
@app.get("/json")
def json_response(request):
    from proapi.helpers import jsonify

    return jsonify({"message": "This is JSON"})
```

### Redirect Response

To redirect to another URL, use the `redirect` function from `proapi.utils`:

```python
@app.get("/redirect")
def redirect_response(request):
    from proapi.utils import redirect

    return redirect("/destination")
```

### Error Response

To return an error response, set the appropriate status code:

```python
@app.get("/error")
def error_response(request):
    from proapi.server import Response

    return Response(
        body={"error": "This is an error response"},
        status=500,
        content_type="application/json"
    )
```

## Setting Cookies

```python
@app.get("/cookie")
def cookie_example(request):
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

## File Downloads

```python
@app.get("/download")
def download_example(request):
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

## Common HTTP Status Codes

- **200**: OK - The request was successful
- **201**: Created - The request was successful and a resource was created
- **204**: No Content - The request was successful but there is no content to return
- **400**: Bad Request - The request was malformed or invalid
- **401**: Unauthorized - Authentication is required
- **403**: Forbidden - The client does not have permission to access the resource
- **404**: Not Found - The requested resource was not found
- **405**: Method Not Allowed - The HTTP method is not supported for this resource
- **500**: Internal Server Error - An error occurred on the server

## Best Practices

1. **Be explicit about content types** - Always specify the content type for custom responses
2. **Use appropriate status codes** - Choose the correct HTTP status code for your response
3. **Set appropriate headers** - Include relevant headers for your response type
4. **Handle errors gracefully** - Return meaningful error messages with appropriate status codes
5. **Use helper functions** - Utilize the built-in helper functions for common response types
