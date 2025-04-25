"""
WebSocket Load Test for ProAPI

This script tests how ProAPI handles multiple concurrent WebSocket connections.
It starts a ProAPI server and then uses asyncio to create multiple WebSocket clients.
"""

import os
import sys
import time
import json
import asyncio
import statistics
import argparse
from datetime import datetime
import threading
import websockets
import random
import string

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI
import proapi.asgi_adapter_fix as asgi_fix

# Create a ProAPI application
app = ProAPI(
    debug=False,  # Disable debug mode for better performance
    fast_mode=False,  # Disable fast mode for WebSocket testing
    enable_docs=True
)

# Set the global app variable for uvicorn to import
asgi_fix.set_app(app)

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
            try:
                await websocket.close()
            except Exception:
                pass

# Chat room WebSocket
chat_rooms = {}

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
        for conn in list(chat_rooms[room]):
            if conn != websocket and not conn.closed:
                try:
                    await conn.send_json({
                        "type": "system",
                        "message": f"{username} has joined the room",
                        "users": len(chat_rooms[room])
                    })
                except Exception:
                    # Skip connections that are closed or have errors
                    continue
        
        # Handle messages
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            # Broadcast to all users in the room
            for conn in list(chat_rooms[room]):
                if conn.closed:
                    # Remove closed connections
                    if conn in chat_rooms[room]:
                        chat_rooms[room].remove(conn)
                    continue
                
                try:
                    await conn.send_json({
                        "username": username,
                        "message": message,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception:
                    # Remove connections that have errors
                    if conn in chat_rooms[room]:
                        chat_rooms[room].remove(conn)
    except Exception as e:
        print(f"Chat WebSocket error: {e}")
    finally:
        # Remove from room
        if room in chat_rooms and websocket in chat_rooms[room]:
            chat_rooms[room].remove(websocket)
            
            # Clean up empty rooms
            if not chat_rooms[room]:
                del chat_rooms[room]

# Start the server in a separate thread
def start_server(host="127.0.0.1", port=8000):
    import threading
    import uvicorn
    
    def run_server():
        uvicorn.run("proapi.asgi_adapter_fix:app", host=host, port=port)
    
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for the server to start
    time.sleep(2)
    return server_thread

# WebSocket client for load testing
class WebSocketClient:
    def __init__(self, uri, client_id):
        self.uri = uri
        self.client_id = client_id
        self.connection = None
        self.connected = False
        self.messages_sent = 0
        self.messages_received = 0
        self.response_times = []
        self.errors = []
        self.last_message_time = None
    
    async def connect(self):
        try:
            self.connection = await websockets.connect(self.uri)
            self.connected = True
            return True
        except Exception as e:
            self.errors.append(f"Connection error: {e}")
            return False
    
    async def send_message(self, message):
        if not self.connected:
            return False
        
        try:
            self.last_message_time = time.time()
            await self.connection.send(message)
            self.messages_sent += 1
            return True
        except Exception as e:
            self.errors.append(f"Send error: {e}")
            self.connected = False
            return False
    
    async def receive_message(self):
        if not self.connected:
            return None
        
        try:
            message = await asyncio.wait_for(self.connection.recv(), timeout=5.0)
            if self.last_message_time:
                response_time = (time.time() - self.last_message_time) * 1000  # ms
                self.response_times.append(response_time)
            self.messages_received += 1
            return message
        except asyncio.TimeoutError:
            self.errors.append("Timeout waiting for response")
            return None
        except Exception as e:
            self.errors.append(f"Receive error: {e}")
            self.connected = False
            return None
    
    async def close(self):
        if self.connected:
            try:
                await self.connection.close()
            except Exception:
                pass
            self.connected = False
    
    def get_stats(self):
        return {
            "client_id": self.client_id,
            "connected": self.connected,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "avg_response_time_ms": statistics.mean(self.response_times) if self.response_times else 0,
            "min_response_time_ms": min(self.response_times) if self.response_times else 0,
            "max_response_time_ms": max(self.response_times) if self.response_times else 0,
            "errors": self.errors
        }

# Load test for WebSockets
class WebSocketLoadTest:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.clients = []
    
    async def run_echo_test(self, num_clients=10, messages_per_client=10, delay_ms=100):
        """Test the echo WebSocket endpoint with multiple clients."""
        print(f"\nRunning echo WebSocket test with {num_clients} clients, {messages_per_client} messages per client")
        
        # Create and connect clients
        self.clients = []
        for i in range(num_clients):
            client = WebSocketClient(f"ws://{self.host}:{self.port}/ws", f"echo-{i}")
            if await client.connect():
                self.clients.append(client)
        
        connected_clients = len(self.clients)
        print(f"  Connected clients: {connected_clients}/{num_clients}")
        
        if not connected_clients:
            print("  No clients connected, aborting test")
            return
        
        # Send and receive messages
        tasks = []
        for client in self.clients:
            tasks.append(self.client_echo_session(client, messages_per_client, delay_ms))
        
        await asyncio.gather(*tasks)
        
        # Close connections
        for client in self.clients:
            await client.close()
        
        # Analyze results
        total_sent = sum(client.messages_sent for client in self.clients)
        total_received = sum(client.messages_received for client in self.clients)
        all_response_times = []
        for client in self.clients:
            all_response_times.extend(client.response_times)
        
        if all_response_times:
            avg_response_time = statistics.mean(all_response_times)
            min_response_time = min(all_response_times)
            max_response_time = max(all_response_times)
            p95_response_time = sorted(all_response_times)[int(len(all_response_times) * 0.95)] if all_response_times else 0
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = 0
        
        print(f"  Messages sent: {total_sent}")
        print(f"  Messages received: {total_received}")
        print(f"  Success rate: {total_received / total_sent * 100 if total_sent else 0:.2f}%")
        print(f"  Average response time: {avg_response_time:.2f} ms")
        print(f"  Min response time: {min_response_time:.2f} ms")
        print(f"  Max response time: {max_response_time:.2f} ms")
        print(f"  P95 response time: {p95_response_time:.2f} ms")
        
        return {
            "connected_clients": connected_clients,
            "messages_sent": total_sent,
            "messages_received": total_received,
            "success_rate": total_received / total_sent * 100 if total_sent else 0,
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min_response_time,
            "max_response_time_ms": max_response_time,
            "p95_response_time_ms": p95_response_time
        }
    
    async def client_echo_session(self, client, num_messages, delay_ms):
        """Run an echo session for a client."""
        for i in range(num_messages):
            message = f"Message {i} from {client.client_id}"
            if await client.send_message(message):
                response = await client.receive_message()
                if response is None:
                    break
            
            # Add a small delay between messages
            await asyncio.sleep(delay_ms / 1000)
    
    async def run_chat_test(self, num_clients=10, messages_per_client=10, num_rooms=2, delay_ms=100):
        """Test the chat WebSocket endpoint with multiple clients in multiple rooms."""
        print(f"\nRunning chat WebSocket test with {num_clients} clients, {messages_per_client} messages per client, {num_rooms} rooms")
        
        # Create and connect clients
        self.clients = []
        for i in range(num_clients):
            room = f"room-{i % num_rooms}"
            username = f"user-{i}"
            client = WebSocketClient(f"ws://{self.host}:{self.port}/chat/{room}?username={username}", f"chat-{i}")
            if await client.connect():
                self.clients.append(client)
        
        connected_clients = len(self.clients)
        print(f"  Connected clients: {connected_clients}/{num_clients}")
        
        if not connected_clients:
            print("  No clients connected, aborting test")
            return
        
        # Receive welcome messages
        for client in self.clients:
            await client.receive_message()
        
        # Send and receive messages
        tasks = []
        for client in self.clients:
            tasks.append(self.client_chat_session(client, messages_per_client, delay_ms))
        
        await asyncio.gather(*tasks)
        
        # Close connections
        for client in self.clients:
            await client.close()
        
        # Analyze results
        total_sent = sum(client.messages_sent for client in self.clients)
        total_received = sum(client.messages_received for client in self.clients)
        all_response_times = []
        for client in self.clients:
            all_response_times.extend(client.response_times)
        
        if all_response_times:
            avg_response_time = statistics.mean(all_response_times)
            min_response_time = min(all_response_times)
            max_response_time = max(all_response_times)
            p95_response_time = sorted(all_response_times)[int(len(all_response_times) * 0.95)] if all_response_times else 0
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = 0
        
        print(f"  Messages sent: {total_sent}")
        print(f"  Messages received: {total_received}")
        print(f"  Average response time: {avg_response_time:.2f} ms")
        print(f"  Min response time: {min_response_time:.2f} ms")
        print(f"  Max response time: {max_response_time:.2f} ms")
        print(f"  P95 response time: {p95_response_time:.2f} ms")
        
        return {
            "connected_clients": connected_clients,
            "messages_sent": total_sent,
            "messages_received": total_received,
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min_response_time,
            "max_response_time_ms": max_response_time,
            "p95_response_time_ms": p95_response_time
        }
    
    async def client_chat_session(self, client, num_messages, delay_ms):
        """Run a chat session for a client."""
        for i in range(num_messages):
            message = json.dumps({"message": f"Message {i} from {client.client_id}"})
            if await client.send_message(message):
                response = await client.receive_message()
                if response is None:
                    break
            
            # Add a small delay between messages
            await asyncio.sleep(delay_ms / 1000)
    
    async def run_all_tests(self, num_clients=10, messages_per_client=10, num_rooms=2, delay_ms=100):
        """Run all WebSocket load tests."""
        print("Running WebSocket load tests...")
        
        results = {}
        
        # Test echo WebSocket
        results["echo"] = await self.run_echo_test(num_clients, messages_per_client, delay_ms)
        
        # Test chat WebSocket
        results["chat"] = await self.run_chat_test(num_clients, messages_per_client, num_rooms, delay_ms)
        
        print("\nAll tests completed!")
        return results

async def main():
    parser = argparse.ArgumentParser(description="WebSocket Load Test for ProAPI")
    parser.add_argument("--clients", type=int, default=10, help="Number of clients")
    parser.add_argument("--messages", type=int, default=10, help="Number of messages per client")
    parser.add_argument("--rooms", type=int, default=2, help="Number of chat rooms")
    parser.add_argument("--delay", type=int, default=100, help="Delay between messages in ms")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()
    
    print("WebSocket Load Test for ProAPI")
    print("=============================")
    print(f"ProAPI version: {sys.modules['proapi'].__version__}")
    print(f"Clients: {args.clients}")
    print(f"Messages per client: {args.messages}")
    print(f"Chat rooms: {args.rooms}")
    print(f"Delay between messages: {args.delay} ms")
    print()
    
    # Start the server
    server_thread = start_server(port=args.port)
    
    # Run load tests
    load_test = WebSocketLoadTest(port=args.port)
    results = await load_test.run_all_tests(
        num_clients=args.clients,
        messages_per_client=args.messages,
        num_rooms=args.rooms,
        delay_ms=args.delay
    )
    
    # Print summary
    print("\nSummary:")
    for test_name, stats in results.items():
        print(f"{test_name}: {stats['avg_response_time_ms']:.2f} ms avg, {stats.get('success_rate', 'N/A')}% success")

if __name__ == "__main__":
    asyncio.run(main())
