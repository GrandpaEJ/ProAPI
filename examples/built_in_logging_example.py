"""
Example demonstrating ProAPI's built-in logging with Loguru.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, app_logger

# Create the application with custom logging configuration
app = ProAPI(
    debug=True,
    log_level="DEBUG",
    log_format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    log_file="logs/built_in.log"
)

# Define routes

@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Welcome to the Built-in Logging Example!",
        "description": "This example demonstrates ProAPI's built-in logging with Loguru.",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This endpoint"},
            {"path": "/error", "method": "GET", "description": "Trigger an error to see error logging"},
            {"path": "/forward", "method": "GET", "description": "Test port forwarding logging"}
        ]
    }

@app.get("/error")
def error(request):
    """Trigger an error to see error logging."""
    # Intentionally raise an exception to see error logging
    raise ValueError("This is a test error to demonstrate error logging")

@app.get("/forward")
def forward(request):
    """Test port forwarding."""
    # This will log information about port forwarding
    app.run(forward=True, forward_type="ngrok")
    return {"message": "Port forwarding test"}

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the application
    app_logger.info("Starting Built-in Logging Example")
    print("Built-in Logging Example")
    print()
    print("Web Interface: http://127.0.0.1:8000")
    print("Log file: logs/built_in.log")
    print()
    
    # Run the application
    app.run(host="127.0.0.1", port=8000)
