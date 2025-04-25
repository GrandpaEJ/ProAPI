"""
Middleware module for ProAPI framework.

Provides middleware functionality for request/response processing.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from .logging import app_logger

class MiddlewareManager:
    """
    Manages middleware for the application.
    """

    def __init__(self):
        """Initialize the middleware manager"""
        self.middleware = []

    def add(self, middleware_func: Callable):
        """
        Add middleware to the chain.

        Args:
            middleware_func: Middleware function
        """
        self.middleware.append(middleware_func)

    def apply(self, request):
        """
        Apply all middleware to a request.

        Args:
            request: Request object

        Returns:
            Modified request or response
        """
        result = request
        for middleware in self.middleware:
            result = middleware(result)
            # If middleware returns a response, short-circuit
            if hasattr(result, 'status'):
                break
        return result

# Built-in middleware

def cors_middleware(allowed_origins="*", allowed_methods=None, allowed_headers=None):
    """
    CORS middleware factory.

    Args:
        allowed_origins: Allowed origins (string or list)
        allowed_methods: Allowed methods (list)
        allowed_headers: Allowed headers (list)

    Returns:
        Middleware function
    """
    if allowed_methods is None:
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]

    if allowed_headers is None:
        allowed_headers = ["Content-Type", "Authorization"]

    def middleware(request):
        from .server import Response

        # Handle preflight requests
        if request.method == "OPTIONS":
            headers = {
                "Access-Control-Allow-Origin": "*" if allowed_origins == "*" else ", ".join(allowed_origins),
                "Access-Control-Allow-Methods": ", ".join(allowed_methods),
                "Access-Control-Allow-Headers": ", ".join(allowed_headers),
                "Access-Control-Max-Age": "86400",  # 24 hours
            }
            return Response(status=204, headers=headers)

        # For regular requests, just add the CORS headers
        # The actual headers will be added to the response later
        request.cors_headers = {
            "Access-Control-Allow-Origin": "*" if allowed_origins == "*" else ", ".join(allowed_origins),
        }

        return request

    return middleware

def logging_middleware(log_format=None, level="INFO"):
    """
    Logging middleware factory using Loguru.

    Args:
        log_format: Format string for log messages
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Middleware function
    """
    if log_format is None:
        log_format = "[{time}] {method} {path} - {status} ({duration:.3f}s)"

    def middleware(request):
        # Store start time
        request.start_time = time.time()

        # Log the request
        app_logger.log(level, f"Request: {request.method} {request.path}")

        # Add a hook to log after the response is generated
        def log_response(response):
            duration = time.time() - request.start_time
            log_message = log_format.format(
                time=time.strftime("%Y-%m-%d %H:%M:%S"),
                method=request.method,
                path=request.path,
                status=response.status,
                duration=duration
            )

            # Log the response with the appropriate level
            if response.status >= 500:
                app_logger.error(f"Response: {log_message}")
            elif response.status >= 400:
                app_logger.warning(f"Response: {log_message}")
            else:
                app_logger.log(level, f"Response: {log_message}")

            return response

        request.log_response = log_response

        return request

    return middleware

def static_files_middleware(static_dir="static", url_prefix="/static"):
    """
    Static files middleware factory.

    Args:
        static_dir: Directory containing static files
        url_prefix: URL prefix for static files

    Returns:
        Middleware function
    """
    import os
    import mimetypes

    def middleware(request):
        from .server import Response

        # Check if the request is for a static file
        if request.path.startswith(url_prefix):
            # Get the file path
            file_path = request.path[len(url_prefix):].lstrip('/')
            full_path = os.path.join(static_dir, file_path)

            # Check if the file exists
            if os.path.isfile(full_path):
                # Get the content type
                content_type, _ = mimetypes.guess_type(full_path)
                if content_type is None:
                    content_type = "application/octet-stream"

                # Read the file
                with open(full_path, 'rb') as f:
                    content = f.read()

                # Return the response
                return Response(
                    body=content,
                    content_type=content_type
                )

        return request

    return middleware

def compression_middleware(min_size=1024, level=6):
    """
    Compression middleware factory.

    Args:
        min_size: Minimum size for compression (bytes)
        level: Compression level (1-9)

    Returns:
        Middleware function
    """
    try:
        import gzip
        import zlib
        has_compression = True
    except ImportError:
        has_compression = False

    def middleware(request):
        if not has_compression:
            return request

        # Store original _process_result method
        original_process_result = request.app._process_result

        # Override _process_result to add compression
        def compressed_process_result(result):
            from .server import Response

            # Get the original response
            response = original_process_result(result)

            # Check if the client accepts gzip
            accepts_gzip = 'gzip' in request.headers.get('Accept-Encoding', '')

            # Check if the response should be compressed
            if (accepts_gzip and
                isinstance(response.body, (str, bytes)) and
                'Content-Encoding' not in response.headers and
                len(response.body) >= min_size):

                # Convert string to bytes if needed
                body_bytes = response.body.encode('utf-8') if isinstance(response.body, str) else response.body

                # Compress the body
                compressed_body = gzip.compress(body_bytes, level)

                # Update the response
                response.body = compressed_body
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = str(len(compressed_body))
                response.headers['Vary'] = 'Accept-Encoding'

            return response

        # Replace the method
        request.app._process_result = compressed_process_result

        return request

    return middleware
