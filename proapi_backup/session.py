"""
Session management for ProAPI.

This module provides session management functionality for ProAPI applications.
Sessions allow you to store user-specific data across requests.
"""

import json
import os
import time
import uuid
import hashlib
import hmac
from typing import Any, Dict, Optional, Union, List

from .logging import app_logger
from .server import Request, Response


class Session:
    """
    Represents a user session.

    A session stores user-specific data that persists across requests.
    """

    def __init__(self, session_id: str, data: Dict[str, Any] = None, new: bool = False):
        """
        Initialize a session.

        Args:
            session_id: Unique session identifier
            data: Initial session data
            new: Whether this is a new session
        """
        self.session_id = session_id
        self.data = data or {}
        self.new = new
        self.modified = False
        self.created_at = time.time()
        self.last_accessed = time.time()

    def __getitem__(self, key: str) -> Any:
        """Get a value from the session."""
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value in the session."""
        self.data[key] = value
        self.modified = True

    def __delitem__(self, key: str) -> None:
        """Delete a value from the session."""
        if key in self.data:
            del self.data[key]
            self.modified = True

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the session."""
        return key in self.data

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the session with a default."""
        return self.data.get(key, default)

    def pop(self, key: str, default: Any = None) -> Any:
        """Remove a key and return its value."""
        value = self.data.pop(key, default)
        self.modified = True
        return value

    def clear(self) -> None:
        """Clear all session data."""
        self.data.clear()
        self.modified = True

    def update(self, data: Dict[str, Any]) -> None:
        """Update session data with a dictionary."""
        self.data.update(data)
        self.modified = True

    def touch(self) -> None:
        """Update the last accessed time."""
        self.last_accessed = time.time()


class SessionBackend:
    """
    Base class for session storage backends.
    """

    def __init__(self, **kwargs):
        """Initialize the session backend."""
        pass

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data by ID.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        raise NotImplementedError("Session backend must implement get()")

    def save(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Save session data.

        Args:
            session_id: Session ID
            data: Session data
        """
        raise NotImplementedError("Session backend must implement save()")

    def delete(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session ID
        """
        raise NotImplementedError("Session backend must implement delete()")


class MemorySessionBackend(SessionBackend):
    """
    In-memory session storage backend.

    This backend stores sessions in memory. Sessions are lost when the server restarts.
    """

    def __init__(self, **kwargs):
        """Initialize the memory session backend."""
        super().__init__(**kwargs)
        self.sessions = {}
        self.expiry_times = {}
        self.max_age = kwargs.get("max_age", 3600)  # 1 hour default

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data by ID.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        # Check if session exists and is not expired
        if session_id in self.sessions:
            expiry_time = self.expiry_times.get(session_id, 0)
            if expiry_time == 0 or expiry_time > time.time():
                return self.sessions[session_id]
            else:
                # Session expired, remove it
                self.delete(session_id)
        return None

    def save(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Save session data.

        Args:
            session_id: Session ID
            data: Session data
        """
        self.sessions[session_id] = data
        if self.max_age > 0:
            self.expiry_times[session_id] = time.time() + self.max_age

    def delete(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session ID
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.expiry_times:
            del self.expiry_times[session_id]


class FileSessionBackend(SessionBackend):
    """
    File-based session storage backend.

    This backend stores sessions in files. Sessions persist across server restarts.
    """

    def __init__(self, **kwargs):
        """Initialize the file session backend."""
        super().__init__(**kwargs)
        self.directory = kwargs.get("directory", "sessions")
        self.max_age = kwargs.get("max_age", 3600)  # 1 hour default

        # Create session directory if it doesn't exist
        os.makedirs(self.directory, exist_ok=True)

    def _get_session_path(self, session_id: str) -> str:
        """Get the file path for a session."""
        # Ensure the session ID is safe for use in a filename
        safe_id = "".join(c for c in session_id if c.isalnum() or c in "-_")
        return os.path.join(self.directory, f"{safe_id}.json")

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data by ID.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        path = self._get_session_path(session_id)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)

                # Check if session is expired
                created_at = data.get("_created_at", 0)
                if self.max_age > 0 and created_at > 0:
                    if time.time() - created_at > self.max_age:
                        # Session expired, remove it
                        self.delete(session_id)
                        return None

                # Remove metadata from returned data
                if "_created_at" in data:
                    del data["_created_at"]

                return data
            except (json.JSONDecodeError, IOError) as e:
                app_logger.warning(f"Error reading session file: {e}")
        return None

    def save(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Save session data.

        Args:
            session_id: Session ID
            data: Session data
        """
        path = self._get_session_path(session_id)
        try:
            # Add metadata
            save_data = data.copy()
            if "_created_at" not in save_data:
                save_data["_created_at"] = time.time()

            with open(path, "w") as f:
                json.dump(save_data, f)
        except IOError as e:
            app_logger.error(f"Error saving session file: {e}")

    def delete(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session ID
        """
        path = self._get_session_path(session_id)
        if os.path.exists(path):
            try:
                os.remove(path)
            except IOError as e:
                app_logger.error(f"Error deleting session file: {e}")


class SessionManager:
    """
    Manages sessions for a ProAPI application.
    """

    def __init__(self,
                 secret_key: str,
                 cookie_name: str = "session",
                 max_age: int = 3600,  # 1 hour
                 path: str = "/",
                 domain: Optional[str] = None,
                 secure: bool = False,
                 http_only: bool = True,
                 same_site: Optional[str] = "Lax",
                 backend: str = "memory",
                 backend_options: Optional[Dict[str, Any]] = None):
        """
        Initialize the session manager.

        Args:
            secret_key: Secret key for signing session IDs
            cookie_name: Name of the session cookie
            max_age: Maximum age of the session in seconds
            path: Cookie path
            domain: Cookie domain
            secure: Whether the cookie is secure
            http_only: Whether the cookie is HTTP-only
            same_site: SameSite cookie attribute
            backend: Session storage backend ('memory' or 'file')
            backend_options: Additional options for the backend
        """
        self.secret_key = secret_key
        self.cookie_name = cookie_name
        self.max_age = max_age
        self.path = path
        self.domain = domain
        self.secure = secure
        self.http_only = http_only
        self.same_site = same_site

        # Initialize backend
        backend_options = backend_options or {}
        backend_options["max_age"] = max_age

        if backend == "memory":
            self.backend = MemorySessionBackend(**backend_options)
        elif backend == "file":
            self.backend = FileSessionBackend(**backend_options)
        else:
            raise ValueError(f"Unknown session backend: {backend}")

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        # Generate a random UUID
        random_id = str(uuid.uuid4())

        # Sign the ID with the secret key for security
        signature = hmac.new(
            self.secret_key.encode(),
            random_id.encode(),
            hashlib.sha256
        ).hexdigest()

        # Combine the ID and signature
        return f"{random_id}.{signature}"

    def _validate_session_id(self, session_id: str) -> bool:
        """Validate a session ID."""
        try:
            # Split the ID and signature
            parts = session_id.split(".", 1)
            if len(parts) != 2:
                return False

            random_id, signature = parts

            # Verify the signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                random_id.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False

    def get_session(self, request: Request) -> Session:
        """
        Get the session for a request.

        Args:
            request: HTTP request

        Returns:
            Session object
        """
        # Get the session ID from the cookie
        cookies = self._parse_cookies(request.headers.get("Cookie", ""))
        session_id = cookies.get(self.cookie_name)

        # Validate the session ID
        valid_id = session_id and self._validate_session_id(session_id)

        if valid_id:
            # Get session data from the backend
            data = self.backend.get(session_id)
            if data:
                return Session(session_id, data)

        # Create a new session if no valid session was found
        new_session_id = self._generate_session_id()
        return Session(new_session_id, new=True)

    def save_session(self, session: Session, response: Response) -> None:
        """
        Save a session and set the session cookie.

        Args:
            session: Session to save
            response: HTTP response
        """
        # Only save if the session is new or modified
        if session.new or session.modified:
            self.backend.save(session.session_id, session.data)

        # Set the session cookie
        cookie_value = session.session_id

        # Build the cookie string
        cookie = f"{self.cookie_name}={cookie_value}"
        cookie += f"; Path={self.path}"

        if self.max_age:
            cookie += f"; Max-Age={self.max_age}"

        if self.domain:
            cookie += f"; Domain={self.domain}"

        if self.secure:
            cookie += "; Secure"

        if self.http_only:
            cookie += "; HttpOnly"

        if self.same_site:
            cookie += f"; SameSite={self.same_site}"

        # Add the cookie to the response
        if "Set-Cookie" in response.headers:
            response.headers["Set-Cookie"] = [response.headers["Set-Cookie"], cookie]
        else:
            response.headers["Set-Cookie"] = cookie

    def delete_session(self, session: Session, response: Response) -> None:
        """
        Delete a session and clear the session cookie.

        Args:
            session: Session to delete
            response: HTTP response
        """
        # Delete the session from the backend
        self.backend.delete(session.session_id)

        # Clear the session cookie
        cookie = f"{self.cookie_name}=; Path={self.path}; Max-Age=0"

        if self.domain:
            cookie += f"; Domain={self.domain}"

        if self.secure:
            cookie += "; Secure"

        if self.http_only:
            cookie += "; HttpOnly"

        if self.same_site:
            cookie += f"; SameSite={self.same_site}"

        # Add the cookie to the response
        if "Set-Cookie" in response.headers:
            response.headers["Set-Cookie"] = [response.headers["Set-Cookie"], cookie]
        else:
            response.headers["Set-Cookie"] = cookie

    def _parse_cookies(self, cookie_string: str) -> Dict[str, str]:
        """Parse cookies from a Cookie header."""
        cookies = {}
        if not cookie_string:
            return cookies

        for cookie in cookie_string.split(";"):
            cookie = cookie.strip()
            if "=" in cookie:
                name, value = cookie.split("=", 1)
                cookies[name.strip()] = value.strip()

        return cookies


def session_middleware(session_manager: SessionManager):
    """
    Create session middleware.

    Args:
        session_manager: Session manager

    Returns:
        Session middleware function
    """
    def middleware(request: Request):
        """
        Session middleware.

        This middleware adds a session object to the request and saves
        the session after the response is generated.
        """
        # Get the session
        session = session_manager.get_session(request)

        # Add the session to the request
        request.session = session

        # Set the current session in the session proxy
        from .session_proxy import set_current_session
        set_current_session(session)

        # Add a hook to save the session after the response is generated
        def save_session_hook(response: Response):
            session_manager.save_session(session, response)
            return response

        # Add a response hook to the request
        if not hasattr(request, 'response_hooks'):
            request.response_hooks = save_session_hook
        else:
            # Chain with existing hooks
            original_hook = request.response_hooks
            def chained_hook(response):
                response = original_hook(response)
                return save_session_hook(response)
            request.response_hooks = chained_hook

        return request

    return middleware
