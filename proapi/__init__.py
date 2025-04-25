"""
ProAPI - A lightweight, beginner-friendly yet powerful Python web framework.

ProAPI is designed to be simpler than Flask, faster than FastAPI, and stable like Flask.
It provides a clean, intuitive API for building web applications and APIs.

Example:
    from proapi import ProAPI

    app = ProAPI(debug=True)

    @app.get("/")
    def index(request):
        return {"message": "Hello, World!"}

    if __name__ == "__main__":
        app.run()
"""

import sys

# Version information
__version__ = "0.4.1"

# Check Python version
if sys.version_info < (3, 8):
    raise RuntimeError("ProAPI requires Python 3.8 or higher")

# Import core components
from proapi.core.core import ProAPI
from proapi.templates.templating import render
from proapi.auth.login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from proapi.core.logging import app_logger, setup_logger

# Import other useful components
from proapi.performance.scheduler import thread_task, process_task, auto_task
from proapi.utils.forwarding import setup_cloudflare_tunnel

# Define what's available when using "from proapi import *"
__all__ = [
    "ProAPI",
    "render",
    "LoginManager",
    "login_required",
    "login_user",
    "logout_user",
    "current_user",
    "UserMixin",
    "app_logger",
    "setup_logger",
    "thread_task",
    "process_task",
    "auto_task",
    "setup_cloudflare_tunnel",
]
