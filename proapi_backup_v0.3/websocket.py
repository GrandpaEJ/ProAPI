"""
WebSocket support for ProAPI.

This module provides WebSocket support for ProAPI applications.
"""

import json
import asyncio
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable, Set
from collections import defaultdict
import weakref

from .logging import app_logger

# Global room manager for WebSocket connections
class RoomManager:
    """Room manager for WebSocket connections."""

    def __init__(self):
        """Initialize the room manager."""
        self.rooms = defaultdict(set)
        self.connection_rooms = defaultdict(set)

    def join(self, connection, room: str):
        """Add a connection to a room."""
        # Use weak references to avoid memory leaks
        weak_conn = weakref.ref(connection, self._connection_closed)
        self.rooms[room].add(weak_conn)
        self.connection_rooms[weak_conn].add(room)
        app_logger.debug(f"Connection joined room: {room}")
        return len(self.rooms[room])

    def leave(self, connection, room: str):
        """Remove a connection from a room."""
        weak_conn = weakref.ref(connection)
        if weak_conn in self.rooms[room]:
            self.rooms[room].remove(weak_conn)
            self.connection_rooms[weak_conn].discard(room)
            if not self.connection_rooms[weak_conn]:
                del self.connection_rooms[weak_conn]
            app_logger.debug(f"Connection left room: {room}")
            return len(self.rooms[room])
        return len(self.rooms[room])

    def leave_all(self, connection):
        """Remove a connection from all rooms."""
        weak_conn = weakref.ref(connection)
        rooms_to_leave = list(self.connection_rooms[weak_conn])
        for room in rooms_to_leave:
            self.leave(connection, room)
        app_logger.debug(f"Connection left all rooms")

    def get_connections(self, room: str):
        """Get all connections in a room."""
        # Filter out dead weak references
        active_connections = [ref() for ref in self.rooms[room] if ref() is not None]
        return active_connections

    def get_rooms(self, connection):
        """Get all rooms a connection is in."""
        weak_conn = weakref.ref(connection)
        return list(self.connection_rooms[weak_conn])

    def room_size(self, room: str):
        """Get the number of connections in a room."""
        # Count only active connections
        return len([ref for ref in self.rooms[room] if ref() is not None])

    def _connection_closed(self, weak_ref):
        """Called when a connection is garbage collected."""
        if weak_ref in self.connection_rooms:
            rooms = list(self.connection_rooms[weak_ref])
            for room in rooms:
                if weak_ref in self.rooms[room]:
                    self.rooms[room].remove(weak_ref)
            del self.connection_rooms[weak_ref]

# Create a global room manager
room_manager = RoomManager()

