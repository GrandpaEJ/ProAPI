# Advanced WebSocket Support in ProAPI

ProAPI provides comprehensive WebSocket support with advanced features like room management, broadcasting, middleware, and more.

## Basic Usage

Creating a WebSocket endpoint is as simple as using the `@app.websocket` decorator:

```python
from proapi import ProAPI

app = ProAPI()

@app.websocket("/ws")
async def websocket_handler(websocket):
    await websocket.accept()

    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Echo: {message}")
```

## WebSocket Connection Object

The `websocket` parameter passed to your handler is a `WebSocketConnection` object that provides methods for interacting with the WebSocket connection:

### Connection Management

- `await websocket.accept(subprotocol=None)`: Accept the WebSocket connection
- `await websocket.close(code=1000, reason=None)`: Close the WebSocket connection
- `websocket.closed`: Whether the connection is closed

### Receiving Messages

- `await websocket.receive_text()`: Receive a text message
- `await websocket.receive_json()`: Receive and parse a JSON message
- `await websocket.receive_bytes()`: Receive a binary message

### Sending Messages

- `await websocket.send_text(text)`: Send a text message
- `await websocket.send_json(data)`: Send a JSON message
- `await websocket.send_bytes(data)`: Send a binary message

### Connection Properties

- `websocket.path`: The request path
- `websocket.query_params`: Query parameters
- `websocket.headers`: HTTP headers
- `websocket.client_host`: Client IP address
- `websocket.client_port`: Client port
- `websocket.server_host`: Server IP address
- `websocket.server_port`: Server port
- `websocket.user_data`: Dictionary for storing user-defined data

## Room Management

ProAPI includes built-in room management for WebSocket connections:

### Joining and Leaving Rooms

```python
@app.websocket("/chat/{room}")
async def chat_room(websocket, room):
    await websocket.accept()

    # Join the room
    await websocket.join_room(room)

    try:
        # Handle messages
        while True:
            message = await websocket.receive_text()
            # Process message...
    finally:
        # Leave the room
        await websocket.leave_room(room)
```

### Room Management Methods

- `await websocket.join_room(room)`: Join a room
- `await websocket.leave_room(room)`: Leave a room
- `await websocket.get_rooms()`: Get all rooms this connection is in
- `await websocket.get_room_size(room)`: Get the number of connections in a room

## Broadcasting Messages

ProAPI makes it easy to broadcast messages to all connections in a room:

### Broadcasting Methods

- `await websocket.broadcast(room, message)`: Broadcast a text message to all other connections in a room
- `await websocket.broadcast_json(room, data)`: Broadcast a JSON message to all other connections in a room
- `await websocket.broadcast_bytes(room, data)`: Broadcast a binary message to all other connections in a room
- `await websocket.broadcast_to_all(room, message)`: Broadcast a text message to all connections in a room, including self
- `await websocket.broadcast_json_to_all(room, data)`: Broadcast a JSON message to all connections in a room, including self

### Example: Chat Application

```python
@app.websocket("/chat/{room}")
async def chat_room(websocket, room):
    await websocket.accept()
    await websocket.join_room(room)

    # Get username from query parameters
    username = websocket.query_params.get("username", "Anonymous")
    websocket.user_data["username"] = username

    # Broadcast join message
    await websocket.broadcast_json(room, {
        "type": "system",
        "message": f"{username} has joined the room"
    })

    try:
        while True:
            data = await websocket.receive_json()
            data["username"] = username

            # Broadcast message to all users in the room
            await websocket.broadcast_json_to_all(room, data)
    finally:
        # Leave the room and broadcast leave message
        await websocket.leave_room(room)
        await websocket.broadcast_json(room, {
            "type": "system",
            "message": f"{username} has left the room"
        })
```

## WebSocket Middleware

ProAPI supports middleware for WebSocket connections, allowing you to add authentication, logging, rate limiting, and more:

### Global WebSocket Middleware

Global middleware is applied to all WebSocket routes:

```python
from proapi import ProAPI
from proapi.websocket.websocket_middleware import LoggingMiddleware

app = ProAPI()

# Create custom logging middleware
class CustomLoggingMiddleware(LoggingMiddleware):
    async def __call__(self, websocket, next_middleware):
        print(f"WebSocket connection to {websocket.path}")
        return await super().__call__(websocket, next_middleware)

# Add global WebSocket middleware
app.websocket_middlewares = [CustomLoggingMiddleware()]
```

### Route-Specific Middleware

You can also apply middleware to specific routes:

