"""
ProAPI runner module.

This module provides a simplified way to run ProAPI applications with auto-reloading.
"""

import os
import sys
import importlib
import uvicorn
from pathlib import Path

from .logging import app_logger
from .asgi_adapter import create_asgi_app

def run_app(app_path=None, app_instance=None, host="127.0.0.1", port=8000,
            reload=True, workers=1, debug=None):
    """
    Run a ProAPI application with auto-reloading.

    Args:
        app_path: Path to the application file or module:app_var
        app_instance: Direct reference to a ProAPI instance (alternative to app_path)
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reloading
        workers: Number of worker processes
        debug: Enable debug mode (overrides app's debug setting)
    """
    if app_instance and debug is not None:
        app_instance.debug = debug

    if app_instance:
        # Create an ASGI app directly from the instance
        asgi_app = create_asgi_app(app_instance)

        app_logger.info(f"Running ProAPI app with direct ASGI adapter")
        app_logger.info(f"Host: {host}, Port: {port}, Reload: {reload}, Workers: {workers}")

        # Run with uvicorn
        uvicorn.run(
            asgi_app,
            host=host,
            port=port,
            reload=reload,
            workers=workers
        )
        return

    # Check if app_path contains a variable name
    if ":" in app_path:
        module_path, app_var = app_path.split(":", 1)
    else:
        module_path, app_var = app_path, "app"

    # Convert to absolute path if it's a file
    if os.path.exists(module_path):
        module_path = os.path.abspath(module_path)

    # Add the directory to sys.path
    if os.path.isfile(module_path):
        dir_path = os.path.dirname(module_path)
        if dir_path not in sys.path:
            sys.path.insert(0, dir_path)
        module_name = os.path.splitext(os.path.basename(module_path))[0]
    else:
        module_name = module_path

    # Create the import string
    import_string = f"{module_name}:{app_var}"

    app_logger.info(f"Running {import_string} with uvicorn")
    app_logger.info(f"Host: {host}, Port: {port}, Reload: {reload}, Workers: {workers}")

    # Run with uvicorn
    uvicorn.run(
        import_string,
        host=host,
        port=port,
        reload=reload,
        workers=workers
    )

if __name__ == "__main__":
    # This allows the script to be run directly
    if len(sys.argv) < 2:
        print("Usage: python -m proapi.runner app_path [host] [port] [--no-reload]")
        sys.exit(1)

    app_path = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
    reload = "--no-reload" not in sys.argv

    run_app(app_path, host=host, port=port, reload=reload)
