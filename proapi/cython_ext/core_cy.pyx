"""
Cython extension for ProAPI core functionality.

This module provides optimized versions of core ProAPI functions.
"""

# Define optimized functions
def fast_route_match(route_pattern, path):
    """
    Fast route matching using Cython.
    
    Args:
        route_pattern: Route pattern to match
        path: Path to match against
        
    Returns:
        Tuple of (match_result, params)
    """
    # Simple implementation for now
    params = {}
    
    # Convert patterns like '/users/{id}' to regex
    import re
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
    Fast JSON parsing using Cython.
    
    Args:
        json_str: JSON string to parse
        
    Returns:
        Parsed JSON object
    """
    import json
    return json.loads(json_str)
