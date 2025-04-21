"""
Example of multiple ProAPI applications in a single file.

This example demonstrates how to use the CLI to run a specific app instance.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create the first application
app1 = ProAPI(debug=True)

@app1.get("/")
def index1(request):
    """Home page for app1."""
    return {
        "message": "Welcome to app1!",
        "app": "app1",
        "port": 8010
    }

@app1.get("/hello/{name}")
def hello1(name, request):
    """Hello endpoint for app1."""
    return {
        "message": f"Hello, {name} from app1!",
        "app": "app1"
    }

# Create the second application
app2 = ProAPI(debug=True)

@app2.get("/")
def index2(request):
    """Home page for app2."""
    return {
        "message": "Welcome to app2!",
        "app": "app2",
        "port": 8020
    }

@app2.get("/hello/{name}")
def hello2(name, request):
    """Hello endpoint for app2."""
    return {
        "message": f"Hello, {name} from app2!",
        "app": "app2"
    }

# Create the main application
app = ProAPI(debug=True)

@app.get("/")
def index(request):
    """Home page for the main app."""
    return {
        "message": "Welcome to the main app!",
        "app": "main",
        "port": 8000,
        "other_apps": [
            {"name": "app1", "port": 8010},
            {"name": "app2", "port": 8020}
        ]
    }

@app.get("/hello/{name}")
def hello(name, request):
    """Hello endpoint for the main app."""
    return {
        "message": f"Hello, {name} from the main app!",
        "app": "main"
    }

if __name__ == "__main__":
    print("This file contains multiple ProAPI applications.")
    print("To run a specific app, use the CLI:")
    print()
    print("  # Run the main app (default)")
    print("  python -m proapi run examples/multi_app.py")
    print()
    print("  # Run app1")
    print("  python -m proapi run examples/multi_app.py:app1 --port 8010")
    print()
    print("  # Run app2")
    print("  python -m proapi run examples/multi_app.py:app2 --port 8020")
    print()
    print("  # Run with host options")
    print("  python -m proapi run examples/multi_app.py --host local")
    print("  python -m proapi run examples/multi_app.py --host all")
    print()
    print("  # Compile and run")
    print("  python -m proapi -c run examples/multi_app.py")
    print()
    
    # By default, run the main app
    app.run(host="127.0.0.1", port=8000)
