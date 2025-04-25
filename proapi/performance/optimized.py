"""
Optimized components for ProAPI.

This module contains optimized implementations of core ProAPI components.
"""

import json
import re
import time
from typing import Any, Dict, List, Optional, Pattern, Tuple, Union, Callable
import functools
import zlib

from .logging import app_logger
from .server import Request, Response

# Route cache for faster lookups
_route_cache = {}
_route_cache_max_size = 1000
_route_cache_hits = 0
_route_cache_misses = 0

# JSON serialization optimization
_json_dumps = json.dumps
_json_loads = json.loads

# Response compression
def compress_response(body: Union[str, bytes], min_size: int = 1024) -> Tuple[bytes, Dict[str, str]]:
    """
    Compress response body if it's large enough.
    
    Args:
        body: Response body
        min_size: Minimum size for compression
        
    Returns:
        Tuple of (compressed body, additional headers)
    """
    if isinstance(body, str):
        body_bytes = body.encode('utf-8')
    else:
        body_bytes = body
        
    if len(body_bytes) < min_size:
        return body_bytes, {}
        
    compressed = zlib.compress(body_bytes)
    
    # Only use compression if it actually reduces size
    if len(compressed) < len(body_bytes):
        return compressed, {
            'Content-Encoding': 'gzip',
            'Vary': 'Accept-Encoding'
        }
    
    return body_bytes, {}

# Optimized route matching
def find_route_optimized(routes: List, method: str, path: str) -> Tuple[Any, Dict[str, str]]:
    """
    Find a matching route for the given method and path.
    
    Uses caching for better performance.
    
    Args:
        routes: List of routes
        method: HTTP method
        path: URL path
        
    Returns:
        Tuple of (route, path_params)
    """
    global _route_cache_hits, _route_cache_misses
    
    # Check cache first
    cache_key = f"{method}:{path}"
    if cache_key in _route_cache:
        _route_cache_hits += 1
        return _route_cache[cache_key]
    
    _route_cache_misses += 1
    
    # Find matching route
    for route in routes:
        if route.match(method, path):
            path_params = route.extract_params(path)
            result = (route, path_params)
            
            # Update cache
            if len(_route_cache) >= _route_cache_max_size:
                # Simple LRU: just clear the cache when it gets too big
                _route_cache.clear()
            _route_cache[cache_key] = result
            
            return result
    
    # No match found
    return None, {}

# Optimized JSON processing
def process_json_optimized(result: Any) -> Tuple[str, str]:
    """
    Process a result into JSON with optimized serialization.
    
    Args:
        result: Result from handler
        
    Returns:
        Tuple of (body, content_type)
    """
    try:
        # Use faster JSON serialization
        return _json_dumps(result), "application/json"
    except (TypeError, ValueError):
        # Fall back to standard serialization
        return json.dumps(result), "application/json"

# Request object pool
class RequestPool:
    """
    Pool of Request objects to reduce object creation.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize the request pool.
        
        Args:
            max_size: Maximum pool size
        """
        self.pool = []
        self.max_size = max_size
        
    def get(self, method: str, path: str, headers: Dict[str, str], 
            query_params: Dict[str, str], body: bytes, remote_addr: str) -> Request:
        """
        Get a Request object from the pool.
        
        Args:
            method: HTTP method
            path: URL path
            headers: HTTP headers
            query_params: Query parameters
            body: Request body
            remote_addr: Remote address
            
        Returns:
            Request object
        """
        if not self.pool:
            # Create new object if pool is empty
            return Request(method, path, headers, query_params, body, remote_addr)
        
        # Get object from pool
        request = self.pool.pop()
        
        # Reset object
        request.method = method
        request.path = path
        request.headers = headers
        request.query_params = query_params
        request.body = body
        request.remote_addr = remote_addr
        request._json = None
        request._form = None
        
        return request
        
    def release(self, request: Request):
        """
        Release a Request object back to the pool.
        
        Args:
            request: Request object
        """
        if len(self.pool) < self.max_size:
            self.pool.append(request)

# Create a global request pool
request_pool = RequestPool()

# Response object pool
class ResponsePool:
    """
    Pool of Response objects to reduce object creation.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize the response pool.
        
        Args:
            max_size: Maximum pool size
        """
        self.pool = []
        self.max_size = max_size
        
    def get(self, body: Any = None, status: int = 200, 
            headers: Dict[str, str] = None, content_type: str = None) -> Response:
        """
        Get a Response object from the pool.
        
        Args:
            body: Response body
            status: HTTP status code
            headers: HTTP headers
            content_type: Content type
            
        Returns:
            Response object
        """
        if not self.pool:
            # Create new object if pool is empty
            return Response(body, status, headers, content_type)
        
        # Get object from pool
        response = self.pool.pop()
        
        # Reset object
        response.body = body
        response.status = status
        response.headers = headers or {}
        if content_type:
            response.headers["Content-Type"] = content_type
        
        return response
        
    def release(self, response: Response):
        """
        Release a Response object back to the pool.
        
        Args:
            response: Response object
        """
        if len(self.pool) < self.max_size:
            self.pool.append(response)

# Create a global response pool
response_pool = ResponsePool()

# Function to get cache statistics
def get_cache_stats() -> Dict[str, int]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary of cache statistics
    """
    return {
        "route_cache_size": len(_route_cache),
        "route_cache_hits": _route_cache_hits,
        "route_cache_misses": _route_cache_misses,
        "route_cache_hit_ratio": _route_cache_hits / (_route_cache_hits + _route_cache_misses) if (_route_cache_hits + _route_cache_misses) > 0 else 0,
        "request_pool_size": len(request_pool.pool),
        "response_pool_size": len(response_pool.pool)
    }

# Reset cache statistics
def reset_cache_stats():
    """Reset cache statistics."""
    global _route_cache_hits, _route_cache_misses
    _route_cache_hits = 0
    _route_cache_misses = 0
    _route_cache.clear()
    request_pool.pool.clear()
    response_pool.pool.clear()
