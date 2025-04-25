"""
ProAPI run script.

This script provides a simple way to run ProAPI applications with auto-reloading.
"""

import os
import sys
import importlib.util
import uvicorn
from pathlib import Path

from .logging import app_logger

def run_app(app_path, host="127.0.0.1", port=8000, reload=True):
    """
    Run a ProAPI application with auto-reloading.

    Args:
        app_path: Path to the application file or module:app_var
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reloading
    """
    # Check if app_path contains a variable name
    if ":" in app_path:
        module_path, app_var = app_path.split(":", 1)
    else:
        module_path, app_var = app_path, "app"

    # Handle file paths
    if os.path.exists(module_path):
        # Convert to absolute path
        abs_path = os.path.abspath(module_path)

        # Add the directory to sys.path
        dir_path = os.path.dirname(abs_path)
        if dir_path not in sys.path:
            sys.path.insert(0, dir_path)

        # Get the module name from the file name
        module_name = os.path.splitext(os.path.basename(abs_path))[0]
    else:
        # It's already a module name
        module_name = module_path

    # Create the import string
    import_string = f"{module_name}:{app_var}"

    app_logger.info(f"Running {import_string} with uvicorn")
    app_logger.info(f"Host: {host}, Port: {port}, Reload: {reload}")

    # Run with uvicorn
    uvicorn.run(
        import_string,
        host=host,
        port=port,
        reload=reload
    )

if __name__ == "__main__":
    # This allows the script to be run directly
    if len(sys.argv) < 2:
        print("Usage: python -m proapi.run app_path [host] [port] [--no-reload]")
        sys.exit(1)

    app_path = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
    reload = "--no-reload" not in sys.argv

    run_app(app_path, host, port, reload)
