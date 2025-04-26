"""
JWT Authentication for ProAPI.

This module provides JWT (JSON Web Token) authentication for ProAPI applications.
It allows you to:
- Generate JWT tokens for users
- Verify JWT tokens
- Protect routes with JWT authentication
- Access authenticated users in route handlers
- Refresh tokens
- Blacklist tokens

Example:
    from proapi import ProAPI
    from proapi.auth.jwt import JWTManager, jwt_required, create_access_token

    app = ProAPI()
    jwt = JWTManager(app, secret_key="your-secret-key")

    @app.post("/login")
    def login(request):
        username = request.json.get("username")
        password = request.json.get("password")
        
        # Check username and password
        if username == 'admin' and password == 'secret':
            # Create access token
            access_token = create_access_token(identity=username)
            return {"access_token": access_token}
        
        return {"error": "Invalid credentials"}, 401

    @app.get("/protected")
    @jwt_required
    def protected(request):
        # Access the current user
        from proapi.auth.jwt import get_jwt_identity
        current_user = get_jwt_identity()
        return {"message": f"Hello, {current_user}!"}
"""

import base64
import datetime
import functools
import hmac
import json
import time
from typing import Any, Callable, Dict, List, Optional, Union

from proapi.server.server import Request, Response
from proapi.routing.request_proxy import get_current_request
from proapi.core.logging import app_logger

# Use app_logger with a specific context for JWT logs
jwt_logger = app_logger.bind(context="jwt")

# Thread-local storage for JWT data
import threading
_jwt_local = threading.local()


