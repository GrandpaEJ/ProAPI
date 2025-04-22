"""
Core module for ProAPI framework.
"""

import json
import inspect
import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Type, Union
import traceback

from .routing import Route
from .templating import render, setup_jinja
from .logging import setup_logger, app_logger

T = TypeVar('T')

class ProAPI:
    """
    Main application class for ProAPI framework.

    ProAPI is designed to be:
    - Simpler than Flask/FastAPI with intuitive API design
    - Faster than FastAPI with optimized routing and request handling
    - Stable like Flask with robust error handling
    - Easy to use with minimal boilerplate

    Example:
        from proapi import ProAPI

        app = ProAPI()

        @app.get("/")
        def index(request):
            return {"message": "Hello, World!"}

        if __name__ == "__main__":
            app.run()
    """

    def __init__(self,
                 debug: bool = False,
                 env: str = "development",  # 'development', 'production', or 'testing'
                 template_dir: str = "templates",
                 static_dir: str = "static",
                 static_url: str = "/static",
                 enable_cors: bool = False,
                 enable_docs: bool = True,  # Default to True for better developer experience
                 docs_url: str = "/.docs",  # Changed default to /.docs
                 enable_sessions: bool = False,
                 session_secret_key: Optional[str] = None,
                 fast_mode: bool = False,  # New option for enabling fast mode by default
                 json_encoder: Optional[Type[json.JSONEncoder]] = None,
                 # Advanced options - most users won't need to change these
                 log_level: Optional[str] = None,  # Default will be based on env
                 log_file: Optional[str] = None,
                 workers: int = 1,
                 use_reloader: Optional[bool] = None,
                 # Performance and reliability options
                 protect_event_loop: bool = True,  # Protect against event loop blocking
                 auto_offload_blocking: bool = True,  # Auto-offload blocking operations
                 enable_overload_protection: bool = True,  # Enable graceful overload handling
                 auto_restart_workers: bool = True,  # Auto-restart workers on failure
                 max_concurrent_requests: int = 100,  # Maximum concurrent requests
                 request_queue_size: int = 1000):
        """
        Initialize the ProAPI application.

        Args:
            debug: Enable debug mode for detailed error messages and logging
            env: Environment ('development', 'production', or 'testing')
            template_dir: Directory for Jinja2 templates
            static_dir: Directory for static files
            static_url: URL prefix for static files
            enable_cors: Enable CORS headers for cross-origin requests
            enable_docs: Enable API documentation at /.docs
            docs_url: URL path for API documentation
            enable_sessions: Enable session support for user state
            session_secret_key: Secret key for signing session cookies (auto-generated if None)
            fast_mode: Enable optimized request handling for better performance
            json_encoder: Custom JSON encoder for response serialization
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (auto-configured based on environment)
            workers: Number of worker processes (for production)
            use_reloader: Enable auto-reloading when code changes (default: True in development)
            protect_event_loop: Enable protection against event loop blocking
            auto_offload_blocking: Automatically offload blocking operations to thread/process pools
            enable_overload_protection: Enable graceful handling of server overload
            auto_restart_workers: Automatically restart workers on failure
            max_concurrent_requests: Maximum number of concurrent requests
            request_queue_size: Maximum size of the request queue
        """
        # Store basic configuration
        self.debug = debug
        self.env = env.lower()
        self.template_dir = template_dir
        self.static_dir = static_dir
        self.static_url = static_url
        self.enable_cors = enable_cors
        self.enable_docs = enable_docs
        self.docs_url = docs_url
        self.docs_title = "API Documentation"
        self.json_encoder = json_encoder

        # Enable fast mode if specified
        self._fast_mode = fast_mode

        # Set forwarding defaults
        self.enable_forwarding = False
        self.forwarding_type = "cloudflare"

        # Store performance and reliability options
        self.protect_event_loop = protect_event_loop
        self.auto_offload_blocking = auto_offload_blocking
        self.enable_overload_protection = enable_overload_protection
        self.auto_restart_workers = auto_restart_workers
        self.max_concurrent_requests = max_concurrent_requests
        self.request_queue_size = request_queue_size

        # Session configuration
        self.enable_sessions = enable_sessions
        self.session_cookie_name = "session"
        self.session_max_age = 3600  # 1 hour
        self.session_http_only = True
        self.session_same_site = "Lax"
        self.session_backend = "memory"
        self.session_backend_options = {}

        # Set session_secure based on environment
        self.session_secure = (self.env == "production")

        # Generate a random secret key if not provided
        if enable_sessions and not session_secret_key:
            import secrets
            self.session_secret_key = secrets.token_hex(32)
            app_logger.warning("No session secret key provided. Using a randomly generated key.")
            app_logger.warning("This key will change on restart, invalidating all sessions.")
        else:
            self.session_secret_key = session_secret_key

        # Production configuration
        self.workers = workers
        self.request_timeout = 30  # Seconds
        self.max_request_size = 1024 * 1024  # 1MB
        self.trusted_hosts = []

        # Development configuration
        # Set default reloader setting based on environment
        if use_reloader is None:
            self.use_reloader = (self.env == "development" or self.debug)
        else:
            self.use_reloader = use_reloader

        # Set environment-specific defaults
        if self.env == "production":
            # In production, disable debug mode unless explicitly set
            if debug:
                app_logger.warning("Debug mode is enabled in production environment")

        # Logging configuration - set defaults based on environment
        if log_level is None:
            if self.env == "development" or self.debug:
                self.log_level = "DEBUG"
            elif self.env == "testing":
                self.log_level = "INFO"
            else:  # production
                self.log_level = "WARNING"
        else:
            self.log_level = log_level

        self.log_format = None  # Use default format
        self.log_file = log_file

        # For production, ensure we have a log file
        if self.env == "production" and self.log_file is None:
            import os
            os.makedirs("logs", exist_ok=True)
            self.log_file = "logs/proapi.log"
            app_logger.info(f"Auto-configured log file: {self.log_file}")

        # Setup logging
        setup_logger(
            level=self.log_level,
            format=self.log_format,
            sink=self.log_file
        )

        # Log initialization
        app_logger.info(f"ProAPI initialized (env={self.env}, debug={self.debug})")

        # Port forwarder
        self._forwarder = None

        # Setup routes
        self.routes: List[Route] = []

        # Setup WebSocket routes
        self.websocket_routes = []

        # Setup WebSocket middleware
        self.websocket_middleware = []

        # Setup middleware
        self.middleware: List[Callable] = []

        # Store current request for use in documentation
        self._current_request = None

        # Setup Jinja2 environment
        self.jinja_env = setup_jinja(template_dir)

        # Store current request for use in documentation
        self._current_request = None

        # Add static file middleware
        self._add_static_middleware()

        # Add documentation middleware if enabled
        if enable_docs:
            self._add_docs_middleware()

        # Always add default documentation at /.docs
        self._add_default_docs_middleware()

        # Add session middleware if enabled
        if enable_sessions:
            self._add_session_middleware()

        # Server instance
        self._server = None

    def get(self, path: str, **kwargs):
        """Decorator for GET routes"""
        return self._route_decorator("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        """Decorator for POST routes"""
        return self._route_decorator("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        """Decorator for PUT routes"""
        return self._route_decorator("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs):
        """Decorator for DELETE routes"""
        return self._route_decorator("DELETE", path, **kwargs)

    def patch(self, path: str, **kwargs):
        """Decorator for PATCH routes"""
        return self._route_decorator("PATCH", path, **kwargs)

    def websocket(self, path: str, **kwargs):
        """Decorator for WebSocket routes"""
        from .websocket import WebSocketRoute

        def decorator(handler):
            # Get route-specific middleware
            route_middlewares = kwargs.pop('middlewares', [])

            # Combine with global middleware
            all_middlewares = self.websocket_middleware + route_middlewares

            # Create WebSocket route with middleware
            route = WebSocketRoute(path, handler, middlewares=all_middlewares, **kwargs)
            self.websocket_routes.append(route)
            return handler
        return decorator

    def use_websocket(self, middleware):
        """Add middleware to WebSocket routes"""
        self.websocket_middleware.append(middleware)
        return middleware

    def _route_decorator(self, method: str, path: str, **kwargs):
        """Internal route decorator factory"""
        def decorator(handler):
            is_async = inspect.iscoroutinefunction(handler)
            route = Route(method, path, handler, is_async=is_async, **kwargs)
            self.routes.append(route)
            return handler
        return decorator

    def use(self, middleware_func: Callable):
        """Add middleware to the application"""
        self.middleware.append(middleware_func)
        return middleware_func

    def _add_static_middleware(self):
        """Add static file middleware"""
        import os
        import mimetypes

        @self.use
        def static_middleware(request):
            """Serve static files"""
            from .server import Response

            # Check if the request is for a static file
            if request.path.startswith(self.static_url):
                # Get the file path relative to the static directory
                rel_path = request.path[len(self.static_url):].lstrip('/')
                file_path = os.path.join(self.static_dir, rel_path)

                # Check if the file exists
                if os.path.isfile(file_path):
                    # Get the content type
                    content_type, _ = mimetypes.guess_type(file_path)
                    if content_type is None:
                        content_type = 'application/octet-stream'

                    # Read the file
                    with open(file_path, 'rb') as f:
                        content = f.read()

                    # Return the response
                    return Response(
                        body=content,
                        content_type=content_type
                    )

            # Not a static file, continue with request processing
            return request

    def _add_docs_middleware(self):
        """Add documentation middleware"""
        from .docs import DocsMiddleware

        # Create and add the middleware
        docs_middleware = DocsMiddleware(self, self.docs_url, self.docs_title)
        self.use(docs_middleware)

    def _add_default_docs_middleware(self):
        """Add default documentation middleware at /.docs"""
        from .docs import DocsMiddleware

        # Create and add the middleware with default settings
        default_docs_middleware = DocsMiddleware(self, "/.docs", "API Documentation")
        self.use(default_docs_middleware)

    def _add_session_middleware(self):
        """Add session middleware"""
        from .session import SessionManager, session_middleware

        # Create session manager
        session_manager = SessionManager(
            secret_key=self.session_secret_key,
            cookie_name=self.session_cookie_name,
            max_age=self.session_max_age,
            secure=self.session_secure,
            http_only=self.session_http_only,
            same_site=self.session_same_site,
            backend=self.session_backend,
            backend_options=self.session_backend_options
        )

        # Create and add session middleware
        self.use(session_middleware(session_manager))

        # Log session configuration
        app_logger.info(f"Session support enabled (backend: {self.session_backend})")
        if self.env == "production" and not self.session_secure:
            app_logger.warning("Session cookies are not secure in production environment")

    def run(self, host: str = None, port: int = 8000,
            workers: int = None, forward: bool = False,
            use_reloader: bool = None, debug: bool = None,
            fast: bool = None, **kwargs):
        """
        Run the application server.

        Args:
            host: Host to bind to (defaults to 127.0.0.1 in development, 0.0.0.0 in production)
            port: Port to bind to (defaults to 8000)
            workers: Number of worker processes (defaults to 1, or 2+ in production)
            forward: Enable port forwarding with Cloudflare
            use_reloader: Enable auto-reloading when code changes
            debug: Enable debug mode (overrides the instance setting)
            fast: Enable fast mode with optimized request handling
            **kwargs: Additional server options
        """
        from .server import create_server

        # Set defaults based on environment
        if host is None:
            if self.env == "production":
                host = "0.0.0.0"  # Bind to all interfaces in production
            else:
                host = "127.0.0.1"  # Localhost in development

        # Use instance workers setting if not specified
        if workers is None:
            workers = self.workers

        # Override debug mode if specified
        if debug is not None:
            self.debug = debug

        # Enable fast mode if specified
        if fast is not None:
            self._fast_mode = fast

        # Log fast mode status
        if self._fast_mode:
            app_logger.info(f"Running in fast mode with optimized performance")
            print(f"Running in fast mode with optimized performance")

            # Reset cache statistics if optimized module is available
            try:
                from .optimized import reset_cache_stats
                reset_cache_stats()
            except ImportError:
                app_logger.warning("Optimized module not available, falling back to standard mode")
                self._fast_mode = False

        # In production, ensure we have at least 2 workers
        if self.env == "production" and workers < 2:
            workers = 2
            app_logger.info(f"Increased workers to {workers} for production environment")

        # Determine server type based on environment
        server_type = "uvicorn"  # Always use uvicorn for better performance

        # Add production settings to kwargs
        if self.env == "production":
            kwargs.setdefault("request_timeout", self.request_timeout)
            kwargs.setdefault("max_request_size", self.max_request_size)
            if self.trusted_hosts:
                kwargs.setdefault("trusted_hosts", self.trusted_hosts)

        # Start the server
        app_logger.info(f"ProAPI server starting at http://{host}:{port}")
        app_logger.info(f"Environment: {self.env.upper()}")
        app_logger.info(f"Debug mode: {'ON' if self.debug else 'OFF'}")
        app_logger.info(f"Fast mode: {'ON' if self._fast_mode else 'OFF'}")
        app_logger.info(f"Workers: {workers}")

        # Print to console as well
        print(f"ProAPI server starting at http://{host}:{port}")
        print(f"Environment: {self.env.upper()}")
        print(f"Debug mode: {'ON' if self.debug else 'OFF'}")
        print(f"Fast mode: {'ON' if self._fast_mode else 'OFF'}")
        print(f"Workers: {workers}")

        # Start port forwarding if enabled
        if forward:
            try:
                from .forwarding import create_forwarder, get_local_ip

                # Use the local IP if host is 0.0.0.0
                local_host = get_local_ip() if host == "0.0.0.0" else host

                app_logger.info(f"Starting Cloudflare port forwarding...")
                print(f"Starting Cloudflare port forwarding...")

                # Create and start the forwarder
                self._forwarder = create_forwarder(port, local_host, "cloudflare")
                if self._forwarder.start():
                    # Wait for the public URL to be available
                    for _ in range(10):
                        if self._forwarder.public_url:
                            app_logger.success(f"Public URL: {self._forwarder.public_url}")
                            print(f"Public URL: {self._forwarder.public_url}")
                            break
                        time.sleep(0.5)
            except ImportError:
                app_logger.warning("Forwarding module not available. Install with: pip install proapi[cloudflare]")
                print("Forwarding module not available. Install with: pip install proapi[cloudflare]")
                self._forwarder = None
            except Exception as e:
                app_logger.exception(f"Error starting port forwarding: {e}")
                print(f"Error starting port forwarding: {e}")
                self._forwarder = None

        # Determine if reloader should be used
        should_use_reloader = use_reloader if use_reloader is not None else self.use_reloader

        # Initialize performance and reliability features
        if self.protect_event_loop:
            try:
                from .loop_protection import start_loop_monitoring
                start_loop_monitoring()
                app_logger.info("Event loop protection enabled")
            except ImportError:
                app_logger.warning("Event loop protection module not available")

        if self.enable_overload_protection:
            try:
                from .overload_handler import configure_overload_handler
                configure_overload_handler(
                    max_size=self.request_queue_size,
                    max_concurrent=self.max_concurrent_requests
                )
                app_logger.info(f"Overload protection enabled (max_concurrent={self.max_concurrent_requests}, queue_size={self.request_queue_size})")
            except ImportError:
                app_logger.warning("Overload protection module not available")

        # Configure blocking detection if enabled
        if self.auto_offload_blocking:
            try:
                from .blocking_handler import configure_blocking_detection
                configure_blocking_detection(auto_offload=True)
                app_logger.info("Automatic blocking operation detection and offloading enabled")
            except ImportError:
                app_logger.warning("Blocking detection module not available")

        # Create and start the server, passing the reloader option
        server_kwargs = kwargs.copy()

        # Add auto-restart option if enabled
        if self.auto_restart_workers and self.env == "production":
            server_kwargs["auto_restart"] = True
            app_logger.info("Worker auto-restart enabled")

        self._server = create_server(
            self, host, port, server_type, workers,
            use_reloader=should_use_reloader,
            **server_kwargs
        )

        try:
            self._server.start()
        except KeyboardInterrupt:
            app_logger.info("Server shutting down...")
            print("\nServer shutting down...")
        finally:
            # Stop the port forwarder
            if self._forwarder:
                app_logger.info("Stopping port forwarding...")
                print("Stopping port forwarding...")
                self._forwarder.stop()
                self._forwarder = None

            # Stop the server
            if hasattr(self._server, 'stop'):
                self._server.stop()

    def _start_forwarding(self, port: int, host: str, forwarding_type: str, kwargs: Dict[str, Any] = None):
        """
        Start port forwarding.

        Args:
            port: Port to forward
            host: Host to forward from
            forwarding_type: Type of port forwarding
        """
        from .forwarding import create_forwarder, get_local_ip

        # Use the local IP if host is 0.0.0.0
        local_host = get_local_ip() if host == "0.0.0.0" else host

        app_logger.info(f"Starting port forwarding ({forwarding_type})...")
        print(f"Starting port forwarding ({forwarding_type})...")

        try:
            # Create and start the forwarder
            self._forwarder = create_forwarder(port, local_host, forwarding_type, **(kwargs or {}))
            if self._forwarder.start():
                # Wait for the public URL to be available
                for _ in range(10):
                    if self._forwarder.public_url:
                        app_logger.success(f"Public URL: {self._forwarder.public_url}")
                        print(f"Public URL: {self._forwarder.public_url}")
                        return
                    time.sleep(0.5)

                app_logger.warning("Timeout waiting for public URL.")
                print("Timeout waiting for public URL.")
            else:
                app_logger.error(f"Failed to start port forwarding: {self._forwarder.error}")
                print(f"Failed to start port forwarding: {self._forwarder.error}")
                self._forwarder = None
        except Exception as e:
            app_logger.exception(f"Error starting port forwarding: {e}")
            print(f"Error starting port forwarding: {e}")
            self._forwarder = None

    def handle_request(self, request):
        """
        Process an incoming request through middleware and route handlers.

        Args:
            request: The request object

        Returns:
            Response object
        """
        from .server import Response
        from .request_proxy import set_current_request, clear_current_request

        # Store current request for use in documentation
        self._current_request = request

        # Set the current request in the request proxy
        set_current_request(request)

        try:
            # Apply middleware (pre-request)
            for middleware in self.middleware:
                request = middleware(request)
                if isinstance(request, Response):
                    return request

            # Find matching route (use optimized version if fast mode is enabled)
            if getattr(self, '_fast_mode', False):
                from .optimized import find_route_optimized, response_pool
                route, path_params = find_route_optimized(self.routes, request.method, request.path)

                if not route:
                    return response_pool.get(
                        status=404,
                        body=json.dumps({"error": "Not Found"}),
                        content_type="application/json"
                    )
            else:
                route = self._find_route(request.method, request.path)

                if not route:
                    return Response(
                        status=404,
                        body=json.dumps({"error": "Not Found"}),
                        content_type="application/json"
                    )

                # Extract path parameters (will be done later in the optimized version)
                path_params = route.extract_params(request.path)

            # Prepare handler arguments
            kwargs = {**path_params}

            # Add request to kwargs
            kwargs['request'] = request

            # Debug output
            if self.debug:
                app_logger.debug(f"Handler: {route.handler.__name__}")
                app_logger.debug(f"Path params: {path_params}")
                app_logger.debug(f"Kwargs: {kwargs}")

                # Also print to console in debug mode
                print(f"Handler: {route.handler.__name__}")
                print(f"Path params: {path_params}")
                print(f"Kwargs: {kwargs}")

            # Call the handler
            try:
                if route.is_async:
                    import asyncio
                    result = asyncio.run(route.handler(**kwargs))
                else:
                    result = route.handler(**kwargs)
            except TypeError as e:
                # Check if the error is due to unexpected 'request' argument
                if "got an unexpected keyword argument 'request'" in str(e):
                    # Remove the request parameter and try again
                    kwargs.pop('request', None)
                    if route.is_async:
                        import asyncio
                        result = asyncio.run(route.handler(**kwargs))
                    else:
                        result = route.handler(**kwargs)
                else:
                    # Re-raise the error if it's not related to the request parameter
                    raise

            # Process the result
            return self._process_result(result)

        except Exception as e:
            # Get traceback for logging
            traceback_str = traceback.format_exc()

            # Log the error with appropriate level based on environment
            if self.env == "production":
                # In production, log with error level but don't expose details
                app_logger.error(f"Error in handler: {str(e)}")
                app_logger.debug(traceback_str)  # Only log traceback at debug level
            else:
                # In development, log full details
                app_logger.error(f"Error: {str(e)}")
                app_logger.error(traceback_str)

                # Also print to console in debug mode
                if self.debug:
                    print(f"Error: {str(e)}")
                    print(traceback_str)

            # Create appropriate response based on environment
            if self.debug:
                # In debug mode, return detailed error information
                return Response(
                    status=500,
                    body=json.dumps({
                        "error": str(e),
                        "traceback": traceback_str,
                        "type": e.__class__.__name__
                    }),
                    content_type="application/json"
                )
            elif self.env == "testing":
                # In testing, return error message but no traceback
                return Response(
                    status=500,
                    body=json.dumps({
                        "error": str(e),
                        "type": e.__class__.__name__
                    }),
                    content_type="application/json"
                )
            else:
                # In production, return generic error message
                return Response(
                    status=500,
                    body=json.dumps({"error": "Internal Server Error"}),
                    content_type="application/json"
                )
        finally:
            # Clear the current request from the request proxy
            clear_current_request()

    def _find_route(self, method: str, path: str):
        """Find a matching route for the given method and path"""
        for route in self.routes:
            if route.match(method, path):
                return route
        return None

    def _process_result(self, result):
        """Process the result from a route handler"""
        from .server import Response

        # Use optimized processing if fast mode is enabled
        if getattr(self, '_fast_mode', False):
            from .optimized import process_json_optimized, response_pool, compress_response

            # If result is already a Response, return it
            if isinstance(result, Response):
                # Apply compression if needed
                if result.body and result.headers.get('Content-Type', '').startswith('text/') or \
                   result.headers.get('Content-Type', '').startswith('application/json'):
                    body_bytes, extra_headers = compress_response(result.body)
                    result.body = body_bytes
                    result.headers.update(extra_headers)
                return result

            # If result is a tuple (data, status_code), handle it
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
                data, status_code = result
                if isinstance(data, (dict, list)):
                    body, content_type = process_json_optimized(data)
                    return response_pool.get(body=body, status=status_code, content_type=content_type)

            # If result is a dict or list, convert to JSON
            if isinstance(result, (dict, list)):
                body, content_type = process_json_optimized(result)
                return response_pool.get(body=body, content_type=content_type)

            # If result is a string, assume it's HTML
            if isinstance(result, str):
                return response_pool.get(body=result, content_type="text/html")

            # For other types, convert to string
            return response_pool.get(body=str(result), content_type="text/plain")
        else:
            # Standard processing
            # If result is already a Response, return it
            if isinstance(result, Response):
                return result

            # If result is a tuple (data, status_code), handle it
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
                data, status_code = result
                if isinstance(data, (dict, list)):
                    return Response(
                        body=json.dumps(data, cls=self.json_encoder),
                        status=status_code,
                        content_type="application/json"
                    )

            # If result is a dict or list, convert to JSON
            if isinstance(result, (dict, list)):
                return Response(
                    body=json.dumps(result, cls=self.json_encoder),
                    content_type="application/json"
                )

            # If result is a string, assume it's HTML
            if isinstance(result, str):
                return Response(
                    body=result,
                    content_type="text/html"
                )

            # For other types, convert to string
            return Response(
                body=str(result),
                content_type="text/plain"
            )
