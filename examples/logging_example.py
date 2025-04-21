"""
Example of logging functionality with ProAPI and Loguru.
"""

import os
import sys
import time

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, app_logger

# Create the application with logging configuration
app = ProAPI(
    debug=True,
    log_level="DEBUG",  # Set log level to DEBUG for more detailed logs
    log_file="logs/app.log"  # Save logs to a file
)

# Define routes

@app.get("/")
def index(request):
    """Home page."""
    app_logger.info("Accessing home page")
    return {
        "message": "Welcome to the Logging Example!",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This endpoint"},
            {"path": "/debug", "method": "GET", "description": "Log a debug message"},
            {"path": "/info", "method": "GET", "description": "Log an info message"},
            {"path": "/warning", "method": "GET", "description": "Log a warning message"},
            {"path": "/error", "method": "GET", "description": "Log an error message"},
            {"path": "/critical", "method": "GET", "description": "Log a critical message"}
        ]
    }

@app.get("/debug")
def debug_log(request):
    """Log a debug message."""
    app_logger.debug("This is a debug message")
    return {"message": "Debug message logged", "level": "DEBUG"}

@app.get("/info")
def info_log(request):
    """Log an info message."""
    app_logger.info("This is an info message")
    return {"message": "Info message logged", "level": "INFO"}

@app.get("/warning")
def warning_log(request):
    """Log a warning message."""
    app_logger.warning("This is a warning message")
    return {"message": "Warning message logged", "level": "WARNING"}

@app.get("/error")
def error_log(request):
    """Log an error message."""
    app_logger.error("This is an error message")
    return {"message": "Error message logged", "level": "ERROR"}

@app.get("/critical")
def critical_log(request):
    """Log a critical message."""
    app_logger.critical("This is a critical message")
    return {"message": "Critical message logged", "level": "CRITICAL"}

@app.get("/exception")
def exception_log(request):
    """Log an exception."""
    try:
        # Intentionally raise an exception
        1 / 0
    except Exception as e:
        app_logger.exception(f"An exception occurred: {e}")
        return {"message": "Exception logged", "error": str(e)}

# Add middleware for custom logging
@app.use
def timing_middleware(request):
    """Add timing information to the response."""
    request.start_time = time.time()
    
    # Log the request with custom fields
    app_logger.bind(
        method=request.method,
        path=request.path,
        ip=request.headers.get("X-Forwarded-For", request.client_address[0])
    ).info("Request received")
    
    def add_timing_header(response):
        duration = time.time() - request.start_time
        response.headers['X-Response-Time'] = f"{duration:.6f}s"
        
        # Log the response with custom fields
        status_code = response.status
        app_logger.bind(
            method=request.method,
            path=request.path,
            status=status_code,
            duration=f"{duration:.6f}s"
        ).info("Response sent")
        
        return response
    
    request.add_timing_header = add_timing_header
    return request

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Log application startup
    app_logger.info("Logging Example Application starting up")
    
    print("Logging Example")
    print()
    print("Web Interface: http://127.0.0.1:8000")
    print("Log file: logs/app.log")
    print()
    
    # Run the application
    app.run(host="127.0.0.1", port=8000)
