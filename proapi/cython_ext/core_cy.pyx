"""
Cython-optimized core functionality for ProAPI framework.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union

# Optimized route matching
cpdef bint match_route(str method, str path, str route_method, object pattern):
    """
    Check if a route matches the given method and path.
    
    Args:
        method: HTTP method
        path: URL path
        route_method: Route HTTP method
        pattern: Compiled regex pattern
        
    Returns:
        True if the route matches, False otherwise
    """
    return method.upper() == route_method and pattern.match(path) is not None

# Optimized path parameter extraction
cpdef dict extract_params(object pattern, str path):
    """
    Extract path parameters from the given path.
    
    Args:
        pattern: Compiled regex pattern
        path: URL path
        
    Returns:
        Dictionary of parameter names and values
    """
    cdef dict params = {}
    match = pattern.match(path)
    
    if not match:
        return params
    
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

# Optimized JSON processing
cpdef str json_dumps(object data):
    """
    Serialize data to JSON.
    
    Args:
        data: Data to serialize
        
    Returns:
        JSON string
    """
    return json.dumps(data)

cpdef object json_loads(str data):
    """
    Parse JSON string.
    
    Args:
        data: JSON string
        
    Returns:
        Parsed data
    """
    return json.loads(data)

# Optimized URL parsing
cpdef tuple parse_url(str url):
    """
    Parse a URL into path and query string.
    
    Args:
        url: URL to parse
        
    Returns:
        Tuple of (path, query_string)
    """
    cdef int query_index = url.find('?')
    
    if query_index == -1:
        return url, ''
    
    return url[:query_index], url[query_index+1:]

# Optimized query string parsing
cpdef dict parse_query_string(str query_string):
    """
    Parse a query string into a dictionary.
    
    Args:
        query_string: Query string to parse
        
    Returns:
        Dictionary of parameter names and values
    """
    cdef dict params = {}
    
    if not query_string:
        return params
    
    for param in query_string.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            
            # Handle multiple values for the same key
            if key in params:
                if isinstance(params[key], list):
                    params[key].append(value)
                else:
                    params[key] = [params[key], value]
            else:
                params[key] = value
        else:
            params[param] = ''
    
    return params
