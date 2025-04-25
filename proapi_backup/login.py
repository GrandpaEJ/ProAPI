"""
Login support for ProAPI.

This module provides login functionality similar to Flask-Login.
It allows you to:
- Manage user authentication
- Protect routes with login_required decorator
- Store and retrieve user information in sessions
- Customize user loading and authentication

Example:
    from proapi import ProAPI
    from proapi.login import LoginManager, login_required, current_user

    app = ProAPI(enable_sessions=True)
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Load user from database
        return User.get(user_id)

    @app.get("/profile")
    @login_required
    def profile(request):
        return {"user": current_user.to_dict()}
"""

import functools
import threading
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

from .server import Request, Response
from .session_proxy import get_current_session
from .request_proxy import get_current_request
from .logging import app_logger

# Use app_logger with a specific context for login-related logs
login_logger = app_logger.bind(context="login")

# Thread-local storage for the current user
_user_local = threading.local()

# Type variable for the user class
UserType = TypeVar('UserType')


class AnonymousUser:
    """
    Default user class for unauthenticated users.

    This class provides a default implementation for unauthenticated users.
    It can be replaced with a custom class by setting LoginManager.anonymous_user.
    """

    @property
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated."""
        return False

    @property
    def is_active(self) -> bool:
        """Check if the user is active."""
        return False

    @property
    def is_anonymous(self) -> bool:
        """Check if the user is anonymous."""
        return True

    def get_id(self) -> str:
        """Get the user ID."""
        return ""


class UserMixin:
    """
    Mixin class that provides default implementations for the user methods.

    This class can be used as a mixin for user classes to provide default
    implementations for the required methods.
    """

    @property
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated."""
        return True

    @property
    def is_active(self) -> bool:
        """Check if the user is active."""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Check if the user is anonymous."""
        return False

    def get_id(self) -> str:
        """Get the user ID."""
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError(
                "No id attribute found. Override get_id() or set an id attribute."
            )


class LoginManager:
    """
    Login manager for ProAPI.

    This class manages user authentication and provides access to the current user.
    """

    def __init__(self, app=None):
        """
        Initialize the login manager.

        Args:
            app: ProAPI application (optional)
        """
        self.app = app
        self._user_callback = None
        self.anonymous_user = AnonymousUser
        self.login_view = None
        self.login_message = "Please log in to access this page."
        self.login_message_category = "info"

        login_logger.info("LoginManager initialized")

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize the login manager with an application.

        Args:
            app: ProAPI application
        """
        self.app = app

        # Check if sessions are enabled
        if not getattr(app, 'enable_sessions', False):
            login_logger.warning(
                "Sessions are not enabled. Login functionality requires sessions. "
                "Enable sessions by setting enable_sessions=True when creating the app."
            )
        else:
            login_logger.info("Sessions are enabled, login functionality will work properly")

        # Add login middleware
        app.use(self._login_middleware)
        login_logger.debug("Added login middleware to application")

        # Store login manager in app for access from routes
        app._login_manager = self
        login_logger.info(f"LoginManager initialized for application: {app.__class__.__name__}")

    def user_loader(self, callback):
        """
        Decorator to register a user loader function.

        The user loader function is called to load a user from the user ID
        stored in the session.

        Args:
            callback: Function that takes a user ID and returns a user object

        Returns:
            The callback function
        """
        self._user_callback = callback
        login_logger.info(f"User loader function registered: {callback.__name__}")
        return callback

    def _load_user(self, user_id):
        """
        Load a user from the user ID.

        Args:
            user_id: User ID

        Returns:
            User object or None if not found
        """
        if self._user_callback is None:
            login_logger.error("No user_loader has been registered")
            raise Exception(
                "No user_loader has been registered. "
                "Register one with the user_loader decorator."
            )

        login_logger.debug(f"Loading user with ID: {user_id}")
        user = self._user_callback(user_id)
        if user:
            login_logger.debug(f"User loaded successfully: {user_id}")
        else:
            login_logger.warning(f"User not found with ID: {user_id}")
        return user

    def _login_middleware(self, request):
        """
        Login middleware.

        This middleware loads the current user from the session and makes it
        available through the current_user proxy.

        Args:
            request: HTTP request

        Returns:
            Modified request
        """
        # Check if sessions are enabled
        if not hasattr(request, 'session'):
            login_logger.debug("No session available, setting anonymous user")
            set_current_user(self.anonymous_user())
            return request

        # Get user ID from session
        user_id = request.session.get('_user_id')

        if user_id:
            login_logger.debug(f"Found user ID in session: {user_id}")
            # Load user from user ID - simple synchronous version like Flask
            user = self._load_user(user_id)
            if user:
                # Set current user
                login_logger.debug(f"Setting current user: {user_id}")
                set_current_user(user)
                return request

        # No user found, set anonymous user
        login_logger.debug("No authenticated user found, setting anonymous user")
        set_current_user(self.anonymous_user())
        return request


