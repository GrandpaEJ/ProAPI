# WebSocket Support in ProAPI

ProAPI now includes built-in support for WebSockets, allowing you to create real-time applications with ease.

## Basic Usage

Creating a WebSocket endpoint is as simple as using the `@app.websocket` decorator:

```python
from proapi import ProAPI

app = ProAPI()

@app.websocket("/ws")
async def websocket_handler(websocket):
    # Accept the connection
    await websocket.accept()

    # Echo messages back to the client
    while True:
        message = await websocket.receive_text()
        await websocket.send_text(f"Echo: {message}")
```

## WebSocket Connection Object

The `websocket` parameter passed to your handler is a `WebSocketConnection` object that provides methods for interacting with the WebSocket connection:

### Connection Management

- `await websocket.accept(subprotocol=None)`: Accept the WebSocket connection
- `await websocket.close(code=1000, reason=None)`: Close the WebSocket connection

### Receiving Messages

- `await websocket.receive_text()`: Receive a text message
- `await websocket.receive_json()`: Receive and parse a JSON message
- `await websocket.receive_bytes()`: Receive a binary message

### Sending Messages

- `await websocket.send_text(text)`: Send a text message
- `await websocket.send_json(data)`: Send a JSON message
- `await websocket.send_bytes(data)`: Send a binary message

### Properties

- `websocket.path`: The request path
- `websocket.query_params`: Query parameters
- `websocket.headers`: HTTP headers
- `websocket.closed`: Whether the connection is closed
- `websocket.client_host`: Client IP address
- `websocket.client_port`: Client port
- `websocket.server_host`: Server IP address
- `websocket.server_port`: Server port
- `websocket.user_data`: Dictionary for storing user-defined data

## Path Parameters

You can use path parameters in WebSocket routes just like in HTTP routes:

```python
@app.websocket("/chat/{room}")
async def chat_room(websocket, room):
    await websocket.accept()
    await websocket.send_text(f"Welcome to room: {room}")

    # Handle messages
    while True:
        message = await websocket.receive_text()
        # Process message...
```

## Room Management

ProAPI includes built-in room management for WebSocket connections:

```python
# Join a room
await websocket.join_room(room)

# Leave a room
await websocket.leave_room(room)

# Get all rooms this connection is in
rooms = await websocket.get_rooms()

# Get the number of connections in a room
count = await websocket.get_room_size(room)
```

## Broadcasting Messages

You can broadcast messages to all connections in a room:

```python
# Broadcast a text message to all other connections in a room
await websocket.broadcast(room, "Hello everyone!")

# Broadcast a JSON message to all other connections in a room
await websocket.broadcast_json(room, {"message": "Hello everyone!"})

# Broadcast a text message to all connections in a room, including self
await websocket.broadcast_to_all(room, "Hello everyone!")

# Broadcast a JSON message to all connections in a room, including self
await websocket.broadcast_json_to_all(room, {"message": "Hello everyone!"})
```

## Example: Chat Application

Here's a simple chat application using WebSockets:

```python
from proapi import ProAPI

app = ProAPI()

@app.websocket("/chat/{room}")
async def chat_room(websocket, room):
    # Accept the connection
    await websocket.accept()

    # Join the room
    await websocket.join_room(room)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "system",
            "message": f"Welcome to room: {room}",
            "users": await websocket.get_room_size(room)
        })

        # Broadcast join message
        await websocket.broadcast_json(room, {
            "type": "system",
            "message": "A new user has joined",
            "users": await websocket.get_room_size(room)
        })

        # Handle messages
        while True:
            data = await websocket.receive_json()

            # Broadcast message to all users in the room
            await websocket.broadcast_json_to_all(room, data)
    finally:
        # Leave the room
        await websocket.leave_room(room)
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

## Using with Fast Mode

WebSocket support works seamlessly with ProAPI's fast mode:

```python
if __name__ == "__main__":
    app.run(fast=True)  # WebSockets will work with fast mode
```

## Client-Side Example

Here's a simple JavaScript example for connecting to a WebSocket endpoint:

```javascript
const socket = new WebSocket('ws://localhost:8000/ws');

socket.onopen = () => {
    console.log('Connected');
    socket.send('Hello, server!');
};

socket.onmessage = (event) => {
    console.log('Received:', event.data);
};

socket.onclose = () => {
    console.log('Disconnected');
};

socket.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

## Performance Considerations

- WebSocket connections are maintained for the duration of the connection, which can consume server resources
- For high-traffic applications, consider implementing a heartbeat mechanism to detect and close stale connections
- Use a production-grade server like uvicorn with multiple workers for better performance
