"""
Request proxy for ProAPI.

This module provides a global request object that proxies to the current request.
"""

import threading
from typing import Any, Dict, List, Optional, Union

# Thread-local storage for the current request
_request_local = threading.local()


class RequestProxy:
    """
    Proxy to the current request.

    This class provides access to the current request in the current thread.
    It's used to provide a global `request` object that always refers to the
    current request being processed.
    """

    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the current request.

        Args:
            name: Attribute name

        Returns:
            Attribute value

        Raises:
            AttributeError: If the current request is not set or doesn't have the attribute
        """
        if not hasattr(_request_local, "request"):
            raise AttributeError(
                "No request is being processed. The 'request' object is only available "
                "during request processing."
            )
        
        return getattr(_request_local.request, name)
    
    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set an attribute on the current request.

        Args:
            name: Attribute name
            value: Attribute value

        Raises:
            AttributeError: If the current request is not set
        """
        if not hasattr(_request_local, "request"):
            raise AttributeError(
                "No request is being processed. The 'request' object is only available "
                "during request processing."
            )
        
        setattr(_request_local.request, name, value)


# Create a global request object
request = RequestProxy()


def set_current_request(req: Any) -> None:
    """
    Set the current request for the current thread.

    Args:
        req: Request object
    """
    _request_local.request = req


def get_current_request() -> Optional[Any]:
    """
    Get the current request for the current thread.

    Returns:
        Current request or None if not set
    """
    return getattr(_request_local, "request", None)


def clear_current_request() -> None:
    """Clear the current request for the current thread."""
    if hasattr(_request_local, "request"):
        delattr(_request_local, "request")
