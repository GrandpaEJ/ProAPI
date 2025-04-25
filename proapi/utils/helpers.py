"""
Helper functions for ProAPI.
"""

import json
from typing import Any, Dict, List, Optional, Union

def redirect(url: str, status_code: int = 302):
    """
    Create a redirect response.
    
    Args:
        url: URL to redirect to
        status_code: HTTP status code (default: 302)
    
    Returns:
        Response object
    """
    from proapi.server.server import Response
    
    return Response(
        status=status_code,
        headers={"Location": url},
        body=""
    )

def jsonify(data: Any, status_code: int = 200):
    """
    Create a JSON response.
    
    Args:
        data: Data to convert to JSON
        status_code: HTTP status code (default: 200)
    
    Returns:
        Response object
    """
    from proapi.server.server import Response
    
    return Response(
        status=status_code,
        body=json.dumps(data),
        content_type="application/json"
    )
