"""
WebSocket Example for ProAPI

This example demonstrates the WebSocket functionality in ProAPI.
It creates a simple echo server and a chat room.

To run this example:
    python examples/websocket_example.py

Or using the CLI:
    proapi run examples/websocket_example.py

Test with a WebSocket client or browser console:
    const socket = new WebSocket('ws://localhost:8000/ws');
    socket.onopen = () => socket.send('Hello, ProAPI!');
    socket.onmessage = (event) => console.log('Received:', event.data);
"""

import os
import sys
import json
import asyncio
from datetime import datetime

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create a ProAPI application
app = ProAPI(
    debug=True,
    fast_mode=False,  # Disable fast mode for WebSocket testing
    enable_docs=True
)

# Basic HTTP route
@app.get("/")
def index(request):
    return {
        "message": "WebSocket Example",
        "endpoints": {
            "ws": "Basic echo WebSocket at /ws",
            "chat": "Chat room WebSocket at /chat/{room_name}"
        }
    }

# HTML page with WebSocket client
@app.get("/client")
def client(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ProAPI WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            #messages { border: 1px solid #ccc; height: 300px; overflow-y: auto; margin-bottom: 10px; padding: 10px; }
            #input-form { display: flex; }
            #message-input { flex-grow: 1; padding: 8px; margin-right: 10px; }
            button { padding: 8px 16px; background: #4CAF50; color: white; border: none; cursor: pointer; }
            .system { color: #888; }
            .error { color: #f44336; }
        </style>
    </head>
    <body>
        <h1>ProAPI WebSocket Test</h1>

        <h2>Echo Test</h2>
        <div id="echo-messages" class="messages"></div>
        <form id="echo-form" class="input-form">
            <input type="text" id="echo-input" placeholder="Type a message..." />
            <button type="submit">Send</button>
        </form>

        <h2>Chat Room</h2>
        <div>
            <label for="room">Room:</label>
            <input type="text" id="room" value="general" />
            <label for="username">Username:</label>
            <input type="text" id="username" value="User" />
            <button id="join-btn">Join</button>
            <button id="leave-btn" disabled>Leave</button>
        </div>
        <div id="chat-messages" class="messages"></div>
        <form id="chat-form" class="input-form">
            <input type="text" id="chat-input" placeholder="Type a message..." disabled />
            <button type="submit" disabled>Send</button>
        </form>

        <script>
            // Echo WebSocket
            const echoMessages = document.getElementById('echo-messages');
            const echoForm = document.getElementById('echo-form');
            const echoInput = document.getElementById('echo-input');
            let echoSocket = null;

            function connectEcho() {
                echoSocket = new WebSocket(`ws://${window.location.host}/ws`);

                echoSocket.onopen = () => {
                    addEchoMessage('Connected to echo server', 'system');
                };

                echoSocket.onmessage = (event) => {
                    addEchoMessage(`Server: ${event.data}`);
                };

                echoSocket.onclose = () => {
                    addEchoMessage('Disconnected from echo server', 'system');
                    // Try to reconnect after 3 seconds
                    setTimeout(connectEcho, 3000);
                };

                echoSocket.onerror = (error) => {
                    addEchoMessage('WebSocket error', 'error');
                    console.error('WebSocket error:', error);
                };
            }

            function addEchoMessage(message, className = '') {
                const div = document.createElement('div');
                div.textContent = message;
                if (className) div.className = className;
                echoMessages.appendChild(div);
                echoMessages.scrollTop = echoMessages.scrollHeight;
            }

            echoForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const message = echoInput.value;
                if (message && echoSocket && echoSocket.readyState === WebSocket.OPEN) {
                    addEchoMessage(`You: ${message}`);
                    echoSocket.send(message);
                    echoInput.value = '';
                }
            });

            // Chat WebSocket
            const chatMessages = document.getElementById('chat-messages');
            const chatForm = document.getElementById('chat-form');
            const chatInput = document.getElementById('chat-input');
            const roomInput = document.getElementById('room');
            const usernameInput = document.getElementById('username');
            const joinBtn = document.getElementById('join-btn');
            const leaveBtn = document.getElementById('leave-btn');
            let chatSocket = null;

            function joinChat() {
                const room = roomInput.value || 'general';
                const username = usernameInput.value || 'User';

                chatSocket = new WebSocket(`ws://${window.location.host}/chat/${room}?username=${encodeURIComponent(username)}`);

                chatSocket.onopen = () => {
                    addChatMessage('Connected to chat server', 'system');
                    chatInput.disabled = false;
                    chatForm.querySelector('button').disabled = false;
                    joinBtn.disabled = true;
                    leaveBtn.disabled = false;
                    roomInput.disabled = true;
                    usernameInput.disabled = true;
                };

                chatSocket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.type === 'system') {
                            addChatMessage(data.message, 'system');
                        } else {
                            addChatMessage(`${data.username}: ${data.message}`);
                        }
                    } catch (e) {
                        addChatMessage(`Received: ${event.data}`);
                    }
                };

                chatSocket.onclose = () => {
                    addChatMessage('Disconnected from chat server', 'system');
                    chatInput.disabled = true;
                    chatForm.querySelector('button').disabled = true;
                    joinBtn.disabled = false;
                    leaveBtn.disabled = true;
                    roomInput.disabled = false;
                    usernameInput.disabled = false;
                };

                chatSocket.onerror = (error) => {
                    addChatMessage('WebSocket error', 'error');
                    console.error('WebSocket error:', error);
                };
            }

            function leaveChat() {
                if (chatSocket) {
                    chatSocket.close();
                }
            }

            function addChatMessage(message, className = '') {
                const div = document.createElement('div');
                div.textContent = message;
                if (className) div.className = className;
                chatMessages.appendChild(div);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const message = chatInput.value;
                if (message && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
                    chatSocket.send(JSON.stringify({
                        message: message
                    }));
                    chatInput.value = '';
                }
            });

            joinBtn.addEventListener('click', joinChat);
            leaveBtn.addEventListener('click', leaveChat);

            // Connect to echo server on page load
            connectEcho();
        </script>
    </body>
    </html>
    """
    return html

# Simple echo WebSocket
@app.websocket("/ws")
async def websocket_echo(websocket):
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Echo: {message}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if not websocket.closed:
            await websocket.close()

# Store active chat connections
chat_rooms = {}

# Chat room WebSocket
@app.websocket("/chat/{room}")
async def chat_room(websocket, room):
    # Create room if it doesn't exist
    if room not in chat_rooms:
        chat_rooms[room] = []

    # Accept the connection
    await websocket.accept()

    # Get username from query parameters
    username = websocket.query_params.get("username", ["Anonymous"])[0]

    # Add to room
    chat_rooms[room].append(websocket)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "system",
            "message": f"Welcome to room: {room}",
            "users": len(chat_rooms[room])
        })

        # Broadcast join message to others
        for conn in chat_rooms[room]:
            if conn != websocket:
                await conn.send_json({
                    "type": "system",
                    "message": f"{username} has joined the room",
                    "users": len(chat_rooms[room])
                })

        # Handle messages
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")

            # Broadcast to all users in the room
            for conn in chat_rooms[room]:
                await conn.send_json({
                    "username": username,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                })
    except Exception as e:
        print(f"Chat WebSocket error: {e}")
    finally:
        # Remove from room
        if room in chat_rooms and websocket in chat_rooms[room]:
            chat_rooms[room].remove(websocket)

            # Broadcast leave message
            for conn in chat_rooms[room]:
                await conn.send_json({
                    "type": "system",
                    "message": f"{username} has left the room",
                    "users": len(chat_rooms[room])
                })

            # Clean up empty rooms
            if not chat_rooms[room]:
                del chat_rooms[room]

if __name__ == "__main__":
    print("WebSocket Example for ProAPI")
    print()
    print("Available endpoints:")
    print("  - HTTP: http://localhost:8000/")
    print("  - HTTP Client: http://localhost:8000/client")
    print("  - WebSocket Echo: ws://localhost:8000/ws")
    print("  - WebSocket Chat: ws://localhost:8000/chat/{room}?username={username}")
    print()
    print("Open http://localhost:8000/client in your browser to test the WebSockets")
    print()

    # Run the application
    app.run(host="127.0.0.1", port=8000)
