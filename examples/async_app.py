"""
Async example application for ProAPI.
"""

import os
import sys
import asyncio
import time

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

app = ProAPI(debug=True)

# Simulate an async database query
async def fetch_data(delay=1):
    await asyncio.sleep(delay)
    return {"timestamp": time.time(), "data": "Async data"}

# Basic async route
@app.get("/async")
async def async_route():
    data = await fetch_data()
    return {"message": "Async route", "result": data}

# Async route with parameter
@app.get("/async/{delay:float}")
async def async_with_delay(delay):
    data = await fetch_data(delay)
    return {"message": f"Async route with {delay}s delay", "result": data}

# Multiple async operations
@app.get("/async/parallel")
async def async_parallel():
    # Run multiple async operations in parallel
    results = await asyncio.gather(
        fetch_data(0.5),
        fetch_data(1.0),
        fetch_data(1.5)
    )
    
    return {
        "message": "Parallel async operations",
        "results": results
    }

# Regular synchronous route for comparison
@app.get("/sync")
def sync_route():
    # Simulate a blocking operation
    time.sleep(1)
    return {"message": "Sync route", "timestamp": time.time()}

if __name__ == "__main__":
    # Run the application
    app.run(host="127.0.0.1", port=8000)
