# HTML Response Handling in ProAPI

ProAPI provides multiple ways to return HTML content from your route handlers. This guide explains the different methods and best practices for returning HTML responses.

## Methods for Returning HTML Content

### Method 1: Direct String Return

The simplest way to return HTML content is to return an HTML string directly from your route handler:

```python
@app.get("/page")
def page(request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ProAPI Example</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
        </style>
    </head>
    <body>
        <h1>ProAPI Example</h1>
        <p>This is a simple HTML response.</p>
    </body>
    </html>
    """
```

This method is simple and works well for most routes. ProAPI automatically detects that you're returning an HTML string and sets the appropriate content type.

### Method 2: Using Response Class

For more control over the response, you can use the `Response` class with an explicit content type:

```python
from proapi.server.server import Response

@app.get("/page")
def page(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ProAPI Example</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
        </style>
    </head>
    <body>
        <h1>ProAPI Example</h1>
        <p>This is a simple HTML response.</p>
    </body>
    </html>
    """
    
    return Response(
        status=200,
        body=html,
        content_type="text/html"
    )
```

This method gives you more control over the response, allowing you to set the status code, headers, and content type explicitly.

### Method 3: Using Template Rendering

For more complex pages, you can use template rendering with Jinja2:

```python
from proapi import render

@app.get("/page")
def page(request):
    return render(
        "page.html",
        title="ProAPI Example",
        message="This is a simple HTML response."
    )
```

This method is recommended for complex pages that require dynamic content.

## Special Considerations for Certain Routes

Some route paths may have special handling in the framework. For example, the "/register" path has been observed to have issues when returning HTML content directly.

### Issues with "/register" Path

When using the "/register" path, you may encounter issues when returning HTML content directly. This is due to special handling of this path in the framework.

#### Solution 1: Use Response Class

```python
@app.get("/register")
def register_page(request):
    from proapi.server.server import Response
    
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
    
    return Response(
        status=200,
        body=html,
        content_type="text/html"
    )
```

#### Solution 2: Use a Different Path

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

## Best Practices

1. **Use Direct String Return for Simple Pages**: For simple pages, returning an HTML string directly is the simplest approach.

2. **Use Response Class for Complex Responses**: When you need more control over the response, use the `Response` class with an explicit content type.

3. **Use Template Rendering for Complex Pages**: For pages with dynamic content, use template rendering with Jinja2.

4. **Be Aware of Special Paths**: Some paths may have special handling in the framework. If you encounter issues with a specific path, try using the `Response` class or a different path.

5. **Set Explicit Content Type**: When using the `Response` class, always set the content type explicitly to "text/html" for HTML responses.

## Examples

### Login Page Example

```python
@app.get("/login")
def login_page(request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input { width: 300px; padding: 8px; border: 1px solid #ddd; }
            button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; }
        </style>
    </head>
    <body>
        <h1>Login</h1>
        <form method="post" action="/login">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """
```

### Registration Page Example

```python
@app.get("/signup")
def signup_page(request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input { width: 300px; padding: 8px; border: 1px solid #ddd; }
            button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; }
        </style>
    </head>
    <body>
        <h1>Register</h1>
        <form method="post" action="/register">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="confirm_password">Confirm Password:</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="/login">Login</a></p>
    </body>
    </html>
    """
```

### Dashboard Page Example with Template Rendering

```python
@app.get("/dashboard")
@login_required
def dashboard(request):
    return render(
        "dashboard.html",
        title="Dashboard",
        user=current_user,
        items=[
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]
    )
```

## Troubleshooting

If you encounter issues with HTML responses:

1. **Check the Content Type**: Make sure the content type is set correctly to "text/html".

2. **Try Using the Response Class**: If direct string return doesn't work, try using the `Response` class with an explicit content type.

3. **Try a Different Path**: If a specific path is causing issues, try using a different path.

4. **Check for Special Characters**: Make sure your HTML doesn't contain special characters that could be interpreted as control characters.

5. **Check for Syntax Errors**: Make sure your HTML is valid and doesn't contain syntax errors.
