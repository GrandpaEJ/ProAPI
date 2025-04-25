"""
ASGI adapter for ProAPI.

This module provides a simple ASGI adapter for ProAPI applications.
"""

import json
import traceback
from typing import Dict, Any, Callable, Awaitable

from .logging import app_logger
from .server import Request, Response

class ASGIAdapter:
    """
    ASGI adapter for ProAPI applications.

    This class provides a simple ASGI adapter that can be used with uvicorn.
    """

    def __init__(self, app):
        """
        Initialize the ASGI adapter.

        Args:
            app: ProAPI application
        """
        self.app = app

    async def __call__(self, scope, receive, send):
        """
        ASGI application.

        Args:
            scope: ASGI scope
            receive: ASGI receive function
            send: ASGI send function
        """
        if scope["type"] == "websocket":
            # Handle WebSocket connections
            path = scope["path"]

            # Find matching WebSocket route
            websocket_route = None
            if hasattr(self.app, 'websocket_routes'):
                for route in self.app.websocket_routes:
                    if route.match(path):
                        websocket_route = route
                        break

            if websocket_route:
                # Handle the WebSocket connection
                await websocket_route(scope, receive, send)
                return
            else:
                # No matching route, close the connection
                await send({"type": "websocket.close", "code": 1000})
                return

        elif scope["type"] != "http":
            # We don't handle other types
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"application/json")]
            })
            await send({
                "type": "http.response.body",
                "body": json.dumps({"error": "Only HTTP and WebSocket requests are supported"}).encode("utf-8")
            })
            return

        try:
            # Extract method and path
            method = scope["method"]
            path = scope["path"]

            # Extract headers - optimized for speed
            headers = {}
            for k, v in scope["headers"]:
                key = k.decode("utf-8")
                headers[key] = v.decode("utf-8")

            # Extract query parameters - optimized for speed
            query_params = {}
            query_string = scope.get("query_string", b"")
            if query_string:
                query_str = query_string.decode("utf-8")
                for param in query_str.split("&"):
                    if not param:
                        continue
                    if "=" in param:
                        k, v = param.split("=", 1)
                        if k in query_params:
                            if isinstance(query_params[k], list):
                                query_params[k].append(v)
                            else:
                                query_params[k] = [query_params[k], v]
                        else:
                            query_params[k] = v

            # Extract client address
            client_address = scope.get("client", ("127.0.0.1", 0))

            # Read request body - optimized for common case of no body
            message = await receive()
            body = message.get("body", b"")

            # Only read more if there's more to read
            if message.get("more_body", False):
                chunks = [body]
                more_body = True
                while more_body:
                    message = await receive()
                    chunks.append(message.get("body", b""))
                    more_body = message.get("more_body", False)
                body = b"".join(chunks)

            # Create ProAPI request
            request = Request(
                method=method,
                path=path,
                headers=headers,
                query_params=query_params,
                body=body,
                remote_addr=client_address[0]
            )

            # Process the request
            response = self.app.handle_request(request)

            # Convert headers - optimized for speed
            headers = []
            for k, v in response.headers.items():
                headers.append((k.encode("utf-8"), str(v).encode("utf-8")))

            # Send response start
            await send({
                "type": "http.response.start",
                "status": response.status,
                "headers": headers
            })

            # Send response body - optimized for common case of string
            if isinstance(response.body, str):
                body = response.body.encode("utf-8")
            elif isinstance(response.body, bytes):
                body = response.body
            else:
                body = b""

            await send({
                "type": "http.response.body",
                "body": body
            })
        except Exception as e:
            # Get traceback for better debugging
            error_traceback = traceback.format_exc()
            app_logger.exception(f"Error in ASGI adapter: {e}")

            # Send error response
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"application/json")]
            })

            error_body = {"error": "Internal Server Error"}
            if hasattr(self.app, 'debug') and self.app.debug:
                error_body["detail"] = str(e)
                error_body["traceback"] = error_traceback

            await send({
                "type": "http.response.body",
                "body": json.dumps(error_body).encode("utf-8")
            })

def create_asgi_app(app):
    """
    Create an ASGI application from a ProAPI application.

    Args:
        app: ProAPI application

    Returns:
        ASGI application
    """
    return ASGIAdapter(app)
