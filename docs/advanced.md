# Advanced Features in ProAPI

This guide covers advanced features and customization options in ProAPI.

## Async Support

ProAPI supports async route handlers for improved performance with I/O-bound operations:

```python
from proapi import ProAPI

app = ProAPI()

@app.get("/async")
async def async_route():
    # Simulate async operation
    import asyncio
    await asyncio.sleep(0.1)
    
    return {"message": "Async route"}
```

### Mixing Sync and Async

You can mix synchronous and asynchronous route handlers in the same application:

```python
@app.get("/sync")
def sync_route():
    return {"message": "Sync route"}

@app.get("/async")
async def async_route():
    return {"message": "Async route"}
```

### Async with External Libraries

Use async libraries for improved performance:

```python
@app.get("/users/{user_id:int}")
async def get_user(user_id):
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/users/{user_id}") as response:
            data = await response.json()
            
    return data
```

## Cython Compilation

ProAPI supports Cython compilation for improved performance:

```bash
pip install cython
```

Compile your application:

```bash
python -m proapi run app.py --compile
```

### Manual Compilation

You can also compile your application manually:

```python
from proapi.cython_ext import compile_app

compile_app("app.py")
```

## Port Forwarding

ProAPI supports port forwarding to expose your application to the internet:

```python
app.run(
    forward=True,
    forward_type="ngrok"  # "ngrok", "cloudflare", or "localtunnel"
)
```

### Cloudflare Tunnels

Use Cloudflare Tunnels for secure port forwarding:

```python
app.run(
    forward=True,
    forward_type="cloudflare",
    forward_kwargs={
        "token": "your-cloudflare-tunnel-token"
    }
)
```

## Custom JSON Encoders

You can provide a custom JSON encoder for your application:

```python
import json
import datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

app = ProAPI(json_encoder=CustomJSONEncoder)
```

## Route Groups

You can create route groups with a common prefix:

```python
# Create a sub-application
api_v1 = ProAPI()

# Define routes on the sub-application
@api_v1.get("/users")
def get_users_v1():
    return {"version": "v1", "users": []}

# Create another sub-application
api_v2 = ProAPI()

# Define routes on the sub-application
@api_v2.get("/users")
def get_users_v2():
    return {"version": "v2", "users": []}

# Mount the sub-applications with prefixes
app.use(api_v1, prefix="/api/v1")
app.use(api_v2, prefix="/api/v2")
```

## Custom Middleware

Create advanced middleware for complex use cases:

```python
def jwt_auth_middleware(secret_key, algorithm="HS256"):
    """
    JWT authentication middleware.
    
    Args:
        secret_key: Secret key for JWT verification
        algorithm: JWT algorithm
    
    Returns:
        Middleware function
    """
    import jwt
    from proapi.server import Response
    
    def middleware(request):
        # Skip auth for public endpoints
        if request.path.startswith('/public'):
            return request
        
        # Get authorization header
        auth_header = request.headers.get('Authorization', '')
        
        # Check if it's a Bearer token
        if not auth_header.startswith('Bearer '):
            return Response(
                status=401,
                body={"error": "Authorization header must start with 'Bearer'"},
                content_type="application/json"
            )
        
        # Extract token
        token = auth_header[7:]
        
        try:
            # Verify and decode token
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            
            # Store user info on the request
            request.user = payload
            
            return request
        except jwt.ExpiredSignatureError:
            return Response(
                status=401,
                body={"error": "Token expired"},
                content_type="application/json"
            )
        except jwt.InvalidTokenError:
            return Response(
                status=401,
                body={"error": "Invalid token"},
                content_type="application/json"
            )
    
    return middleware

# Usage
app.use(jwt_auth_middleware("your-secret-key"))
```

## Custom Response Processing

You can customize how responses are processed:

```python
# Store original _process_result method
original_process_result = app._process_result

# Define custom processing function
def custom_process_result(result):
    # Get the original response
    response = original_process_result(result)
    
    # Add custom headers
    response.headers['X-Powered-By'] = 'ProAPI'
    response.headers['X-Version'] = '1.0.0'
    
    return response

# Replace the method
app._process_result = custom_process_result
```

## WebSockets Support

Add WebSocket support to your application:

```python
import asyncio
import json

# Store connected clients
clients = set()

@app.websocket("/ws")
async def websocket_handler(websocket):
    # Add client to set
    clients.add(websocket)
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_text()
            
            # Parse message
            data = json.loads(message)
            
            # Broadcast message to all clients
            for client in clients:
                await client.send_text(json.dumps({
                    "type": "message",
                    "data": data
                }))
    finally:
        # Remove client from set
        clients.remove(websocket)
```

## Custom Error Handlers

Register custom error handlers for specific status codes:

```python
@app.error_handler(404)
def not_found_handler(request, exception):
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "path": request.path
    }

@app.error_handler(500)
def server_error_handler(request, exception):
    # Log the error
    app_logger.error(f"Server error: {exception}")
    
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }
```

## Background Tasks

Run background tasks:

```python
import threading
import time

def background_task():
    while True:
        # Perform background work
        print("Background task running...")
        time.sleep(60)

# Start background task
threading.Thread(target=background_task, daemon=True).start()
```

## Custom CLI Commands

Extend the CLI with custom commands:

```python
from proapi.cli import main

# Add a custom command
def custom_command(args):
    print(f"Running custom command with args: {args}")

# Register the command
main.subparsers.add_parser("custom", help="Custom command")
main.commands["custom"] = custom_command
```

## Environment-Specific Configuration

Load configuration based on the environment:

```python
import os

# Determine environment
env = os.environ.get("PROAPI_ENV", "development")

# Load environment-specific configuration
if env == "development":
    from config.development import config
elif env == "production":
    from config.production import config
elif env == "testing":
    from config.testing import config
else:
    from config.default import config

# Create application with configuration
app = ProAPI(**config)
```

## Custom Template Filters

Add custom filters to Jinja2 templates:

```python
import markdown
from proapi.templating import _jinja_env

# Add markdown filter
_jinja_env.filters['markdown'] = lambda text: markdown.markdown(text)

# Usage in template: {{ content|markdown }}
```

## Database Integration

Integrate with databases:

```python
import sqlite3

# Create a database connection
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

@app.get("/users")
def get_users():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = [dict(user) for user in cursor.fetchall()]
    return {"users": users}

@app.post("/users")
def create_user(request):
    user_data = request.json
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (user_data['name'], user_data['email'])
    )
    conn.commit()
    return {"id": cursor.lastrowid, **user_data}
```

## Custom Decorators

Create custom decorators for route handlers:

```python
import functools

def require_auth(f):
    @functools.wraps(f)
    def wrapper(request, *args, **kwargs):
        from proapi.server import Response
        
        # Check if user is authenticated
        if not hasattr(request, 'user'):
            return Response(
                status=401,
                body={"error": "Authentication required"},
                content_type="application/json"
            )
        
        return f(request, *args, **kwargs)
    
    return wrapper

# Usage
@app.get("/protected")
@require_auth
def protected_route(request):
    return {"message": "Protected route", "user": request.user}
```