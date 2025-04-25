"""
ASGI adapter for ProAPI framework.

Provides ASGI compatibility for ProAPI applications.
"""

import json
import inspect
from typing import Dict, Any, Callable, Awaitable

from .logging import app_logger
from .server import Request, Response

# This is a placeholder for the old async function that's been replaced
# by the non-async version below

async def asgi_to_proapi_request(scope, receive):
    """
    Convert ASGI request to ProAPI request.

    Args:
        scope: ASGI scope
        receive: ASGI receive function

    Returns:
        ProAPI Request
    """
    # Extract method and path
    method = scope["method"]
    path = scope["path"]

    # Extract headers
    headers = {k.decode("utf-8"): v.decode("utf-8") for k, v in scope["headers"]}

    # Extract query parameters
    query_params = {}
    for k, v in scope.get("query_string", b"").decode("utf-8").split("&"):
        if k:
            if k in query_params:
                if isinstance(query_params[k], list):
                    query_params[k].append(v)
                else:
                    query_params[k] = [query_params[k], v]
            else:
                query_params[k] = v

    # Extract client address
    client_address = scope.get("client", ("127.0.0.1", 0))

    # Read request body
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    # Create ProAPI request
    request = Request(
        method=method,
        path=path,
        headers=headers,
        query_params=query_params,
        body=body,
        remote_addr=client_address[0]
    )

    return request

async def proapi_to_asgi_response(response, send):
    """
    Convert ProAPI response to ASGI response.

    Args:
        response: ProAPI Response
        send: ASGI send function
    """
    # Convert headers
    headers = []
    for k, v in response.headers.items():
        headers.append((k.encode("utf-8"), str(v).encode("utf-8")))

    # Send response start
    await send({
        "type": "http.response.start",
        "status": response.status,
        "headers": headers
    })

    # Send response body
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

def create_asgi_app(app):
    """
    Create an ASGI application from a ProAPI application.

    This is a non-async version that returns an async function.

    Args:
        app: ProAPI application

    Returns:
        ASGI application
    """
    async def asgi_app(scope, receive, send):
        """
        ASGI application.

        Args:
            scope: ASGI scope
            receive: ASGI receive function
            send: ASGI send function
        """
        if scope["type"] != "http":
            # We only handle HTTP requests for now
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"application/json")]
            })
            await send({
                "type": "http.response.body",
                "body": json.dumps({"error": "Only HTTP requests are supported"}).encode("utf-8")
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
            response = app.handle_request(request)

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
            import traceback
            error_traceback = traceback.format_exc()
            app_logger.exception(f"Error in ASGI adapter: {e}")

            # Send error response
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"application/json")]
            })

            error_body = {"error": "Internal Server Error"}
            if hasattr(app, 'debug') and app.debug:
                error_body["detail"] = str(e)
                error_body["traceback"] = error_traceback

            await send({
                "type": "http.response.body",
                "body": json.dumps(error_body).encode("utf-8")
            })

    return asgi_app
