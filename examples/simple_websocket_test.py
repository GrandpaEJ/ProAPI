"""
Simple WebSocket Test for ProAPI

This is a minimal example to test WebSocket functionality in ProAPI.
"""

import os
import sys
import asyncio

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
        "message": "Simple WebSocket Test",
        "endpoints": {
            "ws": "Echo WebSocket at /ws",
            "client": "HTML client at /client"
        }
    }

# HTML client
@app.get("/client")
def client(request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
            #messages { border: 1px solid #ccc; height: 300px; overflow-y: auto; margin-bottom: 10px; padding: 10px; }
            #form { display: flex; }
            #input { flex-grow: 1; padding: 8px; margin-right: 10px; }
            button { padding: 8px 16px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Simple WebSocket Test</h1>
        <div id="messages"></div>
        <form id="form">
            <input type="text" id="input" placeholder="Type a message..." />
            <button type="submit">Send</button>
        </form>
        
        <script>
            const messages = document.getElementById('messages');
            const form = document.getElementById('form');
            const input = document.getElementById('input');
            let socket = null;
            
            function connect() {
                socket = new WebSocket(`ws://${window.location.host}/ws`);
                
                socket.onopen = () => {
                    addMessage('Connected to server', 'system');
                };
                
                socket.onmessage = (event) => {
                    addMessage(`Server: ${event.data}`);
                };
                
                socket.onclose = () => {
                    addMessage('Disconnected from server', 'system');
                    // Try to reconnect after 3 seconds
                    setTimeout(connect, 3000);
                };
                
                socket.onerror = (error) => {
                    addMessage('WebSocket error', 'error');
                    console.error('WebSocket error:', error);
                };
            }
            
            function addMessage(message, className = '') {
                const div = document.createElement('div');
                div.textContent = message;
                if (className) div.className = className;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }
            
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const message = input.value;
                if (message && socket && socket.readyState === WebSocket.OPEN) {
                    addMessage(`You: ${message}`);
                    socket.send(message);
                    input.value = '';
                }
            });
            
            // Connect on page load
            connect();
        </script>
    </body>
    </html>
    """

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

if __name__ == "__main__":
    print("Simple WebSocket Test for ProAPI")
    print()
    print("Available endpoints:")
    print("  - HTTP: http://localhost:8000/")
    print("  - HTML Client: http://localhost:8000/client")
    print("  - WebSocket: ws://localhost:8000/ws")
    print()
    print("Open http://localhost:8000/client in your browser to test the WebSocket")
    print()
    
    # Run the application
    app.run(host="127.0.0.1", port=8000)
