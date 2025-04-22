"""
Server module for ProAPI framework.

Provides HTTP server implementations.
"""

import json
import os
import sys
import socket
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from .logging import app_logger

class Request:
    """
    Represents an HTTP request.
    """

    def __init__(self,
                 method: str,
                 path: str,
                 headers: Dict[str, str],
                 query_params: Dict[str, List[str]],
                 body: bytes = b'',
                 remote_addr: Optional[str] = None):
        """
        Initialize a request.

        Args:
            method: HTTP method
            path: URL path
            headers: HTTP headers
            query_params: URL query parameters
            body: Request body
            remote_addr: Client IP address
        """
        self.method = method
        self.path = path
        self.headers = headers
        self.query_params = query_params
        self.body = body
        self.remote_addr = remote_addr
        self._json = None
        self._form = None
        self._cookies = None

    @property
    def content_type(self) -> str:
        """Get the Content-Type header"""
        return self.headers.get('Content-Type', '').lower()

    @property
    def json(self) -> Any:
        """Parse the request body as JSON"""
        if self._json is None:
            if 'application/json' in self.content_type:
                try:
                    self._json = json.loads(self.body.decode('utf-8'))
                except json.JSONDecodeError:
                    self._json = {}
            else:
                self._json = {}
        return self._json

    @property
    def form(self) -> Dict[str, str]:
        """Parse the request body as form data"""
        if self._form is None:
            if 'application/x-www-form-urlencoded' in self.content_type:
                body_str = self.body.decode('utf-8')
                parsed = parse_qs(body_str)
                # Convert lists to single values for easier use
                self._form = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
            else:
                self._form = {}
        return self._form

    def get_query_param(self, name: str, default: Any = None) -> Any:
        """Get a query parameter value"""
        values = self.query_params.get(name, [])
        return values[0] if values else default

    def get_header(self, name: str, default: Any = None) -> Any:
        """Get a header value"""
        return self.headers.get(name, default)

    @property
    def cookies(self) -> Dict[str, str]:
        """Parse cookies from the Cookie header"""
        if self._cookies is None:
            self._cookies = {}
            cookie_header = self.headers.get('Cookie', '')
            if cookie_header:
                for cookie in cookie_header.split(';'):
                    cookie = cookie.strip()
                    if '=' in cookie:
                        name, value = cookie.split('=', 1)
                        self._cookies[name.strip()] = value.strip()
        return self._cookies

    def get_cookie(self, name: str, default: Any = None) -> Any:
        """Get a cookie value"""
        return self.cookies.get(name, default)

class Response:
    """
    Represents an HTTP response.
    """

    def __init__(self,
                 body: Union[str, bytes, None] = None,
                 status: int = 200,
                 headers: Optional[Dict[str, str]] = None,
                 content_type: str = "text/html"):
        """
        Initialize a response.

        Args:
            body: Response body
            status: HTTP status code
            headers: HTTP headers
            content_type: Content-Type header
        """
        self.body = body if body is not None else ""
        self.status = status
        self.headers = headers or {}

        # Set Content-Type if not already set
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = content_type

    def set_cookie(self,
                   name: str,
                   value: str,
                   max_age: Optional[int] = None,
                   expires: Optional[str] = None,
                   path: str = "/",
                   domain: Optional[str] = None,
                   secure: bool = False,
                   http_only: bool = False,
                   same_site: Optional[str] = None):
        """
        Set a cookie in the response.

        Args:
            name: Cookie name
            value: Cookie value
            max_age: Maximum age in seconds
            expires: Expiration date
            path: Cookie path
            domain: Cookie domain
            secure: Whether the cookie is secure
            http_only: Whether the cookie is HTTP-only
            same_site: SameSite cookie attribute ('Strict', 'Lax', or 'None')
        """
        cookie = f"{name}={value}"

        if max_age is not None:
            cookie += f"; Max-Age={max_age}"
        if expires is not None:
            cookie += f"; Expires={expires}"
        if path:
            cookie += f"; Path={path}"
        if domain:
            cookie += f"; Domain={domain}"
        if secure:
            cookie += "; Secure"
        if http_only:
            cookie += "; HttpOnly"
        if same_site:
            cookie += f"; SameSite={same_site}"

        # Support multiple cookies
        if 'Set-Cookie' in self.headers:
            if isinstance(self.headers['Set-Cookie'], list):
                self.headers['Set-Cookie'].append(cookie)
            else:
                self.headers['Set-Cookie'] = [self.headers['Set-Cookie'], cookie]
        else:
            self.headers['Set-Cookie'] = cookie

    def delete_cookie(self,
                      name: str,
                      path: str = "/",
                      domain: Optional[str] = None):
        """
        Delete a cookie by setting its expiration in the past.

        Args:
            name: Cookie name
            path: Cookie path
            domain: Cookie domain
        """
        self.set_cookie(
            name=name,
            value="",
            max_age=0,
            path=path,
            domain=domain
        )

class ProAPIRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for ProAPI.
    """

    def __init__(self, *args, **kwargs):
        self.app = kwargs.pop('app', None)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self._handle_request('GET')

    def do_POST(self):
        self._handle_request('POST')

    def do_PUT(self):
        self._handle_request('PUT')

    def do_DELETE(self):
        self._handle_request('DELETE')

    def do_PATCH(self):
        self._handle_request('PATCH')

    def _handle_request(self, method):
        # Parse URL
        url_parts = urlparse(self.path)
        path = url_parts.path
        query_params = parse_qs(url_parts.query)

        # Get headers
        headers = {k: v for k, v in self.headers.items()}

        # Security checks for production
        if hasattr(self.app, 'env') and self.app.env == "production":
            # Check request size
            content_length = int(self.headers.get('Content-Length', 0))
            max_size = getattr(self.app, 'max_request_size', 1024 * 1024)  # Default 1MB

            if content_length > max_size:
                app_logger.warning(f"Request too large: {content_length} bytes (max: {max_size})")
                self.send_error(413, "Request Entity Too Large")
                return

            # Check trusted hosts if configured
            trusted_hosts = getattr(self.app, 'trusted_hosts', [])
            if trusted_hosts:
                host_header = self.headers.get('Host', '')
                if host_header:
                    # Extract host without port if present
                    host = host_header.split(':')[0] if ':' in host_header else host_header
                    # Check if host matches any trusted host pattern
                    is_trusted = False
                    for th in trusted_hosts:
                        # Exact match
                        if host == th:
                            is_trusted = True
                            break
                        # Wildcard match (*.example.com)
                        if th.startswith('*') and host.endswith(th[1:]):
                            is_trusted = True
                            break
                        # Host with port match (if trusted host includes port)
                        if th == host_header:
                            is_trusted = True
                            break

                    if not is_trusted:
                        app_logger.warning(f"Request from untrusted host: {host_header}")
                        self.send_error(403, "Forbidden")
                        return

        # Get request body with size limit
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''

        # Create request object
        request = Request(
            method=method,
            path=path,
            headers=headers,
            query_params=query_params,
            body=body,
            remote_addr=self.client_address[0]
        )

        # Add production properties
        if hasattr(self.app, 'env'):
            request.env = self.app.env

        # Process the request with timeout for production
        if hasattr(self.app, 'env') and self.app.env == "production" and hasattr(self.app, 'request_timeout'):
            import threading
            import queue

            # Use a queue to get the response from the thread
            response_queue = queue.Queue()

            def process_with_timeout():
                try:
                    response = self.app.handle_request(request)
                    response_queue.put(response)
                except Exception as e:
                    app_logger.error(f"Error processing request: {e}")
                    response_queue.put(None)

            # Start processing in a thread
            thread = threading.Thread(target=process_with_timeout)
            thread.daemon = True
            thread.start()

            try:
                # Wait for the response with timeout
                response = response_queue.get(timeout=self.app.request_timeout)
                if response is None:
                    # Error occurred in the thread
                    self.send_error(500, "Internal Server Error")
                    return
            except queue.Empty:
                # Timeout occurred
                app_logger.warning(f"Request timeout after {self.app.request_timeout}s: {method} {path}")
                self.send_error(504, "Gateway Timeout")
                return
        else:
            # Process normally without timeout
            response = self.app.handle_request(request)

        # Send response
        self.send_response(response.status)

        # Send headers
        for name, value in response.headers.items():
            if isinstance(value, list):
                # Handle multiple headers with the same name (e.g., Set-Cookie)
                for v in value:
                    self.send_header(name, v)
            else:
                self.send_header(name, value)
        self.end_headers()

        # Send body
        if isinstance(response.body, str):
            self.wfile.write(response.body.encode('utf-8'))
        elif isinstance(response.body, bytes):
            self.wfile.write(response.body)

    def log_message(self, format, *args):
        """Override to customize logging using Loguru"""
        # Extract status code and request info
        status_code = args[1] if len(args) > 1 else '---'
        request_line = args[0] if args else 'Unknown'

        # Format the log message
        log_msg = f"{self.client_address[0]} - {request_line} - {status_code}"

        # Log with appropriate level based on status code
        if status_code.startswith('5'):
            app_logger.error(log_msg)
        elif status_code.startswith('4'):
            app_logger.warning(log_msg)
        else:
            # Only log in debug mode or for error codes
            if self.app and self.app.debug:
                app_logger.info(log_msg)

class DefaultServer:
    """
    Default HTTP server implementation using http.server.
    """

    def __init__(self, app, host, port, **kwargs):
        """
        Initialize the server.

        Args:
            app: ProAPI application
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional options including:
                request_timeout: Request timeout in seconds
                max_request_size: Maximum request size in bytes
                trusted_hosts: List of trusted hosts for security
        """
        self.app = app
        self.host = host
        self.port = port
        self.options = kwargs
        self.server = None

        # Extract production options
        self.request_timeout = kwargs.get('request_timeout', 30)
        self.max_request_size = kwargs.get('max_request_size', 1024 * 1024)  # 1MB
        self.trusted_hosts = kwargs.get('trusted_hosts', [])

    def start(self):
        """Start the server"""
        # Create a request handler class with a reference to the app
        handler = lambda *args: ProAPIRequestHandler(*args, app=self.app)

        # Create and start the server
        self.server = HTTPServer((self.host, self.port), handler)

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            pass

    def stop(self):
        """Stop the server"""
        if self.server:
            self.server.shutdown()

class MultiWorkerServer:
    """
    Multi-worker HTTP server implementation.
    Recommended for production use.
    """

    def __init__(self, app, host, port, workers=4, **kwargs):
        """
        Initialize the server.

        Args:
            app: ProAPI application
            host: Host to bind to
            port: Port to bind to
            workers: Number of worker processes
            **kwargs: Additional options including:
                request_timeout: Request timeout in seconds
                max_request_size: Maximum request size in bytes
                trusted_hosts: List of trusted hosts for security
        """
        self.app = app
        self.host = host
        self.port = port
        self.workers = max(1, workers)
        self.options = kwargs
        self.server = None
        self.worker_threads = []

        # Extract production options
        self.request_timeout = kwargs.get('request_timeout', 30)
        self.max_request_size = kwargs.get('max_request_size', 1024 * 1024)  # 1MB
        self.trusted_hosts = kwargs.get('trusted_hosts', [])

        # Log production configuration
        if app.env == "production":
            app_logger.info(f"Production server configured with {self.workers} workers")
            app_logger.info(f"Request timeout: {self.request_timeout}s, Max request size: {self.max_request_size} bytes")
            if self.trusted_hosts:
                app_logger.info(f"Trusted hosts: {', '.join(self.trusted_hosts)}")

    def start(self):
        """Start the server with multiple workers"""
        # Create a request handler class with a reference to the app
        handler = lambda *args: ProAPIRequestHandler(*args, app=self.app)

        # Create the server
        self.server = HTTPServer((self.host, self.port), handler)

        # Create worker threads
        for i in range(self.workers):
            thread = threading.Thread(
                target=self._worker_thread,
                name=f"ProAPI-Worker-{i+1}"
            )
            thread.daemon = True
            self.worker_threads.append(thread)
            thread.start()

        # Wait for all workers to finish
        try:
            while any(t.is_alive() for t in self.worker_threads):
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def _worker_thread(self):
        """Worker thread function"""
        try:
            self.server.serve_forever()
        except Exception as e:
            app_logger.exception(f"Worker thread error: {e}")

    def stop(self):
        """Stop the server"""
        if self.server:
            self.server.shutdown()

def create_server(app, host, port, server_type=None, workers=1, use_reloader=False, **kwargs):
    """
    Create a server instance based on the specified type.

    Args:
        app: ProAPI application
        host: Host to bind to
        port: Port to bind to
        server_type: Server type ('default', 'multiworker', 'uvicorn', 'gunicorn')
        workers: Number of worker processes
        use_reloader: Whether to use auto-reloading (only works with uvicorn)
        **kwargs: Additional server options

    Returns:
        Server instance
    """
    # If server_type is None, choose based on environment
    if server_type is None:
        if hasattr(app, 'env'):
            if app.env == "production":
                server_type = "multiworker"
            else:
                server_type = "default"
        else:
            server_type = "default"

    # If reloader is requested, use uvicorn
    if use_reloader and server_type != "uvicorn":
        import uvicorn
        app_logger.info("Using uvicorn server for auto-reloading")
        server_type = "uvicorn"

    # Create the appropriate server
    if server_type == "multiworker":
        # Check if auto_restart is enabled
        if kwargs.get('auto_restart', False):
            try:
                from .worker_manager import WorkerManager

                # Create command for worker processes
                import sys
                cmd = [sys.executable, "-m", "uvicorn", "proapi.asgi_adapter:app",
                       "--host", host, "--port", str(port)]

                # Create worker manager
                app_logger.info(f"Using worker manager with auto-restart for {workers} workers")
                manager = WorkerManager(
                    cmd=cmd,
                    num_workers=workers,
                    worker_timeout=kwargs.get('request_timeout', 30),
                    worker_max_requests=kwargs.get('worker_max_requests', 1000),
                    worker_max_memory_mb=kwargs.get('worker_max_memory_mb', 512),
                    worker_restart_delay=kwargs.get('worker_restart_delay', 3)
                )

                # Create a server wrapper for the worker manager
                class WorkerManagerServer:
                    def __init__(self, manager):
                        self.manager = manager

                    def start(self):
                        self.manager.start()

                    def stop(self):
                        self.manager.stop()

                return WorkerManagerServer(manager)
            except ImportError:
                app_logger.warning("Worker manager not available. Falling back to standard multiworker server.")
                return MultiWorkerServer(app, host, port, workers=workers, **kwargs)
        else:
            return MultiWorkerServer(app, host, port, workers=workers, **kwargs)
    elif server_type == "uvicorn":
        import uvicorn

        # Create ASGI app adapter
        from .asgi import create_asgi_app

        # Make the app callable for uvicorn
        class ASGIApp:
            def __init__(self, app):
                self.app = app
                self.asgi_app = create_asgi_app(app)

            async def __call__(self, scope, receive, send):
                await self.asgi_app(scope, receive, send)

        asgi_app = ASGIApp(app)

        # Return uvicorn server
        class UvicornServer:
            def __init__(self, app, host, port, asgi_app, use_reloader=False, **kwargs):
                self.app = app
                self.host = host
                self.port = port
                self.asgi_app = asgi_app
                self.use_reloader = use_reloader
                self.options = kwargs

            def start(self):
                app_logger.info(f"Starting Uvicorn server on {self.host}:{self.port}")
                if self.use_reloader:
                    app_logger.info("Auto-reloader enabled (using uvicorn)")
                    print("Auto-reloader enabled (using uvicorn)")

                # Make a copy of options to avoid modifying the original
                options = self.options.copy()

                # For reloading, we need to use the import string approach
                if self.use_reloader:
                    # Get the main module name
                    import __main__
                    # Handle case where __main__ might not have __file__ attribute
                    main_module = getattr(__main__, '__file__', None)

                    # If main_module is None, try to get it from sys.modules['__main__']
                    if main_module is None:
                        import sys
                        if '__main__' in sys.modules:
                            main = sys.modules['__main__']
                            main_module = getattr(main, '__file__', None)

                    # If still None, try to get it from the current file
                    if main_module is None:
                        import inspect
                        current_frame = inspect.currentframe()
                        main_module = current_frame.f_back.f_globals.get('__file__')

                    if main_module:
                        # Get the relative path to make it an import string
                        import os
                        import sys

                        # Get absolute path of the main module
                        main_module_abs = os.path.abspath(main_module)
                        app_dir = os.path.dirname(main_module_abs)

                        # Add the parent directory to sys.path to ensure imports work
                        parent_dir = os.path.dirname(app_dir)
                        if parent_dir not in sys.path:
                            sys.path.insert(0, parent_dir)

                        # Get just the filename without extension for the module name
                        module_name = os.path.splitext(os.path.basename(main_module))[0]

                        # Find the app variable name
                        app_var = None
                        for var_name, var_val in __main__.__dict__.items():
                            if var_val is self.app:
                                app_var = var_name
                                break

                        if app_var:
                            # Use a direct import string that doesn't rely on Python package structure
                            import_string = f"{module_name}:{app_var}"
                            app_logger.info(f"Using import string for reloading: {import_string}")

                            # Add the current directory to sys.path to ensure imports work
                            import sys
                            if app_dir not in sys.path:
                                sys.path.insert(0, app_dir)

                            # Run with the import string
                            # Make a copy of options to avoid modifying the original
                            options = self.options.copy()
                            # Don't pass reload in options if we're setting it explicitly
                            if 'reload' in options:
                                del options['reload']

                            uvicorn.run(
                                import_string,
                                host=self.host,
                                port=self.port,
                                reload=True,
                                workers=workers,
                                **options
                            )
                            return

                # Fall back to direct app reference (no reloading)
                if self.use_reloader:
                    app_logger.warning("Could not determine import string for reloading. Falling back to direct app reference (no reloading).")
                    print("Could not determine import string for reloading. Falling back to direct app reference (no reloading).")

                # Make a copy of options to avoid modifying the original
                options = self.options.copy()
                # Don't pass reload in options if it's already there
                if 'reload' in options:
                    del options['reload']

                uvicorn.run(
                    self.asgi_app,
                    host=self.host,
                    port=self.port,
                    workers=workers,
                    **options
                )

            def stop(self):
                pass  # Uvicorn handles its own shutdown

        return UvicornServer(app, host, port, asgi_app=asgi_app, use_reloader=use_reloader, **kwargs)
    elif server_type == "gunicorn":
        # This would be implemented for production WSGI support
        # For now, fall back to multiworker
        app_logger.warning("Gunicorn support not yet implemented. Using multiworker server.")
        return MultiWorkerServer(app, host, port, workers=workers, **kwargs)
    else:
        # Default to basic server
        if server_type != "default":
            app_logger.warning(f"Unknown server type: {server_type}. Falling back to default server.")
        return DefaultServer(app, host, port, **kwargs)
