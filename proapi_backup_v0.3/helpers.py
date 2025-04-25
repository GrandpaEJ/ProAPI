"""
Helper functions for ProAPI.

This module provides helper functions for common tasks.
"""

import json
from typing import Any, Dict, List, Optional, Union

from .server import Response


def redirect(location: str, status_code: int = 302) -> Response:
    """
    Create a redirect response.

    Args:
        location: URL to redirect to
        status_code: HTTP status code (default: 302 Found)

    Returns:
        Response object
    """
    return Response(
        body="",
        status=status_code,
        headers={"Location": location}
    )


def jsonify(data: Any) -> Response:
    """
    Create a JSON response.

    Args:
        data: Data to convert to JSON

    Returns:
        Response object with JSON content
    """
    # Convert data to JSON
    json_data = json.dumps(data)

    # Create response
    return Response(
        body=json_data,
        content_type="application/json"
    )
