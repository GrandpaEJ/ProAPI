"""
Example demonstrating ProAPI with uvicorn's auto-reloader.

This example shows how to use uvicorn's auto-reloader feature to automatically
reload the application when code changes are detected.

To test:
1. Run this example
2. Edit this file (e.g., change the message in the index function)
3. Save the file
4. The application will automatically reload with your changes

Requirements:
- uvicorn: pip install uvicorn
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create the application with reloader enabled
app = ProAPI(
    debug=True,
    env="development",
    use_reloader=True  # Enable auto-reloader (requires uvicorn)
)

# Define routes

@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Welcome to the Uvicorn Reloader Example!",
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
    print("Uvicorn Reloader Example")
    print()
    print("Web Interface: http://127.0.0.1:8000")
    print("Auto-reloader is enabled. Edit this file and save to see changes.")
    print()
    
    # Run the application with uvicorn reloader
    app.run(host="127.0.0.1", port=8000, server_type="uvicorn", use_reloader=True)
