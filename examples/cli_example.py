"""
Example of CLI functionality with ProAPI.

This example demonstrates how to use the ProAPI CLI to run an application.
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
        "message": "CLI Example",
        "description": "This example demonstrates how to use the ProAPI CLI.",
        "usage": [
            "python -m proapi run examples/cli_example.py",
            "python -m proapi run examples/cli_example.py --debug",
            "python -m proapi run examples/cli_example.py --port 8080",
            "python -m proapi run examples/cli_example.py --workers 4"
        ]
    }

@app.get("/hello/{name}")
def hello(name, request):
    """Hello endpoint."""
    return {
        "message": f"Hello, {name}!",
        "method": request.method,
        "path": request.path,
        "headers": {k: v for k, v in request.headers.items()}
    }

# This conditional is important for the CLI to work correctly
if __name__ == "__main__":
    # When run directly, start the server
    app.run(host="127.0.0.1", port=8004)
    
    # When run via the CLI, the app will be imported and the CLI will call app.run()
    # with the appropriate arguments
