"""
Role-Based Authorization for ProAPI.

This module provides role-based access control (RBAC) for ProAPI applications,
similar to Flask-Principal. It allows you to:
- Define roles and permissions
- Protect routes with role-based access control
- Check permissions in route handlers
- Integrate with the login system

Example:
    from proapi import ProAPI
    from proapi.auth.login import LoginManager, login_required, current_user
    from proapi.auth.principal import Principal, Permission, RoleNeed, UserNeed

    app = ProAPI(enable_sessions=True)
    login_manager = LoginManager(app)
    principal = Principal(app)

    # Define permissions
    admin_permission = Permission(RoleNeed('admin'))
    editor_permission = Permission(RoleNeed('editor'))

    @principal.identity_loader
    def load_identity():
        if current_user.is_authenticated:
            # Return the identity with the user's roles
            return {'user_id': current_user.id, 'roles': current_user.roles}
        return None

    @app.get("/admin")
    @login_required
    @admin_permission.require()
    def admin_page(request):
        return {"message": "Admin page"}

    @app.get("/editor")
    @login_required
    @editor_permission.require()
    def editor_page(request):
        return {"message": "Editor page"}
"""

import functools
import threading
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from proapi.server.server import Response
from proapi.routing.request_proxy import get_current_request
from proapi.core.logging import app_logger

# Use app_logger with a specific context for principal logs
principal_logger = app_logger.bind(context="principal")

# Thread-local storage for identity data
_identity_local = threading.local()


class Need:
    """
    Base class for authorization needs.
    
    A need is a tuple of (need_type, value) that represents a specific
    authorization requirement.
    """
    
    def __init__(self, need_type: str, value: Any):
        """
        Initialize a need.
        
        Args:
            need_type: Type of need (e.g., 'role', 'action', 'user')
            value: Value of the need
        """
        self.need_type = need_type
        self.value = value
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.need_type}:{self.value}>"
    
    def __eq__(self, other):
        if not isinstance(other, Need):
            return False
        return self.need_type == other.need_type and self.value == other.value
    
    def __hash__(self):
        return hash((self.need_type, self.value))


class RoleNeed(Need):
    """
    A need for a specific role.
    """
    
    def __init__(self, role: str):
        """
        Initialize a role need.
        
        Args:
            role: Role name
        """
        super().__init__('role', role)


class UserNeed(Need):
    """
    A need for a specific user.
    """
    
    def __init__(self, user_id: str):
        """
        Initialize a user need.
        
        Args:
            user_id: User ID
        """
        super().__init__('user', user_id)


class ActionNeed(Need):
    """
    A need for a specific action.
    """
    
    def __init__(self, action: str):
        """
        Initialize an action need.
        
        Args:
            action: Action name
        """
        super().__init__('action', action)


class ItemNeed(Need):
    """
    A need for a specific item.
    """
    
    def __init__(self, item_type: str, item_id: str, action: str):
        """
        Initialize an item need.
        
        Args:
            item_type: Type of item
            item_id: Item ID
            action: Action on the item
        """
        super().__init__('item', (item_type, item_id, action))


class Identity:
    """
    Identity for authorization.
    
    An identity represents a user and their authorization needs.
    """
    
    def __init__(self, id: str, auth_type: str = 'session'):
        """
        Initialize an identity.
        
        Args:
            id: Identity ID (usually user ID)
            auth_type: Authentication type
        """
        self.id = id
        self.auth_type = auth_type
        self.provides = set()
    
    def can(self, permission: 'Permission') -> bool:
        """
        Check if the identity has a permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if the identity has the permission, False otherwise
        """
        return permission.allows(self)
    
    def __repr__(self):
        return f"<Identity id={self.id}>"


class AnonymousIdentity(Identity):
    """
    Anonymous identity.
    
    This identity is used when no user is authenticated.
    """
    
    def __init__(self):
        """
        Initialize an anonymous identity.
        """
        super().__init__(id='anonymous', auth_type='anonymous')


