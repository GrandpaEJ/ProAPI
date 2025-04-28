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
__version__ = "0.4.4"

# Check Python version
if sys.version_info < (3, 8):
    raise RuntimeError("ProAPI requires Python 3.8 or higher")

# Import core components
from proapi.core.core import ProAPI
from proapi.templates.templating import render
from proapi.core.logging import app_logger, setup_logger

# Import authentication components
from proapi.auth.login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from proapi.auth.jwt import JWTManager, jwt_required, create_access_token, create_refresh_token
from proapi.auth.http_auth import HTTPBasicAuth, HTTPDigestAuth
from proapi.auth.principal import Principal, Permission, RoleNeed, UserNeed, admin_permission
from proapi.auth.user import UserManager, get_user_manager

# Import other useful components
from proapi.performance.scheduler import thread_task, process_task, auto_task
from proapi.utils.forwarding import setup_cloudflare_tunnel

# Define what's available when using "from proapi import *"
__all__ = [
    # Core
    "ProAPI",
    "render",
    "app_logger",
    "setup_logger",

    # Authentication - Login
    "LoginManager",
    "login_required",
    "login_user",
    "logout_user",
    "current_user",
    "UserMixin",

    # Authentication - JWT
    "JWTManager",
    "jwt_required",
    "create_access_token",
    "create_refresh_token",

    # Authentication - HTTP
    "HTTPBasicAuth",
    "HTTPDigestAuth",

    # Authentication - RBAC
    "Principal",
    "Permission",
    "RoleNeed",
    "UserNeed",
    "admin_permission",

    # Authentication - User Management
    "UserManager",
    "get_user_manager",

    # Performance
    "thread_task",
    "process_task",
    "auto_task",

    # Utilities
    "setup_cloudflare_tunnel",
]
