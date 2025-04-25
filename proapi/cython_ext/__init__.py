"""
Cython extensions for ProAPI.

This package contains Cython-optimized versions of core ProAPI functions.
"""

# Try to import Cython extensions, fall back to pure Python if not available
try:
    from .core_cy import fast_route_match, fast_json_parse
except ImportError:
    # Define fallback functions
    def fast_route_match(route_pattern, path):
        """
        Fallback route matching function.
        
        Args:
            route_pattern: Route pattern to match
            path: Path to match against
            
        Returns:
            Tuple of (match_result, params)
        """
        params = {}
        
        # Convert patterns like '/users/{id}' to regex
        pattern_parts = route_pattern.split('/')
        path_parts = path.split('/')
        
        if len(pattern_parts) != len(path_parts):
            return False, {}
        
        for i, part in enumerate(pattern_parts):
            if part.startswith('{') and part.endswith('}'):
                # Extract parameter name
                param_name = part[1:-1]
                params[param_name] = path_parts[i]
            elif part != path_parts[i]:
                return False, {}
        
        return True, params

    def fast_json_parse(json_str):
        """
        Fallback JSON parsing function.
        
        Args:
            json_str: JSON string to parse
            
        Returns:
            Parsed JSON object
        """
        import json
        return json.loads(json_str)

# Define what's available when using "from proapi.cython_ext import *"
__all__ = [
    "fast_route_match",
    "fast_json_parse"
]
