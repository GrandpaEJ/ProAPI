"""
Example of running ProAPI in production mode.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, app_logger

# Create the application in production mode
app = ProAPI(
    env="production",  # Set environment to production
    debug=False,       # Disable debug mode
    workers=4,         # Use 4 worker processes
    request_timeout=60,  # 60 second timeout
    max_request_size=5 * 1024 * 1024,  # 5MB max request size
    trusted_hosts=[
        "localhost", "localhost:8000",
        "127.0.0.1", "127.0.0.1:8000",
        "*.example.com"
    ],  # Trusted hosts with and without port
    log_file="logs/production.log"  # Log to file
)

# Define routes

@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Welcome to the Production Example!",
        "environment": request.env,
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This endpoint"},
            {"path": "/api/data", "method": "GET", "description": "Get data"},
            {"path": "/api/data", "method": "POST", "description": "Create data"}
        ]
    }

@app.get("/api/data")
def get_data(request):
    """Get data."""
    # In production, we would fetch from a database
    return {
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]
    }

@app.post("/api/data")
def create_data(request):
    """Create data."""
    # Get JSON data from request
    data = request.json

    # Log the operation
    app_logger.info(f"Data creation request: {data}")

    # In production, we would save to a database
    return {
        "success": True,
        "message": "Data created successfully",
        "data": data
    }

@app.get("/error")
def error(request):
    """Trigger an error to see production error handling."""
    # This will be handled according to production settings
    raise ValueError("This is a test error")

# Add middleware for security
@app.use
def security_middleware(request):
    """Add security headers."""
    def add_security_headers(response):
        # Add security headers for production
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    request.add_security_headers = add_security_headers
    return request

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Run the application with production settings
    app_logger.info("Starting Production Example")
    print("Production Example")
    print()
    print("Web Interface: http://127.0.0.1:8000")
    print("Log file: logs/production.log")
    print()

    # Run the application
    # Note: In a real production environment, you would use a proper WSGI/ASGI server
    app.run(host="0.0.0.0", port=8000)
