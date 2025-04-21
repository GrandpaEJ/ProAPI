"""
Example demonstrating ProAPI's auto-reloader.

This example shows how to use the auto-reloader feature to automatically
reload the application when code changes are detected.

To test:
1. Run this example
2. Edit this file (e.g., change the message in the index function)
3. Save the file
4. The application will automatically reload with your changes
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, app_logger

# Create the application with reloader enabled
app = ProAPI(
    debug=True,
    env="development",
    use_reloader=True,  # Enable auto-reloader
    watch_dirs=['.'],   # Watch current directory
    exclude_dirs=['__pycache__', '.git'],  # Exclude these directories
    exclude_patterns=['*.pyc', '*.pyo'],   # Exclude these file patterns
    log_level="DEBUG"
)

# Define routes

@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Welcome to the Reloader Example!",
        "instructions": "Edit this file and save it to see the auto-reloader in action.",
        "tip": "Try changing this message and saving the file."
    }

@app.get("/time")
def get_time(request):
    """Get the current time."""
    import datetime
    now = datetime.datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d")
    }

@app.get("/counter/{count:int}")
def counter(count, request):
    """Count to a number."""
    return {
        "counting_to": count,
        "numbers": list(range(1, count + 1))
    }

if __name__ == "__main__":
    print("Reloader Example")
    print()
    print("Web Interface: http://127.0.0.1:8000")
    print("Auto-reloader is enabled. Edit this file and save to see changes.")
    print()
    
    # Run the application with reloader
    app.run(host="127.0.0.1", port=8000)
