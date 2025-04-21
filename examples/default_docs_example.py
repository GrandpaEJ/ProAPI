"""
Example of default documentation endpoint with ProAPI.
"""

import os
import sys
import time

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create a simple application
app = ProAPI(debug=True)

# Define a simple route
@app.get("/")
def index(request):
    """Home page."""
    return {"message": "Welcome to the default documentation example!"}

@app.get("/hello/{name}")
def hello(name, request):
    """Say hello to a user."""
    return {"message": f"Hello, {name}!"}

@app.post("/users")
def create_user(request):
    """Create a new user."""
    data = request.json
    return {"user": data, "message": "User created successfully"}

# Add a logging middleware to see all requests
@app.use
def logging_middleware(request):
    """Log all requests."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.path}")
    return request

if __name__ == "__main__":
    print("Default Documentation Example")
    print()
    print("Web Interface: http://127.0.0.1:8010")
    print("Default Documentation: http://127.0.0.1:8010/.docs")
    print()
    
    # Run the application
    app.run(host="127.0.0.1", port=8010)
