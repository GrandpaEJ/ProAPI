"""
WebSocket middleware for ProAPI.

This module provides middleware support for WebSocket connections.
"""

from typing import Any, Callable, Dict, List, Optional, Union, Awaitable
import inspect
import functools

from .logging import app_logger
from .websocket import WebSocketConnection

class WebSocketMiddleware:
    """
    Base class for WebSocket middleware.
    
    WebSocket middleware can be used to intercept and modify WebSocket connections.
    """
    
    async def __call__(self, websocket: WebSocketConnection, next_middleware: Callable):
        """
        Process a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            next_middleware: Next middleware in the chain
            
        Returns:
            Result of the next middleware
        """
        # Default implementation just calls the next middleware
        return await next_middleware(websocket)

class AuthMiddleware(WebSocketMiddleware):
    """
    Authentication middleware for WebSocket connections.
    
    This middleware can be used to authenticate WebSocket connections.
    """
    
    def __init__(self, auth_func: Callable):
        """
        Initialize the authentication middleware.
        
        Args:
            auth_func: Function that authenticates a WebSocket connection
                Should return a user object or None if authentication fails
        """
        self.auth_func = auth_func
    
    async def __call__(self, websocket: WebSocketConnection, next_middleware: Callable):
        """
        Authenticate a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            next_middleware: Next middleware in the chain
            
        Returns:
            Result of the next middleware if authentication succeeds
        """
        # Call the authentication function
        if inspect.iscoroutinefunction(self.auth_func):
            user = await self.auth_func(websocket)
        else:
            user = self.auth_func(websocket)
        
        if user is None:
            # Authentication failed, close the connection
            await websocket.accept()
            await websocket.close(1008, "Authentication failed")
            return
        
        # Store the user in the connection
        websocket.user_data["user"] = user
        
        # Call the next middleware
        return await next_middleware(websocket)

class RateLimitMiddleware(WebSocketMiddleware):
    """
    Rate limiting middleware for WebSocket connections.
    
    This middleware can be used to limit the rate of messages from WebSocket connections.
    """
    
    def __init__(self, max_messages: int = 10, window_seconds: int = 1):
        """
        Initialize the rate limiting middleware.
        
        Args:
            max_messages: Maximum number of messages allowed in the window
            window_seconds: Window size in seconds
        """
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.message_counts = {}
    
    async def __call__(self, websocket: WebSocketConnection, next_middleware: Callable):
        """
        Rate limit a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            next_middleware: Next middleware in the chain
            
        Returns:
            Result of the next middleware
        """
        # Store the original receive method
        original_receive = websocket.receive
        
        # Create a wrapper for the receive method
        @functools.wraps(original_receive)
        async def rate_limited_receive():
            # Get the current time
            import time
            current_time = time.time()
            
            # Initialize message count for this connection
            if websocket not in self.message_counts:
                self.message_counts[websocket] = []
            
            # Remove old messages
            self.message_counts[websocket] = [
                t for t in self.message_counts[websocket]
                if current_time - t < self.window_seconds
            ]
            
            # Check if the rate limit is exceeded
            if len(self.message_counts[websocket]) >= self.max_messages:
                # Rate limit exceeded, close the connection
                await websocket.close(1008, "Rate limit exceeded")
                raise Exception("Rate limit exceeded")
            
            # Add the current time to the message count
            self.message_counts[websocket].append(current_time)
            
            # Call the original receive method
            return await original_receive()
        
        # Replace the receive method
        websocket.receive = rate_limited_receive
        
        try:
            # Call the next middleware
            return await next_middleware(websocket)
        finally:
            # Restore the original receive method
            websocket.receive = original_receive
            
            # Clean up
            if websocket in self.message_counts:
                del self.message_counts[websocket]

class LoggingMiddleware(WebSocketMiddleware):
    """
    Logging middleware for WebSocket connections.
    
    This middleware logs WebSocket connections and messages.
    """
    
    def __init__(self, log_messages: bool = True):
        """
        Initialize the logging middleware.
        
        Args:
            log_messages: Whether to log messages
        """
        self.log_messages = log_messages
    
    async def __call__(self, websocket: WebSocketConnection, next_middleware: Callable):
        """
        Log a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            next_middleware: Next middleware in the chain
            
        Returns:
            Result of the next middleware
        """
        # Log the connection
        client_info = f"{websocket.client_host}:{websocket.client_port}" if websocket.client_host else "unknown"
        app_logger.info(f"WebSocket connection from {client_info} to {websocket.path}")
        
        # Store the original methods
        original_receive = websocket.receive
        original_send = websocket.send
        
        # Create wrappers for the methods
        @functools.wraps(original_receive)
        async def logged_receive():
            message = await original_receive()
            
            if self.log_messages:
                if message["type"] == "websocket.receive":
                    if "text" in message:
                        app_logger.debug(f"WebSocket received text: {message['text']}")
                    elif "bytes" in message:
                        app_logger.debug(f"WebSocket received bytes: {len(message['bytes'])} bytes")
                elif message["type"] == "websocket.disconnect":
                    app_logger.info(f"WebSocket disconnected: {message.get('code', 1000)}")
            
            return message
        
        @functools.wraps(original_send)
        async def logged_send(message):
            if self.log_messages:
                if message["type"] == "websocket.send":
                    if "text" in message:
                        app_logger.debug(f"WebSocket sending text: {message['text']}")
                    elif "bytes" in message:
                        app_logger.debug(f"WebSocket sending bytes: {len(message['bytes'])} bytes")
                elif message["type"] == "websocket.close":
                    app_logger.info(f"WebSocket closing: {message.get('code', 1000)}")
            
            return await original_send(message)
        
        # Replace the methods
        websocket.receive = logged_receive
        websocket.send = logged_send
        
        try:
            # Call the next middleware
            return await next_middleware(websocket)
        finally:
            # Restore the original methods
            websocket.receive = original_receive
            websocket.send = original_send
            
            # Log the disconnection
            app_logger.info(f"WebSocket connection closed: {websocket.path}")

def create_middleware_chain(middlewares: List[WebSocketMiddleware], handler: Callable):
    """
    Create a middleware chain.
    
    Args:
        middlewares: List of middleware
        handler: Final handler
        
    Returns:
        Middleware chain
    """
    async def middleware_chain(websocket: WebSocketConnection):
        # Create the chain
        async def chain(index: int):
            if index < len(middlewares):
                return await middlewares[index](websocket, lambda ws: chain(index + 1))
            else:
                return await handler(websocket)
        
        # Start the chain
        return await chain(0)
    
    return middleware_chain
