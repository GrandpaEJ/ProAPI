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
- User authentication and login management
- Automatic API documentation at /.docs
- Structured logging with Loguru
- CLI commands
- Enhanced WebSocket support

Usage:
    from proapi.core import ProAPI

    app = ProAPI()

    @app.get("/")
    def index(request):
        return {"message": "Hello, World!"}

    if __name__ == "__main__":
        app.run()
"""

import sys

# Check Python version
if sys.version_info < (3, 8):
    raise RuntimeError("ProAPI requires Python 3.8 or higher")

__version__ = "0.4.0"

from proapi.core.core import ProAPI
from proapi.routing.routing import Route
from proapi.templates.templating import render
from proapi.core.logging import app_logger, setup_logger, get_logger
from proapi.session.session import Session, SessionManager

# Import helpers for easier usage
from proapi.utils.helpers import redirect, jsonify

# Create a request proxy for global access
from proapi.routing.request_proxy import request

# Create a session proxy for global access
from proapi.session.session_proxy import session

# Import login functionality
from proapi.auth.login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin

__all__ = [
    "ProAPI", "Route", "render", "app_logger", "setup_logger", "get_logger",
    "Session", "SessionManager", "redirect", "jsonify", "request", "session",
    "LoginManager", "login_required", "login_user", "logout_user", "current_user", "UserMixin"
]
