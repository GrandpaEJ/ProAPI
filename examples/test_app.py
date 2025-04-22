"""
Example ProAPI application with session support.

This is a simple example of how to use the ProAPI framework with sessions.
"""

import sys
import os

# Add parent directory to path to import local proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, render, redirect, jsonify
from proapi.session_proxy import session
from proapi.request_proxy import request

# Create the application with session support
app = ProAPI(debug=True, enable_sessions=True, session_secret_key="test-secret-key")

# Define routes

@app.get("/")
def index():
    """Home page."""
    # Get visit count from session or initialize to 0
    visit_count = session.get("visit_count", 0)

    # Increment visit count
    visit_count += 1

    # Store updated visit count in session
    session["visit_count"] = visit_count

    return {
        "message": "Welcome to ProAPI with Sessions!",
        "description": "A lightweight, beginner-friendly yet powerful Python web framework.",
        "visit_count": visit_count,
        "user_agent": request.headers.get("User-Agent", "Unknown"),
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This endpoint"},
            {"path": "/hello/{name}", "method": "GET", "description": "Get a personalized greeting"},
            {"path": "/json", "method": "POST", "description": "Echo JSON data"},
            {"path": "/html", "method": "GET", "description": "HTML example"},
            {"path": "/login", "method": "GET", "description": "Login page"},
            {"path": "/admin", "method": "GET", "description": "Admin page (requires login)"},
            {"path": "/logout", "method": "GET", "description": "Logout"}
        ]
    }

@app.get("/hello/{name}")
def hello(name):
    """Get a personalized greeting."""
    # Get the previous names from session or initialize to empty list
    previous_names = session.get("previous_names", [])

    # Add the current name if it's not already in the list
    if name not in previous_names:
        previous_names.append(name)
        session["previous_names"] = previous_names

    return {
        "message": f"Hello, {name}!",
        "previous_names": previous_names
    }

@app.post("/json")
def json_handler():
    """Echo JSON data."""
    return jsonify({
        "received": request.json,
        "message": "JSON data received successfully",
        "session_data": {k: v for k, v in session.data.items()}
    })

@app.get("/html")
def html_example():
    """HTML example."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ProAPI Example</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <h1>ProAPI Example</h1>
        <p>This is a simple HTML response from ProAPI.</p>

        <h2>Example Code:</h2>
        <pre>
from proapi import ProAPI, session

app = ProAPI(enable_sessions=True)

@app.get("/")
def index():
    visit_count = session.get("visit_count", 0)
    session["visit_count"] = visit_count + 1
    return {"visit_count": visit_count + 1}

if __name__ == "__main__":
    app.run()
        </pre>
    </body>
    </html>
    """

# Login routes
@app.get("/login")
def login():
    """Login page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - ProAPI Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            input[type="text"],
            input[type="password"] {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
            .error {
                color: red;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <h1>Login</h1>

        <div class="content">
            <h2>Login to Your Account</h2>

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

            <p><small>Hint: Use "admin" / "password" to login</small></p>
        </div>
    </body>
    </html>
    """

@app.post("/login")
def login_submit():
    """Process login form."""
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "admin" and password == "password":
        session["username"] = username
        return redirect("/admin")
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Failed</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #333;
                }
                .error {
                    color: red;
                    margin-bottom: 15px;
                }
            </style>
        </head>
        <body>
            <h1>Login Failed</h1>
            <div class="error">Invalid username or password.</div>
            <p><a href="/login">Try again</a></p>
        </body>
        </html>
        """

@app.get("/admin")
def admin():
    """Admin page."""
    if "username" not in session:
        return redirect("/login")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - ProAPI Test</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #333;
            }}
            .dashboard {{
                margin-top: 20px;
            }}
            .dashboard-item {{
                background-color: white;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .logout {{
                display: inline-block;
                background-color: #cc0000;
                color: white;
                text-decoration: none;
                padding: 8px 15px;
                border-radius: 4px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Admin Dashboard</h1>

        <div class="content">
            <h2>Welcome, {session["username"]}!</h2>
            <p>You are logged in to the admin dashboard.</p>

            <div class="dashboard">
                <div class="dashboard-item">
                    <h3>Session Data</h3>
                    <pre>{str(session.data)}</pre>
                </div>
            </div>

            <a href="/logout" class="logout">Logout</a>
        </div>
    </body>
    </html>
    """

@app.get("/logout")
def logout():
    """Logout."""
    session.clear()
    return redirect("/")

# Add middleware for logging
@app.use
def logging_middleware(request):
    """Log requests."""
    print(f"Request: {request.method} {request.path}")
    return request

# Import necessary modules
import json
import time
import traceback
from urllib.parse import parse_qs

