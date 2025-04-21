"""
Example application for testing CLI commands.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create the application
app = ProAPI(debug=True)

@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Welcome to the CLI test app!",
        "app": "main",
        "port": request.headers.get("Host", "unknown").split(":")[-1]
    }

@app.get("/hello/{name}")
def hello(name, request):
    """Hello endpoint."""
    return {
        "message": f"Hello, {name}!",
        "app": "main"
    }

@app.get("/info")
def info(request):
    """Server information."""
    import platform
    import sys
    
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "app": "main",
        "host": request.headers.get("Host", "unknown"),
        "remote_addr": request.remote_addr
    }

if __name__ == "__main__":
    print("This is a test application for the ProAPI CLI.")
    print("To run this app with the CLI, use one of the following commands:")
    print()
    print("  # Run with default settings")
    print("  python -m proapi run examples/main.py")
    print()
    print("  # Run with specific app instance")
    print("  python -m proapi run examples/main.py:app")
    print()
    print("  # Run with specific port")
    print("  python -m proapi run examples/main.py --port 5500")
    print()
    print("  # Run with specific host")
    print("  python -m proapi run examples/main.py --host 0.0.0.0")
    print("  python -m proapi run examples/main.py --host all")
    print()
    print("  # Compile and run")
    print("  python -m proapi -c run examples/main.py")
    print()
    
    # By default, run the app
    app.run(host="127.0.0.1", port=8000)