def login_user(user, remember=False, duration=None):
    """
    Log in a user.

    This function logs in a user by storing the user ID in the session.

    Args:
        user: User object
        remember: Whether to remember the user across sessions
        duration: Session duration in seconds (only used if remember=True)

    Returns:
        True if login was successful, False otherwise
    """
    if not hasattr(user, 'get_id'):
        login_logger.error("User object must have a get_id() method")
        raise TypeError("User must have a get_id() method.")

    # Get user ID
    user_id = user.get_id()
    if not user_id:
        login_logger.warning("User ID is empty, login failed")
        return False

    # Get current session
    session = get_current_session()
    if not session:
        login_logger.error("No session available. Make sure sessions are enabled.")
        return False

    # Store user ID in session - simple synchronous version like Flask
    session['_user_id'] = user_id

    # Set remember cookie if requested
    if remember:
        login_logger.debug(f"Setting remember cookie for user {user_id}")
        if duration:
            session.permanent = True
            login_logger.debug(f"Setting session duration to {duration} seconds")
            # This would set the session expiration, but we need to implement this
            # in the session manager first

    # Set current user
    set_current_user(user)

    login_logger.info(f"User {user_id} logged in successfully")
    return True


def logout_user():
    """
    Log out the current user.

    This function logs out the current user by removing the user ID from the session.

    Returns:
        True if logout was successful, False otherwise
    """
    # Get current session
    session = get_current_session()
    if not session:
        login_logger.error("No session available. Make sure sessions are enabled.")
        return False

    # Get current user ID for logging
    user_id = None
    if '_user_id' in session:
        user_id = session['_user_id']

    # Remove user ID from session - simple synchronous version like Flask
    if '_user_id' in session:
        del session['_user_id']
        login_logger.debug(f"Removed user ID from session")

    # Set anonymous user
    request = get_current_request()
    if request and hasattr(request, 'app') and hasattr(request.app, '_login_manager'):
        set_current_user(request.app._login_manager.anonymous_user())
    else:
        set_current_user(AnonymousUser())

    if user_id:
        login_logger.info(f"User {user_id} logged out successfully")
    else:
        login_logger.info("User logged out successfully")

    return True


def login_required(func=None, redirect_to=None):
    """
    Decorator to require login for a route.

    This decorator checks if the current user is authenticated and redirects
    to the login page if not.

    Args:
        func: Route function
        redirect_to: URL to redirect to if not authenticated (overrides login_view)

    Returns:
        Decorated function
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                # Get request
                request = get_current_request()
                if not request:
                    login_logger.error("No request available in login_required decorator")
                    raise Exception("No request available.")

                # Get login manager
                if not hasattr(request, 'app') or not hasattr(request.app, '_login_manager'):
                    login_logger.error("No login manager available in login_required decorator")
                    raise Exception("No login manager available.")

                login_manager = request.app._login_manager

                # Get login view
                login_view = redirect_to or login_manager.login_view
                if not login_view:
                    # No login view, return 401 Unauthorized
                    login_logger.warning("No login view specified, returning 401 Unauthorized")
                    return Response(
                        status=401,
                        body={"error": login_manager.login_message},
                        content_type="application/json"
                    )

                # Store next URL in session - simple synchronous version like Flask
                if hasattr(request, 'session'):
                    request.session['_next'] = request.path
                    login_logger.debug(f"Stored next URL in session: {request.path}")

                # Redirect to login view
                from .helpers import redirect
                login_logger.info(f"Redirecting unauthenticated user to login page: {login_view}")
                return redirect(login_view)

            # User is authenticated, call the original function
            login_logger.debug(f"User authenticated, accessing protected route: {f.__name__}")
            return f(*args, **kwargs)

        return decorated_function

    # Handle both @login_required and @login_required(redirect_to=...)
    if func:
        return decorator(func)
    return decorator


def set_current_user(user):
    """
    Set the current user for the current thread.

    Args:
        user: User object
    """
    _user_local.user = user


def get_current_user():
    """
    Get the current user for the current thread.

    Returns:
        Current user or AnonymousUser if not set
    """
    return getattr(_user_local, 'user', AnonymousUser())


# Create a proxy for the current user
class CurrentUserProxy:
    """
    Proxy to the current user.

    This class provides access to the current user in the current thread.
    It's used to provide a global `current_user` object that always refers to the
    user of the current request being processed.
    """

    def __getattr__(self, name):
        """
        Get an attribute from the current user.

        Args:
            name: Attribute name

        Returns:
            Attribute value
        """
        return getattr(get_current_user(), name)


# Create a global current_user object
current_user = CurrentUserProxy()
