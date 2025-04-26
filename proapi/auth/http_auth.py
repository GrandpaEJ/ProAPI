"""
HTTP Authentication for ProAPI.

This module provides HTTP Basic and Digest authentication for ProAPI applications.
It allows you to:
- Protect routes with HTTP Basic authentication
- Protect routes with HTTP Digest authentication
- Customize authentication callbacks
- Access authenticated users in route handlers

Example:
    from proapi import ProAPI
    from proapi.auth.http_auth import HTTPBasicAuth, HTTPDigestAuth

    app = ProAPI()
    basic_auth = HTTPBasicAuth()
    digest_auth = HTTPDigestAuth()

    @basic_auth.verify_password
    def verify_password(username, password):
        # Check username and password
        if username == 'admin' and password == 'secret':
            return username
        return None

    @app.get("/basic-auth")
    @basic_auth.login_required
    def basic_protected(request):
        return {"message": f"Hello, {basic_auth.current_user}!"}

    @digest_auth.verify_password
    def verify_digest_password(username, password):
        # Check username and password
        if username == 'admin' and password == 'secret':
            return username
        return None

    @app.get("/digest-auth")
    @digest_auth.login_required
    def digest_protected(request):
        return {"message": f"Hello, {digest_auth.current_user}!"}
"""

import base64
import functools
import hashlib
import os
import time
from typing import Any, Callable, Dict, Optional, Union

from proapi.server.server import Request, Response
from proapi.routing.request_proxy import get_current_request
from proapi.core.logging import app_logger

# Use app_logger with a specific context for HTTP auth logs
http_auth_logger = app_logger.bind(context="http_auth")