class WebSocketConnection:
    """
    WebSocket connection.

    This class represents a WebSocket connection and provides methods for sending and receiving messages.
    """

    def __init__(self, scope, receive, send):
        """
        Initialize a WebSocket connection.

        Args:
            scope: ASGI scope
            receive: ASGI receive function
            send: ASGI send function
        """
        self.scope = scope
        self.receive = receive
        self.send = send
        self.client_state = "CONNECTING"
        self.server_state = "CONNECTING"
        self.path = scope["path"]
        self.query_params = {}
        self.headers = {}
        self.closed = False

        # User data storage for application use
        self.user_data = {}

        # Extract query parameters
        query_string = scope.get("query_string", b"").decode("utf-8")
        if query_string:
            for param in query_string.split("&"):
                if "=" in param:
                    k, v = param.split("=", 1)
                    if k in self.query_params:
                        if isinstance(self.query_params[k], list):
                            self.query_params[k].append(v)
                        else:
                            self.query_params[k] = [self.query_params[k], v]
                    else:
                        self.query_params[k] = v

        # Extract headers
        for k, v in scope["headers"]:
            self.headers[k.decode("utf-8")] = v.decode("utf-8")

        # Extract client info
        self.client_host = None
        self.client_port = None
        if "client" in scope:
            self.client_host, self.client_port = scope["client"]

        # Extract server info
        self.server_host = None
        self.server_port = None
        if "server" in scope:
            self.server_host, self.server_port = scope["server"]

    async def accept(self, subprotocol: Optional[str] = None):
        """
        Accept the WebSocket connection.

        Args:
            subprotocol: WebSocket subprotocol
        """
        if self.client_state == "CONNECTING":
            await self.send({
                "type": "websocket.accept",
                "subprotocol": subprotocol
            })
            self.server_state = "CONNECTED"

    async def receive_text(self) -> str:
        """
        Receive a text message.

        Returns:
            Text message
        """
        if self.client_state != "CONNECTED":
            await self.ensure_connected()

        message = await self.receive()

        if message["type"] == "websocket.disconnect":
            self.client_state = "DISCONNECTED"
            self.closed = True
            raise ConnectionClosed(message.get("code", 1000))

        assert message["type"] == "websocket.receive"

        if "text" not in message:
            raise ValueError("Expected text message, got binary")

        return message["text"]

    async def receive_json(self) -> Any:
        """
        Receive a JSON message.

        Returns:
            Parsed JSON message
        """
        text = await self.receive_text()
        return json.loads(text)

    async def receive_bytes(self) -> bytes:
        """
        Receive a binary message.

        Returns:
            Binary message
        """
        if self.client_state != "CONNECTED":
            await self.ensure_connected()

        message = await self.receive()

        if message["type"] == "websocket.disconnect":
            self.client_state = "DISCONNECTED"
            self.closed = True
            raise ConnectionClosed(message.get("code", 1000))

        assert message["type"] == "websocket.receive"

        if "bytes" not in message:
            raise ValueError("Expected binary message, got text")

        return message["bytes"]

    async def send_text(self, text: str):
        """
        Send a text message.

        Args:
            text: Text message
        """
        if self.server_state != "CONNECTED":
            raise RuntimeError("WebSocket is not connected")

        await self.send({
            "type": "websocket.send",
            "text": text
        })

    async def send_json(self, data: Any):
        """
        Send a JSON message.

        Args:
            data: Data to send as JSON
        """
        text = json.dumps(data)
        await self.send_text(text)

    async def send_bytes(self, data: bytes):
        """
        Send a binary message.

        Args:
            data: Binary data
        """
        if self.server_state != "CONNECTED":
            raise RuntimeError("WebSocket is not connected")

        await self.send({
            "type": "websocket.send",
            "bytes": data
        })

    async def close(self, code: int = 1000, reason: Optional[str] = None):
        """
        Close the WebSocket connection.

        Args:
            code: Close code
            reason: Close reason
        """
        if self.server_state != "CONNECTED":
            return

        # Leave all rooms before closing
        room_manager.leave_all(self)

        await self.send({
            "type": "websocket.close",
            "code": code,
            "reason": reason
        })

        self.server_state = "DISCONNECTED"
        self.closed = True

    # Room management methods

    async def join_room(self, room: str):
        """
        Join a room.

        Args:
            room: Room name

        Returns:
            Number of connections in the room
        """
        return room_manager.join(self, room)

    async def leave_room(self, room: str):
        """
        Leave a room.

        Args:
            room: Room name

        Returns:
            Number of connections in the room
        """
        return room_manager.leave(self, room)

    async def get_rooms(self):
        """
        Get all rooms this connection is in.

        Returns:
            List of room names
        """
        return room_manager.get_rooms(self)

    # Broadcast methods

    async def broadcast(self, room: str, message: str):
        """
        Broadcast a text message to all connections in a room.

        Args:
            room: Room name
            message: Text message
        """
        connections = room_manager.get_connections(room)
        for connection in connections:
            if connection != self and not connection.closed:
                await connection.send_text(message)

    async def broadcast_json(self, room: str, data: Any):
        """
        Broadcast a JSON message to all connections in a room.

        Args:
            room: Room name
            data: Data to send as JSON
        """
        connections = room_manager.get_connections(room)
        for connection in connections:
            if connection != self and not connection.closed:
                await connection.send_json(data)

    async def broadcast_bytes(self, room: str, data: bytes):
        """
        Broadcast a binary message to all connections in a room.

        Args:
            room: Room name
            data: Binary data
        """
        connections = room_manager.get_connections(room)
        for connection in connections:
            if connection != self and not connection.closed:
                await connection.send_bytes(data)

    async def broadcast_to_all(self, room: str, message: str):
        """
        Broadcast a text message to all connections in a room, including self.

        Args:
            room: Room name
            message: Text message
        """
        connections = room_manager.get_connections(room)
        for connection in connections:
            if not connection.closed:
                await connection.send_text(message)

    async def broadcast_json_to_all(self, room: str, data: Any):
        """
        Broadcast a JSON message to all connections in a room, including self.

        Args:
            room: Room name
            data: Data to send as JSON
        """
        connections = room_manager.get_connections(room)
        for connection in connections:
            if not connection.closed:
                await connection.send_json(data)

    async def get_room_size(self, room: str):
        """
        Get the number of connections in a room.

        Args:
            room: Room name

        Returns:
            Number of connections in the room
        """
        return room_manager.room_size(room)

    async def ensure_connected(self):
        """Ensure the WebSocket is connected."""
        if self.client_state != "CONNECTING":
            raise RuntimeError("WebSocket is not connecting")

        message = await self.receive()

        if message["type"] == "websocket.connect":
            self.client_state = "CONNECTED"
            await self.accept()
        else:
            self.client_state = "DISCONNECTED"
            self.closed = True
            raise ConnectionClosed(1006)  # Abnormal Closure