```python
from proapi.websocket.websocket_middleware import AuthMiddleware

# Authentication function
def authenticate(websocket):
    token = websocket.query_params.get("token")
    if token == "secret":
        return {"username": "admin"}
    return None

# Create authentication middleware
auth_middleware = AuthMiddleware(authenticate)

# Apply middleware to a specific route
@app.websocket("/secure", middlewares=[auth_middleware])
async def secure_websocket(websocket):
    await websocket.accept()

    # Get the authenticated user
    user = websocket.user_data.get("user")

    await websocket.send_json({
        "message": f"Welcome, {user['username']}!"
    })

    # Handle messages...
```

### Built-in Middleware

ProAPI includes several built-in middleware classes:

#### Authentication Middleware

```python
from proapi.websocket.websocket_middleware import AuthMiddleware

# Create authentication middleware
auth_middleware = AuthMiddleware(authenticate_function)

@app.websocket("/secure", middlewares=[auth_middleware])
async def secure_websocket(websocket):
    # Authentication already done by middleware
    await websocket.accept()
    # ...
```

#### Rate Limiting Middleware

```python
from proapi.websocket.websocket_middleware import RateLimitMiddleware

# Create rate limiting middleware (5 messages per 10 seconds)
rate_limit = RateLimitMiddleware(max_messages=5, window_seconds=10)

@app.websocket("/limited", middlewares=[rate_limit])
async def limited_websocket(websocket):
    await websocket.accept()
    # ...
```

#### Logging Middleware

```python
from proapi.websocket.websocket_middleware import LoggingMiddleware

# Create logging middleware
logging_middleware = LoggingMiddleware(log_messages=True)

@app.websocket("/logged", middlewares=[logging_middleware])
async def logged_websocket(websocket):
    await websocket.accept()
    # ...
```

### Creating Custom Middleware

You can create custom middleware by extending the `WebSocketMiddleware` class:

```python
from proapi.websocket.websocket_middleware import WebSocketMiddleware

class CustomMiddleware(WebSocketMiddleware):
    async def __call__(self, websocket, next_middleware):
        # Do something before the handler
        print("Before handler")

        # Call the next middleware or handler
        result = await next_middleware(websocket)

        # Do something after the handler
        print("After handler")

        return result
```

## Error Handling

WebSocket connections can be closed unexpectedly. Use try/except blocks to handle errors:

```python
@app.websocket("/ws")
async def websocket_handler(websocket):
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Echo: {message}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Ensure the connection is closed
        if not websocket.closed:
            await websocket.close()
```

## Advanced Example

Here's a more advanced example that combines room management, broadcasting, and middleware:

```python
from proapi import ProAPI
from proapi.websocket.websocket_middleware import AuthMiddleware, LoggingMiddleware

app = ProAPI()

# Add global logging middleware
app.websocket_middlewares = [LoggingMiddleware()]

# Authentication function
def authenticate(websocket):
    token = websocket.query_params.get("token")
    if token == "secret":
        return {"username": "admin"}
    return None

# Create authentication middleware
auth_middleware = AuthMiddleware(authenticate)

@app.websocket("/chat/{room}", middlewares=[auth_middleware])
async def secure_chat(websocket, room):
    await websocket.accept()
    await websocket.join_room(room)

    # Get the authenticated user
    user = websocket.user_data.get("user")
    username = user["username"]

    # Broadcast join message
    await websocket.broadcast_json(room, {
        "type": "system",
        "message": f"{username} has joined the room"
    })

    try:
        while True:
            data = await websocket.receive_json()
            data["username"] = username

            # Broadcast message to all users in the room
            await websocket.broadcast_json_to_all(room, data)
    finally:
        # Leave the room and broadcast leave message
        await websocket.leave_room(room)
        await websocket.broadcast_json(room, {
            "type": "system",
            "message": f"{username} has left the room"
        })
```

## Client-Side Example

Here's a JavaScript example for connecting to a WebSocket endpoint with authentication:

```javascript
// Connect to a secure WebSocket endpoint
const socket = new WebSocket('ws://localhost:8000/secure?token=secret');

socket.onopen = () => {
    console.log('Connected');

    // Send a JSON message
    socket.send(JSON.stringify({
        type: 'message',
        content: 'Hello, server!'
    }));
};

socket.onmessage = (event) => {
    // Parse JSON messages
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

socket.onclose = (event) => {
    console.log('Disconnected with code:', event.code);
};

socket.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

## Performance Considerations

- WebSocket connections are maintained for the duration of the connection, which can consume server resources
- For high-traffic applications, consider implementing a heartbeat mechanism to detect and close stale connections
- Use a production-grade server like uvicorn with multiple workers for better performance
- The room management system uses weak references to avoid memory leaks when connections are closed
- Consider using the rate limiting middleware to prevent abuse

## Using with Fast Mode

WebSocket support works seamlessly with ProAPI's fast mode:

```python
if __name__ == "__main__":
    app.run(fast=True)  # WebSockets will work with fast mode
```