class HTTPAuth:
    """
    Base class for HTTP authentication.
    
    This class provides the base functionality for HTTP authentication methods.
    It should be subclassed to implement specific authentication schemes.
    """
    
    def __init__(self, scheme: str = None, realm: str = "Authentication Required"):
        """
        Initialize the HTTP authentication.
        
        Args:
            scheme: Authentication scheme (e.g., "Basic", "Digest")
            realm: Authentication realm
        """
        self.scheme = scheme
        self.realm = realm
        self._verify_callback = None
        self._error_handler = None
        self._current_user = None
        
        http_auth_logger.debug(f"Initialized {self.__class__.__name__} with realm: {realm}")
    
    def verify_callback(self, callback: Callable) -> Callable:
        """
        Decorator to register a verification callback.
        
        Args:
            callback: Verification callback function
            
        Returns:
            The callback function
        """
        self._verify_callback = callback
        http_auth_logger.debug(f"Registered verification callback: {callback.__name__}")
        return callback
    
    def error_handler(self, callback: Callable) -> Callable:
        """
        Decorator to register an error handler.
        
        Args:
            callback: Error handler function
            
        Returns:
            The callback function
        """
        self._error_handler = callback
        http_auth_logger.debug(f"Registered error handler: {callback.__name__}")
        return callback
    
    def login_required(self, func: Callable) -> Callable:
        """
        Decorator to require authentication for a route.
        
        Args:
            func: Route function
            
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            auth_header = self.get_auth_header()
            
            if not auth_header:
                http_auth_logger.warning("No authentication header found")
                return self.auth_error_response()
            
            try:
                user = self.authenticate(auth_header)
                if not user:
                    http_auth_logger.warning("Authentication failed")
                    return self.auth_error_response()
                
                # Store the authenticated user
                self._current_user = user
                http_auth_logger.debug(f"Authentication successful for user: {user}")
                
                # Call the route function
                return func(*args, **kwargs)
            except Exception as e:
                http_auth_logger.error(f"Authentication error: {str(e)}")
                return self.auth_error_response()
            finally:
                # Clear the current user
                self._current_user = None
        
        return decorated
    
    def get_auth_header(self) -> Optional[str]:
        """
        Get the authentication header from the request.
        
        Returns:
            Authentication header or None if not found
        """
        request = get_current_request()
        if not request:
            http_auth_logger.error("No request available")
            return None
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            http_auth_logger.debug("No Authorization header found")
            return None
        
        return auth_header
    
    def authenticate(self, auth_header: str) -> Any:
        """
        Authenticate a request.
        
        Args:
            auth_header: Authentication header
            
        Returns:
            User object or None if authentication fails
        """
        raise NotImplementedError("Subclasses must implement authenticate()")
    
    def auth_error_response(self) -> Response:
        """
        Create an authentication error response.
        
        Returns:
            Response object
        """
        if self._error_handler:
            return self._error_handler()
        
        headers = {
            'WWW-Authenticate': f'{self.scheme} realm="{self.realm}"'
        }
        
        return Response(
            status=401,
            body={"error": "Unauthorized"},
            content_type="application/json",
            headers=headers
        )
    
    @property
    def current_user(self) -> Any:
        """
        Get the current authenticated user.
        
        Returns:
            Current authenticated user
        """
        return self._current_user


class HTTPBasicAuth(HTTPAuth):
    """
    HTTP Basic authentication.
    
    This class provides HTTP Basic authentication for ProAPI applications.
    """
    
    def __init__(self, realm: str = "Authentication Required"):
        """
        Initialize the HTTP Basic authentication.
        
        Args:
            realm: Authentication realm
        """
        super().__init__(scheme="Basic", realm=realm)
        http_auth_logger.debug("Initialized HTTPBasicAuth")
    
    def verify_password(self, callback: Callable) -> Callable:
        """
        Decorator to register a password verification callback.
        
        Args:
            callback: Password verification callback function
            
        Returns:
            The callback function
        """
        self._verify_callback = callback
        http_auth_logger.debug(f"Registered password verification callback: {callback.__name__}")
        return callback
    
    def authenticate(self, auth_header: str) -> Any:
        """
        Authenticate a request with HTTP Basic authentication.
        
        Args:
            auth_header: Authentication header
            
        Returns:
            User object or None if authentication fails
        """
        if not auth_header.startswith('Basic '):
            http_auth_logger.warning("Invalid Basic authentication header")
            return None
        
        try:
            # Extract and decode the credentials
            encoded = auth_header[6:]  # Remove 'Basic '
            decoded = base64.b64decode(encoded).decode('utf-8')
            username, password = decoded.split(':', 1)
            
            # Verify the credentials
            if not self._verify_callback:
                http_auth_logger.error("No password verification callback registered")
                raise ValueError("No password verification callback registered")
            
            user = self._verify_callback(username, password)
            if user:
                http_auth_logger.debug(f"Basic authentication successful for user: {username}")
                return user
            
            http_auth_logger.warning(f"Basic authentication failed for user: {username}")
            return None
        except Exception as e:
            http_auth_logger.error(f"Basic authentication error: {str(e)}")
            return None


class HTTPDigestAuth(HTTPAuth):
    """
    HTTP Digest authentication.
    
    This class provides HTTP Digest authentication for ProAPI applications.
    """
    
    def __init__(self, realm: str = "Authentication Required", algorithm: str = 'md5'):
        """
        Initialize the HTTP Digest authentication.
        
        Args:
            realm: Authentication realm
            algorithm: Digest algorithm (md5, sha-256, etc.)
        """
        super().__init__(scheme="Digest", realm=realm)
        self.algorithm = algorithm
        self.nonce = {}
        self.opaque = base64.b64encode(os.urandom(16)).decode('utf-8')
        http_auth_logger.debug(f"Initialized HTTPDigestAuth with algorithm: {algorithm}")
    
    def verify_password(self, callback: Callable) -> Callable:
        """
        Decorator to register a password verification callback.
        
        Args:
            callback: Password verification callback function
            
        Returns:
            The callback function
        """
        self._verify_callback = callback
        http_auth_logger.debug(f"Registered password verification callback: {callback.__name__}")
        return callback
    
    def generate_nonce(self) -> str:
        """
        Generate a nonce for Digest authentication.
        
        Returns:
            Nonce string
        """
        nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
        self.nonce[nonce] = time.time()
        return nonce
    
    def authenticate(self, auth_header: str) -> Any:
        """
        Authenticate a request with HTTP Digest authentication.
        
        Args:
            auth_header: Authentication header
            
        Returns:
            User object or None if authentication fails
        """
        if not auth_header.startswith('Digest '):
            http_auth_logger.warning("Invalid Digest authentication header")
            return None
        
        try:
            # Parse the Digest authentication header
            auth_dict = {}
            for item in auth_header[7:].split(','):
                key, value = item.strip().split('=', 1)
                auth_dict[key] = value.strip('"')
            
            # Extract the required fields
            username = auth_dict.get('username')
            realm = auth_dict.get('realm')
            nonce = auth_dict.get('nonce')
            uri = auth_dict.get('uri')
            response = auth_dict.get('response')
            
            if not all([username, realm, nonce, uri, response]):
                http_auth_logger.warning("Missing required Digest authentication fields")
                return None
            
            # Verify the nonce
            if nonce not in self.nonce:
                http_auth_logger.warning("Invalid nonce")
                return None
            
            # Check if the nonce is expired (30 minutes)
            if time.time() - self.nonce[nonce] > 1800:
                http_auth_logger.warning("Expired nonce")
                del self.nonce[nonce]
                return None
            
            # Verify the credentials
            if not self._verify_callback:
                http_auth_logger.error("No password verification callback registered")
                raise ValueError("No password verification callback registered")
            
            password = self._verify_callback(username)
            if not password:
                http_auth_logger.warning(f"Digest authentication failed for user: {username}")
                return None
            
            # Calculate the expected response
            request = get_current_request()
            method = request.method
            
            # Calculate HA1 = MD5(username:realm:password)
            ha1 = hashlib.md5(f"{username}:{realm}:{password}".encode('utf-8')).hexdigest()
            
            # Calculate HA2 = MD5(method:uri)
            ha2 = hashlib.md5(f"{method}:{uri}".encode('utf-8')).hexdigest()
            
            # Calculate the expected response
            expected_response = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode('utf-8')).hexdigest()
            
            if response == expected_response:
                http_auth_logger.debug(f"Digest authentication successful for user: {username}")
                return username
            
            http_auth_logger.warning(f"Digest authentication failed for user: {username}")
            return None
        except Exception as e:
            http_auth_logger.error(f"Digest authentication error: {str(e)}")
            return None
    
    def auth_error_response(self) -> Response:
        """
        Create a Digest authentication error response.
        
        Returns:
            Response object
        """
        if self._error_handler:
            return self._error_handler()
        
        nonce = self.generate_nonce()
        headers = {
            'WWW-Authenticate': (
                f'Digest realm="{self.realm}", '
                f'qop="auth", '
                f'nonce="{nonce}", '
                f'opaque="{self.opaque}", '
                f'algorithm="{self.algorithm}"'
            )
        }
        
        return Response(
            status=401,
            body={"error": "Unauthorized"},
            content_type="application/json",
            headers=headers
        )