class JWTManager:
    """
    JWT Manager for ProAPI.
    
    This class manages JWT authentication for ProAPI applications.
    """
    
    def __init__(self, app=None, secret_key: str = None, algorithm: str = 'HS256',
                 access_token_expires: int = 3600, refresh_token_expires: int = 86400,
                 blacklist_enabled: bool = False):
        """
        Initialize the JWT manager.
        
        Args:
            app: ProAPI application (optional)
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
            access_token_expires: Access token expiration time in seconds (default: 1 hour)
            refresh_token_expires: Refresh token expiration time in seconds (default: 24 hours)
            blacklist_enabled: Whether to enable token blacklisting (default: False)
        """
        self.app = app
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expires = access_token_expires
        self.refresh_token_expires = refresh_token_expires
        self.blacklist_enabled = blacklist_enabled
        self.blacklist = set()
        self._token_verification_callback = None
        self._token_in_blacklist_callback = None
        
        jwt_logger.info("JWTManager initialized")
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the JWT manager with an application.
        
        Args:
            app: ProAPI application
        """
        self.app = app
        
        # Get secret key from app if not provided
        if self.secret_key is None:
            self.secret_key = getattr(app, 'secret_key', None)
            if self.secret_key is None:
                jwt_logger.warning(
                    "No secret key provided. JWT authentication requires a secret key. "
                    "Set it when creating the JWTManager or in the app configuration."
                )
        
        # Add JWT middleware
        app.use(self._jwt_middleware)
        jwt_logger.debug("Added JWT middleware to application")
        
        # Store JWT manager in app for access from routes
        app._jwt_manager = self
        jwt_logger.info(f"JWTManager initialized for application: {app.__class__.__name__}")
    
    def _jwt_middleware(self, request):
        """
        JWT middleware.
        
        This middleware extracts the JWT token from the request and verifies it.
        
        Args:
            request: HTTP request
            
        Returns:
            Modified request
        """
        # Clear JWT data for this request
        clear_jwt_data()
        
        # Get JWT token from request
        token = self._get_token_from_request(request)
        if not token:
            jwt_logger.debug("No JWT token found in request")
            return request
        
        # Verify token
        try:
            payload = self._verify_token(token)
            if payload:
                # Store JWT data for this request
                set_jwt_data(payload)
                jwt_logger.debug(f"JWT token verified for user: {payload.get('sub')}")
        except Exception as e:
            jwt_logger.warning(f"JWT token verification failed: {str(e)}")
        
        return request
    
    def _get_token_from_request(self, request) -> Optional[str]:
        """
        Get the JWT token from the request.
        
        Args:
            request: HTTP request
            
        Returns:
            JWT token or None if not found
        """
        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer '
        
        # Check query parameters
        token = request.query_params.get('token')
        if token:
            return token
        
        # Check cookies
        if hasattr(request, 'cookies'):
            token = request.cookies.get('access_token')
            if token:
                return token
        
        return None
    
    def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Token payload or None if verification fails
        """
        if not token:
            return None
        
        # Check if token is in blacklist
        if self.blacklist_enabled and self._is_token_blacklisted(token):
            jwt_logger.warning("Token is blacklisted")
            return None
        
        try:
            # Parse token
            header_b64, payload_b64, signature_b64 = token.split('.')
            
            # Decode header and payload
            header = json.loads(base64.urlsafe_b64decode(header_b64 + '=' * (4 - len(header_b64) % 4)).decode('utf-8'))
            payload = json.loads(base64.urlsafe_b64decode(payload_b64 + '=' * (4 - len(payload_b64) % 4)).decode('utf-8'))
            
            # Verify algorithm
            if header.get('alg') != self.algorithm:
                jwt_logger.warning(f"Invalid algorithm: {header.get('alg')}")
                return None
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            signature = base64.urlsafe_b64decode(signature_b64 + '=' * (4 - len(signature_b64) % 4))
            
            if not self._verify_signature(message, signature):
                jwt_logger.warning("Invalid signature")
                return None
            
            # Verify expiration
            if 'exp' in payload and payload['exp'] < time.time():
                jwt_logger.warning("Token has expired")
                return None
            
            # Verify not before
            if 'nbf' in payload and payload['nbf'] > time.time():
                jwt_logger.warning("Token is not yet valid")
                return None
            
            # Custom verification
            if self._token_verification_callback:
                if not self._token_verification_callback(payload):
                    jwt_logger.warning("Custom token verification failed")
                    return None
            
            return payload
        except Exception as e:
            jwt_logger.error(f"Token verification error: {str(e)}")
            return None
    
    def _verify_signature(self, message: str, signature: bytes) -> bool:
        """
        Verify the signature of a JWT token.
        
        Args:
            message: Message to verify
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if self.algorithm == 'HS256':
            key = self.secret_key.encode('utf-8')
            expected_signature = hmac.new(key, message.encode('utf-8'), 'sha256').digest()
            return hmac.compare_digest(signature, expected_signature)
        
        # Add support for other algorithms as needed
        jwt_logger.warning(f"Unsupported algorithm: {self.algorithm}")
        return False
    
    def _is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            token: JWT token
            
        Returns:
            True if token is blacklisted, False otherwise
        """
        if not self.blacklist_enabled:
            return False
        
        if self._token_in_blacklist_callback:
            return self._token_in_blacklist_callback(token)
        
        return token in self.blacklist
    
    def token_in_blacklist_loader(self, callback: Callable) -> Callable:
        """
        Decorator to register a callback for checking if a token is in the blacklist.
        
        Args:
            callback: Callback function
            
        Returns:
            The callback function
        """
        self._token_in_blacklist_callback = callback
        jwt_logger.debug(f"Registered token blacklist callback: {callback.__name__}")
        return callback
    
    def token_verification_loader(self, callback: Callable) -> Callable:
        """
        Decorator to register a callback for custom token verification.
        
        Args:
            callback: Callback function
            
        Returns:
            The callback function
        """
        self._token_verification_callback = callback
        jwt_logger.debug(f"Registered token verification callback: {callback.__name__}")
        return callback
    
    def create_access_token(self, identity: Any, expires_delta: Optional[int] = None,
                           fresh: bool = False, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create an access token.
        
        Args:
            identity: User identity
            expires_delta: Token expiration time in seconds (overrides default)
            fresh: Whether the token is fresh
            additional_claims: Additional claims to include in the token
            
        Returns:
            JWT token
        """
        return create_token(
            identity=identity,
            token_type='access',
            expires_delta=expires_delta or self.access_token_expires,
            fresh=fresh,
            additional_claims=additional_claims,
            secret_key=self.secret_key,
            algorithm=self.algorithm
        )
    
    def create_refresh_token(self, identity: Any, expires_delta: Optional[int] = None,
                            additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a refresh token.
        
        Args:
            identity: User identity
            expires_delta: Token expiration time in seconds (overrides default)
            additional_claims: Additional claims to include in the token
            
        Returns:
            JWT token
        """
        return create_token(
            identity=identity,
            token_type='refresh',
            expires_delta=expires_delta or self.refresh_token_expires,
            additional_claims=additional_claims,
            secret_key=self.secret_key,
            algorithm=self.algorithm
        )
    
    def blacklist_token(self, token: str):
        """
        Add a token to the blacklist.
        
        Args:
            token: JWT token
        """
        if not self.blacklist_enabled:
            jwt_logger.warning("Token blacklisting is not enabled")
            return
        
        self.blacklist.add(token)
        jwt_logger.debug("Token added to blacklist")


def create_token(identity: Any, token_type: str, expires_delta: int,
                fresh: bool = False, additional_claims: Optional[Dict[str, Any]] = None,
                secret_key: str = None, algorithm: str = 'HS256') -> str:
    """
    Create a JWT token.
    
    Args:
        identity: User identity
        token_type: Token type ('access' or 'refresh')
        expires_delta: Token expiration time in seconds
        fresh: Whether the token is fresh (only for access tokens)
        additional_claims: Additional claims to include in the token
        secret_key: Secret key for signing the token
        algorithm: JWT algorithm
        
    Returns:
        JWT token
    """
    # Get current time
    now = datetime.datetime.utcnow()
    
    # Create payload
    payload = {
        'iat': int(now.timestamp()),  # Issued at
        'nbf': int(now.timestamp()),  # Not before
        'exp': int((now + datetime.timedelta(seconds=expires_delta)).timestamp()),  # Expiration
        'sub': str(identity),  # Subject (user identity)
        'type': token_type  # Token type
    }
    
    # Add fresh claim for access tokens
    if token_type == 'access' and fresh:
        payload['fresh'] = True
    
    # Add additional claims
    if additional_claims:
        payload.update(additional_claims)
    
    # Create header
    header = {
        'alg': algorithm,
        'typ': 'JWT'
    }
    
    # Encode header and payload
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode('utf-8')).decode('utf-8').rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8').rstrip('=')
    
    # Create signature
    message = f"{header_b64}.{payload_b64}"
    key = secret_key.encode('utf-8')
    
    if algorithm == 'HS256':
        signature = hmac.new(key, message.encode('utf-8'), 'sha256').digest()
    else:
        jwt_logger.warning(f"Unsupported algorithm: {algorithm}")
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    # Encode signature
    signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    # Create token
    token = f"{header_b64}.{payload_b64}.{signature_b64}"
    
    return token


