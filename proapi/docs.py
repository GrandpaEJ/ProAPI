"""
Documentation module for ProAPI framework.

Provides automatic API documentation generation using OpenAPI and Swagger UI.
"""

import inspect
import json
import re
from typing import Any, Dict

from .swagger_ui import SWAGGER_UI_TEMPLATE, SWAGGER_UI_VERSION

def generate_swagger_ui_html(title: str = "ProAPI Docs", spec_url: str = "/docs/json") -> str:
    """
    Generate Swagger UI HTML for API documentation.

    Args:
        title: Documentation title
        spec_url: URL to the OpenAPI specification JSON

    Returns:
        Swagger UI HTML
    """
    return SWAGGER_UI_TEMPLATE.format(
        title=title,
        version=SWAGGER_UI_VERSION,
        spec_url=spec_url
    )

def generate_openapi_spec(app, title: str = "ProAPI Docs") -> Dict[str, Any]:
    """
    Generate OpenAPI specification for a ProAPI application.

    Args:
        app: ProAPI application
        title: Documentation title

    Returns:
        OpenAPI specification as a dictionary
    """
    routes = app.routes

    # Group routes by path
    grouped_routes = {}
    for route in routes:
        # Convert path parameters to OpenAPI format
        openapi_path = route.path
        if '{' in openapi_path:
            # Extract path parameters
            path_params = [p[1:-1] for p in re.findall(r'{[^{}]+}', route.path)]

            # Handle typed parameters like {id:int} -> {id}
            for param in path_params:
                if ':' in param:
                    name, _ = param.split(':', 1)
                    openapi_path = openapi_path.replace(f'{{{param}}}', f'{{{name}}}')

        if openapi_path not in grouped_routes:
            grouped_routes[openapi_path] = []
        grouped_routes[openapi_path].append(route)

    # Generate paths object
    paths = {}
    for path, routes in grouped_routes.items():
        path_data = {}

        for route in routes:
            method = route.method.lower()

            # Get handler docstring
            docstring = inspect.getdoc(route.handler) or "No description"
            summary = docstring.split("\n")[0] if docstring else ""

            # Get handler parameters
            parameters = []
            sig = inspect.signature(route.handler)

            # Path parameters
            for param_name, param in sig.parameters.items():
                if param_name != "request":  # Skip request parameter
                    param_type = "string"
                    param_format = None

                    # Handle typed parameters
                    if ":" in param_name:
                        param_name, param_type = param_name.split(":", 1)

                        # Map Python types to OpenAPI types
                        if param_type == "int":
                            param_type = "integer"
                            param_format = "int32"
                        elif param_type == "float":
                            param_type = "number"
                            param_format = "float"
                        elif param_type == "bool":
                            param_type = "boolean"

                    # Check if parameter is required (not used for path parameters in OpenAPI)

                    # Create parameter object
                    parameter = {
                        "name": param_name,
                        "in": "path",
                        "required": True,  # Path parameters are always required in OpenAPI
                        "schema": {
                            "type": param_type
                        },
                        "description": f"{param_name} parameter"
                    }

                    if param_format:
                        parameter["schema"]["format"] = param_format

                    parameters.append(parameter)

            # Request body for POST, PUT, PATCH methods
            request_body = None
            if method in ["post", "put", "patch"]:
                request_body = {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object"
                            }
                        }
                    },
                    "required": True
                }

            # Create operation object
            operation = {
                "summary": summary,
                "description": docstring,
                "operationId": f"{method}_{route.handler.__name__}",
                "parameters": parameters,
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request"
                    },
                    "404": {
                        "description": "Not Found"
                    },
                    "500": {
                        "description": "Internal Server Error"
                    }
                }
            }

            # Add request body if needed
            if request_body:
                operation["requestBody"] = request_body

            path_data[method] = operation

        paths[path] = path_data

    # Create servers list
    servers = [
        {
            "url": "/",
            "description": "Current server"
        }
    ]

    # Add server URL if available in the request
    if hasattr(app, '_current_request') and app._current_request:
        host = app._current_request.headers.get('Host')
        if host:
            protocol = 'https' if app._current_request.headers.get('X-Forwarded-Proto') == 'https' else 'http'
            servers.insert(0, {
                "url": f"{protocol}://{host}",
                "description": "Current server"
            })

    # Create OpenAPI specification
    return {
        "openapi": "3.0.0",
        "info": {
            "title": title,
            "version": "1.0.0",
            "description": "API documentation generated by ProAPI"
        },
        "servers": servers,
        "paths": paths,
        "components": {
            "schemas": {},
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
        }
    }

class DocsMiddleware:
    """
    Middleware for serving API documentation using Swagger UI.
    """

    def __init__(self, app, url_path: str = "/docs", title: str = "API Documentation"):
        """
        Initialize the docs middleware.

        Args:
            app: ProAPI application
            url_path: URL path for the documentation
            title: Documentation title
        """
        self.app = app
        self.url_path = url_path
        self.title = title

    def __call__(self, request):
        """
        Process the request.

        Args:
            request: Request object

        Returns:
            Request or Response object
        """
        from .server import Response

        # Check if the request is for the documentation
        if request.path == self.url_path:
            # Generate Swagger UI HTML
            spec_url = f"{self.url_path}/json"
            html = generate_swagger_ui_html(self.title, spec_url)

            # Return the response with CORS headers
            return Response(
                body=html,
                content_type="text/html",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )

        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS" and (request.path == self.url_path or request.path == f"{self.url_path}/json"):
            return Response(
                body="",
                status=204,  # No Content
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Max-Age": "86400"  # 24 hours
                }
            )

        # Check if the request is for the OpenAPI specification
        if request.path == f"{self.url_path}/json":
            # Generate OpenAPI specification
            spec = generate_openapi_spec(self.app, self.title)

            # Return the response with CORS headers
            return Response(
                body=json.dumps(spec, indent=2),
                content_type="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )

        # Not a documentation request, continue with request processing
        return request