# Import ProAPI modules at module level to avoid repeated imports
from proapi.server import Request
from proapi.request_proxy import set_current_request, clear_current_request

# Create a cache for common responses
CACHE_SIZE = 100
CACHE_TTL = 5  # seconds

# Response cache
response_cache = {}

# Cache helper functions
def get_cache_key(method, path, query_string):
    """Generate a cache key from request details."""
    return f"{method}:{path}:{query_string}"

def get_cached_response(key):
    """Get a cached response if it exists and is not expired."""
    if key in response_cache:
        timestamp, response = response_cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return response
        # Remove expired cache entry
        del response_cache[key]
    return None

def cache_response(key, response):
    """Cache a response with the current timestamp."""
    # Limit cache size by removing oldest entries if needed
    if len(response_cache) >= CACHE_SIZE:
        oldest_key = min(response_cache.keys(), key=lambda k: response_cache[k][0])
        del response_cache[oldest_key]

    response_cache[key] = (time.time(), response)

# Optimized ASGI application
async def asgi_app(scope, receive, send):
    """
    High-performance ASGI application optimized for speed and stability.

    Args:
        scope: ASGI scope
        receive: ASGI receive function
        send: ASGI send function
    """
    # Handle lifespan protocol messages (startup/shutdown)
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                # Initialize any resources here
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                # Clean up any resources here
                await send({"type": "lifespan.shutdown.complete"})
                break
        return

    # Only handle HTTP requests
    if scope["type"] != "http":
        await send({
            "type": "http.response.start",
            "status": 501,  # Not Implemented
            "headers": [(b"content-type", b"application/json")]
        })
        await send({
            "type": "http.response.body",
            "body": b'{"error": "Only HTTP requests are supported"}'
        })
        return

    # Extract basic request info
    method = scope["method"]
    path = scope["path"]
    query_string = scope.get("query_string", b"")

    # Check cache for GET requests (only cache GET requests)
    if method == "GET" and app.debug is False:
        cache_key = get_cache_key(method, path, query_string)
        cached = get_cached_response(cache_key)
        if cached:
            # Use cached response
            status, headers, body = cached
            await send({
                "type": "http.response.start",
                "status": status,
                "headers": headers
            })
            await send({
                "type": "http.response.body",
                "body": body
            })
            return

    try:
        # Extract headers efficiently (only decode what's needed)
        headers = {}
        for k, v in scope["headers"]:
            # Only decode headers we actually need
            key = k.decode("utf-8").lower()
            if key in ("content-type", "content-length", "cookie", "user-agent", "accept"):
                headers[key] = v.decode("utf-8")

        # Parse query parameters efficiently
        query_params = {}
        if query_string:
            parsed_qs = parse_qs(query_string.decode("utf-8"))
            for k, v in parsed_qs.items():
                query_params[k] = v[0] if len(v) == 1 else v

        # Get client address
        client_address = scope.get("client", ("127.0.0.1", 0))[0]

        # Read request body with optimized handling
        body = b""
        max_size = 10 * 1024 * 1024  # 10MB limit

        message = await receive()
        if message["type"] == "http.request":
            body = message.get("body", b"")

            # Fast path for small bodies (most common case)
            if len(body) < max_size and message.get("more_body", False):
                # Efficient body collection for larger requests
                chunks = [body]
                total_size = len(body)

                while True:
                    message = await receive()
                    chunk = message.get("body", b"")
                    total_size += len(chunk)

                    if total_size > max_size:
                        # Payload too large
                        await send({
                            "type": "http.response.start",
                            "status": 413,
                            "headers": [(b"content-type", b"application/json")]
                        })
                        await send({
                            "type": "http.response.body",
                            "body": b'{"error": "Request body too large"}'
                        })
                        return

                    chunks.append(chunk)
                    if not message.get("more_body", False):
                        break

                # Join chunks only once at the end
                body = b"".join(chunks)

        # Create and process the request
        req = Request(
            method=method,
            path=path,
            headers=headers,
            query_params=query_params,
            body=body,
            remote_addr=client_address
        )

        try:
            # Set the current request in the request proxy
            set_current_request(req)

            # Process the request
            response = app.handle_request(req)

            # Prepare response headers
            resp_headers = []
            for k, v in response.headers.items():
                k_bytes = k.encode("utf-8")
                if isinstance(v, list):
                    for item in v:
                        resp_headers.append((k_bytes, str(item).encode("utf-8")))
                else:
                    resp_headers.append((k_bytes, str(v).encode("utf-8")))

            # Prepare response body
            if isinstance(response.body, str):
                resp_body = response.body.encode("utf-8")
            elif isinstance(response.body, bytes):
                resp_body = response.body
            else:
                resp_body = str(response.body).encode("utf-8")

            # Cache successful GET responses
            if method == "GET" and response.status == 200 and app.debug is False:
                cache_key = get_cache_key(method, path, query_string)
                cache_response(cache_key, (response.status, resp_headers, resp_body))

            # Send response
            await send({
                "type": "http.response.start",
                "status": response.status,
                "headers": resp_headers
            })

            # Optimize sending large responses
            if len(resp_body) > 1024 * 1024:  # 1MB
                # Send in 1MB chunks
                chunk_size = 1024 * 1024
                for i in range(0, len(resp_body), chunk_size):
                    chunk = resp_body[i:i+chunk_size]
                    more = i + chunk_size < len(resp_body)
                    await send({
                        "type": "http.response.body",
                        "body": chunk,
                        "more_body": more
                    })
            else:
                # Send small responses in one go
                await send({
                    "type": "http.response.body",
                    "body": resp_body
                })

        finally:
            # Always clean up
            clear_current_request()

    except Exception as e:
        # Optimized error handling
        error_msg = str(e)
        error_traceback = traceback.format_exc() if app.debug else ""

        # Prepare error response
        error_body = {"error": "Internal Server Error"}
        if app.debug:
            error_body["detail"] = error_msg
            error_body["traceback"] = error_traceback

        error_json = json.dumps(error_body).encode("utf-8")

        # Send error response
        await send({
            "type": "http.response.start",
            "status": 500,
            "headers": [(b"content-type", b"application/json")]
        })

        await send({
            "type": "http.response.body",
            "body": error_json
        })

