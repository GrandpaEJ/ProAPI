"""
ProAPI - A lightweight, beginner-friendly yet powerful Python web framework.

Features:
- Decorator-based routing (@app.get(), @app.post(), etc.)
- Simple template rendering with Jinja2
- Easy server startup with app.run()
- Optional async support
- Optional Cython-based compilation for speed
- Minimal dependencies
- Built-in JSON support
- Middleware system
- Automatic API documentation
- Structured logging with Loguru
- CLI commands

Usage:
    from proapi import ProAPI

    app = ProAPI()

    @app.get("/")
    def index(request):
        return {"message": "Hello, World!"}

    if __name__ == "__main__":
        app.run()
"""

import sys

# Check Python version
if sys.version_info < (3, 7):
    raise RuntimeError("ProAPI requires Python 3.7 or higher")

__version__ = "0.1.0"

from .core import ProAPI
from .routing import Route
from .templating import render
from .logging import app_logger, setup_logger, get_logger

__all__ = ["ProAPI", "Route", "render", "app_logger", "setup_logger", "get_logger"]
