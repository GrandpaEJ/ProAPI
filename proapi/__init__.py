"""
ProAPI - A lightweight, beginner-friendly yet powerful Python web framework.

Features:
- Simpler than Flask/FastAPI with intuitive API design
- Faster than FastAPI with optimized routing and request handling
- Stable like Flask with robust error handling
- Decorator-based routing (@app.get(), @app.post(), etc.)
- Simple template rendering with Jinja2
- Easy server startup with app.run()
- Optional async support
- Optional Cython-based compilation for speed boost
- Minimal dependencies
- Built-in JSON support
- Middleware system
- Session management
- Automatic API documentation at /.docs
- Structured logging with Loguru
- CLI commands
- Enhanced WebSocket support

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

__version__ = "0.3.10"

from .core import ProAPI
from .routing import Route
from .templating import render
from .logging import app_logger, setup_logger, get_logger
from .session import Session, SessionManager

# Import helpers for easier usage
from .helpers import redirect, jsonify

# Create a request proxy for global access
from .request_proxy import request

# Create a session proxy for global access
from .session_proxy import session

__all__ = [
    "ProAPI", "Route", "render", "app_logger", "setup_logger", "get_logger",
    "Session", "SessionManager", "redirect", "jsonify", "request", "session"
]
