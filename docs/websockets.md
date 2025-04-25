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

## Example: Chat Application

Here's a simple chat application using WebSockets:

```python
from proapi import ProAPI

app = ProAPI()

# Store active connections
connections = {}

@app.websocket("/chat/{room}")
async def chat_room(websocket, room):
    # Create room if it doesn't exist
    if room not in connections:
        connections[room] = []
    
    # Accept the connection
    await websocket.accept()
    
    # Add to room
    connections[room].append(websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "system",
            "message": f"Welcome to room: {room}",
            "users": len(connections[room])
        })
        
        # Broadcast join message
        for conn in connections[room]:
            if conn != websocket:
                await conn.send_json({
                    "type": "system",
                    "message": "A new user has joined",
                    "users": len(connections[room])
                })
        
        # Handle messages
        while True:
            data = await websocket.receive_json()
            
            # Broadcast to all users in the room
            for conn in connections[room]:
                await conn.send_json(data)
    finally:
        # Remove from room
        if room in connections and websocket in connections[room]:
            connections[room].remove(websocket)
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