class Permission:
    """
    Permission for authorization.
    
    A permission is a set of needs that must be satisfied for access to be granted.
    """
    
    def __init__(self, *needs: Need):
        """
        Initialize a permission.
        
        Args:
            *needs: Needs required for this permission
        """
        self.needs = set(needs)
    
    def allows(self, identity: Identity) -> bool:
        """
        Check if an identity satisfies this permission.
        
        Args:
            identity: Identity to check
            
        Returns:
            True if the identity satisfies the permission, False otherwise
        """
        # If no needs are specified, allow access
        if not self.needs:
            return True
        
        # Check if any of the needs are provided by the identity
        return bool(self.needs.intersection(identity.provides))
    
    def require(self, http_exception: int = 403):
        """
        Decorator to require this permission for a route.
        
        Args:
            http_exception: HTTP status code to return if permission is denied
            
        Returns:
            Decorated function
        """
        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                # Get current identity
                identity = get_current_identity()
                
                # Check permission
                if not self.allows(identity):
                    principal_logger.warning(f"Permission denied for identity: {identity.id}")
                    return Response(
                        status=http_exception,
                        body={"error": "Permission denied"},
                        content_type="application/json"
                    )
                
                # Permission granted, call the original function
                principal_logger.debug(f"Permission granted for identity: {identity.id}")
                return f(*args, **kwargs)
            
            return decorated_function
        
        return decorator
    
    def union(self, other: 'Permission') -> 'Permission':
        """
        Create a new permission that is the union of this permission and another.
        
        Args:
            other: Other permission
            
        Returns:
            New permission
        """
        return Permission(*self.needs.union(other.needs))
    
    def __or__(self, other: 'Permission') -> 'Permission':
        """
        Create a new permission that is the union of this permission and another.
        
        Args:
            other: Other permission
            
        Returns:
            New permission
        """
        return self.union(other)
    
    def __repr__(self):
        return f"<Permission needs={self.needs}>"


class Principal:
    """
    Principal for ProAPI.
    
    This class manages role-based access control for ProAPI applications.
    """
    
    def __init__(self, app=None):
        """
        Initialize the principal.
        
        Args:
            app: ProAPI application (optional)
        """
        self.app = app
        self._identity_loader = None
        
        principal_logger.info("Principal initialized")
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the principal with an application.
        
        Args:
            app: ProAPI application
        """
        self.app = app
        
        # Add principal middleware
        app.use(self._principal_middleware)
        principal_logger.debug("Added principal middleware to application")
        
        # Store principal in app for access from routes
        app._principal = self
        principal_logger.info(f"Principal initialized for application: {app.__class__.__name__}")
    
    def identity_loader(self, callback: Callable) -> Callable:
        """
        Decorator to register an identity loader function.
        
        The identity loader function is called to load the identity for the
        current request.
        
        Args:
            callback: Function that returns an identity
            
        Returns:
            The callback function
        """
        self._identity_loader = callback
        principal_logger.info(f"Identity loader function registered: {callback.__name__}")
        return callback
    
    def _principal_middleware(self, request):
        """
        Principal middleware.
        
        This middleware loads the identity for the current request.
        
        Args:
            request: HTTP request
            
        Returns:
            Modified request
        """
        # Clear identity for this request
        clear_identity()
        
        # Load identity
        identity_data = None
        if self._identity_loader:
            try:
                identity_data = self._identity_loader()
                principal_logger.debug(f"Identity loaded: {identity_data}")
            except Exception as e:
                principal_logger.error(f"Error loading identity: {str(e)}")
        
        # Create identity
        if identity_data:
            identity = Identity(id=str(identity_data.get('user_id', 'anonymous')))
            
            # Add user need
            identity.provides.add(UserNeed(identity.id))
            
            # Add role needs
            roles = identity_data.get('roles', [])
            for role in roles:
                identity.provides.add(RoleNeed(role))
            
            # Add action needs
            actions = identity_data.get('actions', [])
            for action in actions:
                identity.provides.add(ActionNeed(action))
            
            # Add item needs
            items = identity_data.get('items', [])
            for item in items:
                if len(item) == 3:
                    item_type, item_id, action = item
                    identity.provides.add(ItemNeed(item_type, item_id, action))
            
            # Set identity
            set_identity(identity)
            principal_logger.debug(f"Identity set: {identity.id} with {len(identity.provides)} needs")
        else:
            # Set anonymous identity
            set_identity(AnonymousIdentity())
            principal_logger.debug("Anonymous identity set")
        
        return request


def set_identity(identity: Identity):
    """
    Set the identity for the current request.
    
    Args:
        identity: Identity
    """
    _identity_local.identity = identity


def get_current_identity() -> Identity:
    """
    Get the identity for the current request.
    
    Returns:
        Identity or AnonymousIdentity if not set
    """
    return getattr(_identity_local, 'identity', AnonymousIdentity())


def clear_identity():
    """
    Clear the identity for the current request.
    """
    if hasattr(_identity_local, 'identity'):
        delattr(_identity_local, 'identity')


# Create some common permissions
admin_permission = Permission(RoleNeed('admin'))
"""Permission that requires the 'admin' role."""

authenticated_permission = Permission(UserNeed('authenticated'))
"""Permission that requires an authenticated user."""
