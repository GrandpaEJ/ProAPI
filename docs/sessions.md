# Sessions in ProAPI

ProAPI includes built-in support for session management, allowing you to store user-specific data across requests. This guide explains how to enable and use sessions in your application.

## Enabling Sessions

Sessions are disabled by default. To enable sessions, set the `enable_sessions` parameter when creating your application:

```python
from proapi import ProAPI

app = ProAPI(
    enable_sessions=True,
    session_secret_key="your-secret-key-here"  # Use a secure random key in production
)
```

## Session Configuration Options

ProAPI provides several options for configuring sessions:

| Option | Description | Default |
|--------|-------------|---------|
| `enable_sessions` | Enable session support | `False` |
| `session_secret_key` | Secret key for signing session cookies | Random key (not persistent) |
| `session_cookie_name` | Name of the session cookie | `"session"` |
| `session_max_age` | Maximum age of the session in seconds | `3600` (1 hour) |
| `session_secure` | Whether the session cookie is secure | `True` in production, `False` otherwise |
| `session_http_only` | Whether the session cookie is HTTP-only | `True` |
| `session_same_site` | SameSite cookie attribute | `"Lax"` |
| `session_backend` | Session storage backend | `"memory"` |
| `session_backend_options` | Additional options for the session backend | `{}` |

## Session Storage Backends

ProAPI supports multiple session storage backends:

### Memory Backend

The memory backend stores sessions in memory. Sessions are lost when the server restarts.

```python
app = ProAPI(
    enable_sessions=True,
    session_secret_key="your-secret-key",
    session_backend="memory"
)
```

### File Backend

The file backend stores sessions in files. Sessions persist across server restarts.

```python
app = ProAPI(
    enable_sessions=True,
    session_secret_key="your-secret-key",
    session_backend="file",
    session_backend_options={
        "directory": "sessions"  # Directory to store session files
    }
)
```

## Using Sessions

Once sessions are enabled, you can access the session object through the request:

```python
@app.get("/")
def index(request):
    # Get a value from the session
    user_id = request.session.get("user_id")
    
    # Set a value in the session
    request.session["last_visit"] = time.time()
    
    return {"user_id": user_id}
```

## Session Methods

The session object provides several methods for working with session data:

### Getting Values

```python
# Get a value with a default
value = request.session.get("key", "default")

# Get a value using dictionary syntax
value = request.session["key"]  # Raises KeyError if not found
```

### Setting Values

```python
# Set a value using dictionary syntax
request.session["key"] = "value"

# Update multiple values
request.session.update({"key1": "value1", "key2": "value2"})
```

### Deleting Values

```python
# Delete a value
del request.session["key"]

# Remove a value and return it
value = request.session.pop("key", "default")

# Clear all values
request.session.clear()
```

### Checking for Keys

```python
if "key" in request.session:
    # Key exists
    pass
```

## Session Lifecycle

Sessions are automatically created, retrieved, and saved by the session middleware. The session cookie is set on the first request and used to identify the session on subsequent requests.

## Example: User Authentication

Here's a simple example of using sessions for user authentication:

```python
@app.post("/login")
def login(request):
    username = request.json.get("username")
    password = request.json.get("password")
    
    # Check credentials (in a real app, you'd check against a database)
    if username == "admin" and password == "password":
        # Store user info in session
        request.session["user_id"] = 1
        request.session["username"] = username
        request.session["is_authenticated"] = True
        
        return {"message": "Login successful"}
    else:
        return {"error": "Invalid credentials"}

@app.get("/profile")
def profile(request):
    # Check if user is authenticated
    if not request.session.get("is_authenticated", False):
        from proapi.server import Response
        return Response(
            status=302,  # Redirect
            headers={"Location": "/login"}
        )
    
    # User is authenticated, return profile
    return {
        "user_id": request.session["user_id"],
        "username": request.session["username"]
    }

@app.post("/logout")
def logout(request):
    # Clear the session
    request.session.clear()
    
    return {"message": "Logout successful"}
```

## Security Considerations

1. **Secret Key**: Use a strong, random secret key in production. The secret key is used to sign session cookies to prevent tampering.

2. **Secure Cookies**: In production, ensure that session cookies are secure by setting `session_secure=True`. This ensures that cookies are only sent over HTTPS.

3. **HTTP-Only Cookies**: Keep `session_http_only=True` to prevent JavaScript from accessing the session cookie, which helps protect against cross-site scripting (XSS) attacks.

4. **SameSite Attribute**: The `session_same_site` option helps protect against cross-site request forgery (CSRF) attacks. The default value `"Lax"` is a good balance between security and usability.

5. **Session Data**: Don't store sensitive information in sessions. If you need to store sensitive data, consider encrypting it.

6. **Session Expiration**: Set an appropriate `session_max_age` value to limit the lifetime of sessions.

## Performance Considerations

1. **Memory Backend**: The memory backend is faster but doesn't persist across server restarts. It's suitable for development and small applications.

2. **File Backend**: The file backend is slower but persists across server restarts. It's suitable for production applications where session persistence is important.

3. **Session Size**: Keep session data small to minimize overhead. Store only what you need in the session.

4. **Session Cleanup**: Sessions are automatically cleaned up when they expire, but you may want to periodically clean up old session files if using the file backend in a long-running application.
