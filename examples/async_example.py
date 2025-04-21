"""
Example of async functionality with ProAPI.
"""

import os
import sys
import asyncio
import time

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create the application
app = ProAPI(debug=True)

# Simulate an async database query
async def fetch_data(delay=1):
    await asyncio.sleep(delay)
    return {
        "timestamp": time.time(),
        "data": "Async data fetched successfully"
    }

# Basic route
@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Async Example",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This endpoint"},
            {"path": "/sync", "method": "GET", "description": "Synchronous endpoint"},
            {"path": "/async", "method": "GET", "description": "Asynchronous endpoint"},
            {"path": "/async/delay/{seconds}", "method": "GET", "description": "Asynchronous endpoint with delay"}
        ]
    }

# Synchronous route
@app.get("/sync")
def sync_route(request):
    """Synchronous endpoint."""
    # Simulate a blocking operation
    start_time = time.time()
    time.sleep(1)
    end_time = time.time()

    return {
        "message": "Synchronous operation completed",
        "duration": end_time - start_time,
        "timestamp": time.time()
    }

# Asynchronous route
@app.get("/async")
async def async_route(request):
    """Asynchronous endpoint."""
    start_time = time.time()
    data = await fetch_data()
    end_time = time.time()

    return {
        "message": "Asynchronous operation completed",
        "duration": end_time - start_time,
        "result": data
    }

# Asynchronous route with parameter
@app.get("/async/delay/{seconds:float}")
async def async_with_delay(seconds, request):
    """Asynchronous endpoint with delay."""
    print(f"Delay parameter: {seconds}")
    try:
        delay = float(seconds)
    except ValueError:
        return {"error": "Invalid delay value. Must be a number."}

    start_time = time.time()
    data = await fetch_data(delay)
    end_time = time.time()

    return {
        "message": f"Asynchronous operation with {delay}s delay completed",
        "requested_delay": delay,
        "actual_duration": end_time - start_time,
        "result": data
    }

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8002)