# This is the ASGI application that uvicorn will use
application = asgi_app

# Run the application
if __name__ == "__main__":
    import uvicorn
    import platform
    import os
    import psutil

    # Get system information for optimal configuration
    cpu_count = os.cpu_count() or 1
    memory_gb = psutil.virtual_memory().total / (1024 * 1024 * 1024)

    # Calculate optimal settings based on system resources
    if platform.system() == "Windows":
        # Windows optimization
        worker_count = 1  # Windows performs better with a single worker
        concurrency_per_worker = min(30, int(memory_gb * 5))  # 5 connections per GB, max 30
        backlog = 100  # Connection queue size
        keep_alive = 2  # Short keep-alive to free connections quickly

        print(f"\n[OPTIMIZED CONFIG] Windows mode with {worker_count} worker")
        print(f"[OPTIMIZED CONFIG] Memory: {memory_gb:.1f}GB, Concurrency: {concurrency_per_worker} per worker")
        print(f"[OPTIMIZED CONFIG] Total max connections: {concurrency_per_worker}")

        # Run with Windows-optimized settings
        uvicorn.run(
            "test_app:application",
            host="127.0.0.1",
            port=8000,
            reload=True,
            loop="asyncio",
            workers=worker_count,
            limit_concurrency=concurrency_per_worker,
            backlog=backlog,
            # Use a very high value instead of 0 to avoid termination
            limit_max_requests=1000000,  # Very high value to effectively disable restarts
            timeout_keep_alive=keep_alive,
            log_level="warning",  # Minimal logging
            access_log=False,      # No access logs
            use_colors=False,      # Disable colors for less overhead
            http="h11"            # Use h11 for Windows compatibility
        )
    else:
        # Unix optimization
        worker_count = min(cpu_count, 4)  # Use up to 4 workers (diminishing returns after that)
        concurrency_per_worker = min(100, int(memory_gb * 10))  # 10 connections per GB, max 100
        backlog = 2048  # Larger connection queue for Unix
        keep_alive = 5  # Standard keep-alive

        print(f"\n[OPTIMIZED CONFIG] Unix mode with {worker_count} workers")
        print(f"[OPTIMIZED CONFIG] Memory: {memory_gb:.1f}GB, Concurrency: {concurrency_per_worker} per worker")
        print(f"[OPTIMIZED CONFIG] Total max connections: {worker_count * concurrency_per_worker}")

        # Run with Unix-optimized settings
        uvicorn.run(
            "test_app:application",
            host="127.0.0.1",
            port=8000,
            reload=True,
            loop="uvloop",  # Use uvloop for better performance on Unix
            workers=worker_count,
            limit_concurrency=concurrency_per_worker,
            backlog=backlog,
            # Use a very high value instead of 0 to avoid termination
            limit_max_requests=1000000,  # Very high value to effectively disable restarts
            timeout_keep_alive=keep_alive,
            log_level="warning",  # Minimal logging
            access_log=False,      # No access logs
            use_colors=False,      # Disable colors for less overhead
            http="httptools"      # Use httptools for better performance on Unix
        )