class ConnectionClosed(Exception):
    """
    Exception raised when a WebSocket connection is closed.
    """

    def __init__(self, code: int = 1000):
        """
        Initialize the exception.

        Args:
            code: Close code
        """
        self.code = code
        super().__init__(f"WebSocket connection closed with code {code}")

class WebSocketRoute:
    """
    WebSocket route.

    This class represents a WebSocket route in the application.
    """

    def __init__(self, path: str, handler: Callable, name: Optional[str] = None, middlewares: List = None):
        """
        Initialize a WebSocket route.

        Args:
            path: URL path pattern
            handler: Function to handle the WebSocket connection
            name: Optional name for the route
            middlewares: List of middleware to apply to this route
        """
        from .routing import Route

        # Create a dummy Route object to reuse the path pattern logic
        dummy_route = Route("GET", path, lambda: None)

        self.path = path
        self.pattern = dummy_route.pattern
        self.handler = handler
        self.name = name or handler.__name__
        self.middlewares = middlewares or []

    def match(self, path: str) -> bool:
        """
        Check if this route matches the given path.

        Args:
            path: URL path

        Returns:
            True if the route matches, False otherwise
        """
        return self.pattern.match(path) is not None

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

        return match.groupdict()

    async def __call__(self, scope, receive, send):
        """
        Handle a WebSocket connection.

        Args:
            scope: ASGI scope
            receive: ASGI receive function
            send: ASGI send function
        """
        # Create WebSocket connection
        websocket = WebSocketConnection(scope, receive, send)

        # Extract path parameters
        path_params = self.extract_params(scope["path"])

        try:
            # Create the handler with path parameters
            async def handler(ws):
                return await self.handler(ws, **path_params)

            # Apply middleware if any
            if self.middlewares:
                from .websocket_middleware import create_middleware_chain
                handler = create_middleware_chain(self.middlewares, handler)

            # Call the handler
            await handler(websocket)
        except ConnectionClosed:
            # Connection closed normally
            pass
        except Exception as e:
            # Log the error
            app_logger.exception(f"Error in WebSocket handler: {e}")

            # Close the connection if it's still open
            if not websocket.closed:
                await websocket.close(1011)  # Internal Error
        finally:
            # Ensure the connection is closed
            if not websocket.closed:
                await websocket.close(1000)  # Normal Closure