def set_jwt_data(data: Dict[str, Any]):
    """
    Set JWT data for the current request.
    
    Args:
        data: JWT data
    """
    _jwt_local.jwt_data = data


def get_jwt_data() -> Optional[Dict[str, Any]]:
    """
    Get JWT data for the current request.
    
    Returns:
        JWT data or None if not set
    """
    return getattr(_jwt_local, 'jwt_data', None)


def clear_jwt_data():
    """
    Clear JWT data for the current request.
    """
    if hasattr(_jwt_local, 'jwt_data'):
        delattr(_jwt_local, 'jwt_data')


def get_jwt_identity() -> Optional[Any]:
    """
    Get the identity from the JWT token.
    
    Returns:
        User identity or None if not set
    """
    jwt_data = get_jwt_data()
    if jwt_data:
        return jwt_data.get('sub')
    return None


def get_jwt() -> Optional[Dict[str, Any]]:
    """
    Get the JWT token data.
    
    Returns:
        JWT token data or None if not set
    """
    return get_jwt_data()


def jwt_required(func=None, fresh=False, refresh=False, optional=False):
    """
    Decorator to require JWT authentication for a route.
    
    Args:
        func: Route function
        fresh: Whether to require a fresh token
        refresh: Whether to require a refresh token
        optional: Whether authentication is optional
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Get JWT data
            jwt_data = get_jwt_data()
            
            # Check if JWT data is available
            if not jwt_data:
                if optional:
                    jwt_logger.debug("JWT authentication is optional, proceeding without authentication")
                    return f(*args, **kwargs)
                
                jwt_logger.warning("No JWT token found or token is invalid")
                return Response(
                    status=401,
                    body={"error": "Missing or invalid JWT token"},
                    content_type="application/json"
                )
            
            # Check token type
            token_type = jwt_data.get('type')
            if refresh and token_type != 'refresh':
                jwt_logger.warning("Refresh token required but access token provided")
                return Response(
                    status=401,
                    body={"error": "Refresh token required"},
                    content_type="application/json"
                )
            
            if not refresh and token_type != 'access':
                jwt_logger.warning("Access token required but refresh token provided")
                return Response(
                    status=401,
                    body={"error": "Access token required"},
                    content_type="application/json"
                )
            
            # Check if token is fresh
            if fresh and not jwt_data.get('fresh', False):
                jwt_logger.warning("Fresh token required but non-fresh token provided")
                return Response(
                    status=401,
                    body={"error": "Fresh token required"},
                    content_type="application/json"
                )
            
            # Token is valid, call the original function
            jwt_logger.debug(f"JWT authentication successful for user: {jwt_data.get('sub')}")
            return f(*args, **kwargs)
        
        return decorated_function
    
    # Handle both @jwt_required and @jwt_required(fresh=True)
    if func:
        return decorator(func)
    return decorator


def create_access_token(identity: Any, expires_delta: Optional[int] = None,
                       fresh: bool = False, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Create an access token.
    
    Args:
        identity: User identity
        expires_delta: Token expiration time in seconds
        fresh: Whether the token is fresh
        additional_claims: Additional claims to include in the token
        
    Returns:
        JWT token
    """
    # Get request
    request = get_current_request()
    if not request:
        jwt_logger.error("No request available")
        raise RuntimeError("No request available")
    
    # Get JWT manager
    if not hasattr(request, 'app') or not hasattr(request.app, '_jwt_manager'):
        jwt_logger.error("No JWT manager available")
        raise RuntimeError("No JWT manager available")
    
    jwt_manager = request.app._jwt_manager
    
    return jwt_manager.create_access_token(
        identity=identity,
        expires_delta=expires_delta,
        fresh=fresh,
        additional_claims=additional_claims
    )


def create_refresh_token(identity: Any, expires_delta: Optional[int] = None,
                        additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a refresh token.
    
    Args:
        identity: User identity
        expires_delta: Token expiration time in seconds
        additional_claims: Additional claims to include in the token
        
    Returns:
        JWT token
    """
    # Get request
    request = get_current_request()
    if not request:
        jwt_logger.error("No request available")
        raise RuntimeError("No request available")
    
    # Get JWT manager
    if not hasattr(request, 'app') or not hasattr(request.app, '_jwt_manager'):
        jwt_logger.error("No JWT manager available")
        raise RuntimeError("No JWT manager available")
    
    jwt_manager = request.app._jwt_manager
    
    return jwt_manager.create_refresh_token(
        identity=identity,
        expires_delta=expires_delta,
        additional_claims=additional_claims
    )
