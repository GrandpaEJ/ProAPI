"""
Session proxy for ProAPI.

This module provides a global session object that proxies to the current session.
"""

import threading
from typing import Any, Dict, List, Optional, Union

from .request_proxy import get_current_request

# Thread-local storage for the current session
_session_local = threading.local()


class SessionProxy:
    """
    Proxy to the current session.

    This class provides access to the current session in the current thread.
    It's used to provide a global `session` object that always refers to the
    session of the current request being processed.
    """

    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the current session.

        Args:
            name: Attribute name

        Returns:
            Attribute value

        Raises:
            AttributeError: If the current session is not set or doesn't have the attribute
        """
        # Try to get the session from the current request
        request = get_current_request()
        if request and hasattr(request, "session"):
            return getattr(request.session, name)
        
        # If no request is available, try to get from thread-local storage
        if hasattr(_session_local, "session"):
            return getattr(_session_local.session, name)
        
        # No session available
        raise AttributeError(
            "No session is available. The 'session' object is only available "
            "during request processing when sessions are enabled."
        )
    
    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set an attribute on the current session.

        Args:
            name: Attribute name
            value: Attribute value

        Raises:
            AttributeError: If the current session is not set
        """
        # Try to get the session from the current request
        request = get_current_request()
        if request and hasattr(request, "session"):
            setattr(request.session, name, value)
            return
        
        # If no request is available, try to use thread-local storage
        if hasattr(_session_local, "session"):
            setattr(_session_local.session, name, value)
            return
        
        # No session available
        raise AttributeError(
            "No session is available. The 'session' object is only available "
            "during request processing when sessions are enabled."
        )
    
    def __getitem__(self, key: str) -> Any:
        """
        Get an item from the current session.

        Args:
            key: Item key

        Returns:
            Item value

        Raises:
            AttributeError: If the current session is not set
        """
        # Try to get the session from the current request
        request = get_current_request()
        if request and hasattr(request, "session"):
            return request.session[key]
        
        # If no request is available, try to get from thread-local storage
        if hasattr(_session_local, "session"):
            return _session_local.session[key]
        
        # No session available
        raise AttributeError(
            "No session is available. The 'session' object is only available "
            "during request processing when sessions are enabled."
        )
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set an item on the current session.

        Args:
            key: Item key
            value: Item value

        Raises:
            AttributeError: If the current session is not set
        """
        # Try to get the session from the current request
        request = get_current_request()
        if request and hasattr(request, "session"):
            request.session[key] = value
            return
        
        # If no request is available, try to use thread-local storage
        if hasattr(_session_local, "session"):
            _session_local.session[key] = value
            return
        
        # No session available
        raise AttributeError(
            "No session is available. The 'session' object is only available "
            "during request processing when sessions are enabled."
        )
    
    def __contains__(self, key: str) -> bool:
        """
        Check if an item is in the current session.

        Args:
            key: Item key

        Returns:
            True if the item is in the session, False otherwise

        Raises:
            AttributeError: If the current session is not set
        """
        # Try to get the session from the current request
        request = get_current_request()
        if request and hasattr(request, "session"):
            return key in request.session
        
        # If no request is available, try to get from thread-local storage
        if hasattr(_session_local, "session"):
            return key in _session_local.session
        
        # No session available
        raise AttributeError(
            "No session is available. The 'session' object is only available "
            "during request processing when sessions are enabled."
        )


# Create a global session object
session = SessionProxy()


def set_current_session(sess: Any) -> None:
    """
    Set the current session for the current thread.

    Args:
        sess: Session object
    """
    _session_local.session = sess


def get_current_session() -> Optional[Any]:
    """
    Get the current session for the current thread.

    Returns:
        Current session or None if not set
    """
    # Try to get the session from the current request
    request = get_current_request()
    if request and hasattr(request, "session"):
        return request.session
    
    # If no request is available, try to get from thread-local storage
    return getattr(_session_local, "session", None)


def clear_current_session() -> None:
    """Clear the current session for the current thread."""
    if hasattr(_session_local, "session"):
        delattr(_session_local, "session")
