"""
Example of middleware functionality with ProAPI.
"""

import os
import sys
import time

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create the application
app = ProAPI(debug=True)

# Define middleware

@app.use
def logging_middleware(request):
    """Log request details."""
    print(f"[Logging] {request.method} {request.path}")
    # Store start time for calculating duration
    request.start_time = time.time()
    return request

@app.use
def timing_middleware(request):
    """Add timing information to the response."""
    # This middleware will be applied after the request is processed
    # by adding a hook to the response
    def add_timing_header(response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response.headers['X-Response-Time'] = f"{duration:.6f}s"
        return response
    
    # Store the hook on the request object
    request.add_timing_header = add_timing_header
    return request

@app.use
def auth_middleware(request):
    """Simple authentication middleware."""
    from proapi.server import Response
    
    # Check for API key in headers
    api_key = request.headers.get('X-API-Key')
    
    # Skip auth for the home page
    if request.path == '/':
        return request
    
    # Require API key for other endpoints
    if not api_key:
        return Response(
            status=401,
            body={"error": "API key required"},
            content_type="application/json"
        )
    
    # Very simple validation (in a real app, you'd check against a database)
    if api_key != "test-api-key":
        return Response(
            status=403,
            body={"error": "Invalid API key"},
            content_type="application/json"
        )
    
    # Store user info on the request
    request.user = {"id": 1, "name": "Test User"}
    return request

# Define routes

@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Middleware Example",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This endpoint (no auth required)"},
            {"path": "/protected", "method": "GET", "description": "Protected endpoint (requires API key)"},
            {"path": "/user", "method": "GET", "description": "User info (requires API key)"}
        ],
        "usage": "Add header 'X-API-Key: test-api-key' to access protected endpoints"
    }

@app.get("/protected")
def protected(request):
    """Protected endpoint."""
    return {
        "message": "You have accessed a protected endpoint",
        "timestamp": time.time()
    }

@app.get("/user")
def user_info(request):
    """User info endpoint."""
    return {
        "message": "User info",
        "user": request.user
    }

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8003)
