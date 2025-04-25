"""
Routing module for ProAPI framework.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Union

class Route:
    """
    Represents a route in the application.

    A route maps a URL pattern to a handler function.
    """

    def __init__(self,
                 method: str,
                 path: str,
                 handler: Callable,
                 is_async: bool = False,
                 name: Optional[str] = None,
                 **kwargs):
        """
        Initialize a route.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: URL path pattern
            handler: Function to handle the route
            is_async: Whether the handler is an async function
            name: Optional name for the route
            **kwargs: Additional route options
        """
        self.method = method.upper()
        self.path = path
        self.handler = handler
        self.is_async = is_async
        self.name = name or handler.__name__
        self.options = kwargs

        # Convert path pattern to regex
        self.pattern = self._path_to_regex(path)

    def _path_to_regex(self, path: str) -> Pattern:
        """
        Convert a path pattern to a regex pattern.

        Supports:
        - Static segments: /users
        - Path parameters: /users/{id}
        - Optional parameters: /users/{id?}
        - Wildcard: /static/{*path}

        Args:
            path: Path pattern

        Returns:
            Compiled regex pattern
        """
        # Replace {param} with named capture groups
        regex = re.sub(r'{([^{}]+)}', self._param_to_regex_group, path)

        # Ensure the path matches exactly
        regex = f'^{regex}$'

        return re.compile(regex)

    def _param_to_regex_group(self, match):
        """Convert a parameter match to a regex group"""
        param = match.group(1)

        # Handle optional parameters
        if param.endswith('?'):
            param_name = param[:-1]
            return f'(?P<{param_name}>[^/]*)?'

        # Handle wildcard parameters
        if param.startswith('*'):
            param_name = param[1:]
            return f'(?P<{param_name}>.*)'

        # Handle typed parameters
        if ':' in param:
            param_name, param_type = param.split(':', 1)
            if param_type == 'int':
                return f'(?P<{param_name}>[0-9]+)'
            elif param_type == 'float':
                return fr'(?P<{param_name}>[0-9]+\.[0-9]+)'
            elif param_type == 'uuid':
                return f'(?P<{param_name}>[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}})'
            # Add more types as needed

        # Default: match any non-slash characters
        return f'(?P<{param}>[a-zA-Z0-9_-]+)'

    def match(self, method: str, path: str) -> bool:
        """
        Check if this route matches the given method and path.

        Args:
            method: HTTP method
            path: URL path

        Returns:
            True if the route matches, False otherwise
        """
        return method.upper() == self.method and self.pattern.match(path) is not None

    def extract_params(self, path: str) -> Dict[str, str]:
        """
        Extract path parameters from the given path.

        Args:
            path: URL path

        Returns:
            Dictionary of parameter names and values
        """
        match = self.pattern.match(path)
        if not match:
            return {}

        params = match.groupdict()

        # Convert parameters to appropriate types
        for param, value in list(params.items()):
            if param.endswith(':int'):
                clean_param = param.rsplit(':', 1)[0]
                params[clean_param] = int(value)
                del params[param]
            elif param.endswith(':float'):
                clean_param = param.rsplit(':', 1)[0]
                params[clean_param] = float(value)
                del params[param]

        return params
