"""
Load Test for ProAPI

This script tests how ProAPI handles multiple concurrent requests.
It starts a ProAPI server and then uses asyncio to send multiple concurrent requests.
"""

import os
import sys
import time
import json
import asyncio
import statistics
import argparse
from datetime import datetime
import concurrent.futures
import threading
import requests
from urllib.parse import urljoin

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create a ProAPI application
app = ProAPI(
    debug=False,  # Disable debug mode for better performance
    fast_mode=True,  # Enable fast mode for better performance
    enable_docs=True
)

# Simple JSON response
@app.get("/json")
def json_endpoint(request):
    return {"message": "Hello, World!", "timestamp": datetime.now().isoformat()}

# Echo endpoint that returns the request body
@app.post("/echo")
def echo_endpoint(request):
    return request.json

# Parameterized endpoint
@app.get("/params/{param}")
def params_endpoint(param, request):
    return {"param": param, "query": request.query_params}

# Simulated delay endpoint
@app.get("/delay/{seconds}")
def delay_endpoint(seconds, request):
    # Convert seconds to float
    seconds = float(seconds)

    # Simulate a delay (e.g., database query or external API call)
    time.sleep(min(seconds, 2.0))  # Limit to 2 seconds max
    return {"message": f"Delayed response for {seconds} seconds"}

# CPU-intensive endpoint
@app.get("/compute/{n}")
def compute_endpoint(n, request):
    # Convert n to int
    n = int(n)

    # Compute Fibonacci sequence (inefficient algorithm for testing CPU load)
    def fib(n):
        if n <= 1:
            return n
        return fib(n-1) + fib(n-2)

    result = fib(min(n, 25))  # Limit to avoid excessive computation
    return {"result": result, "n": n}

# Start the server in a separate thread
def start_server(host="127.0.0.1", port=8000):
    import threading
    import uvicorn

    def run_server():
        import proapi.asgi_adapter_fix as asgi_fix
        asgi_fix.set_app(app)
        uvicorn.run("proapi.asgi_adapter_fix:app", host=host, port=port)

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait for the server to start
    time.sleep(2)
    return server_thread

# Load test client
class LoadTest:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    async def send_request(self, method, path, body=None):
        """Send a request and measure response time."""
        url = urljoin(self.base_url, path)

        loop = asyncio.get_event_loop()
        start = time.time()

        try:
            if method.upper() == "GET":
                response = await loop.run_in_executor(
                    None, lambda: self.session.get(url)
                )
            elif method.upper() == "POST":
                response = await loop.run_in_executor(
                    None, lambda: self.session.post(url, json=body)
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            end = time.time()
            return {
                "status": response.status_code,
                "time_ms": (end - start) * 1000,  # Convert to milliseconds
                "response": response.json() if response.headers.get("content-type") == "application/json" else None
            }
        except Exception as e:
            end = time.time()
            return {
                "status": -1,
                "time_ms": (end - start) * 1000,
                "error": str(e)
            }

    async def run_concurrent_requests(self, method, path, body=None, num_requests=100, concurrency=10):
        """Run multiple concurrent requests."""
        tasks = []
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_request():
            async with semaphore:
                return await self.send_request(method, path, body)

        for _ in range(num_requests):
            tasks.append(bounded_request())

        results = await asyncio.gather(*tasks)
        return results

    def analyze_results(self, results):
        """Analyze the results of the load test."""
        times = [r["time_ms"] for r in results if r["status"] == 200]
        errors = [r for r in results if r["status"] != 200]

        if not times:
            return {
                "success_rate": 0,
                "error_count": len(errors),
                "avg_ms": 0,
                "min_ms": 0,
                "max_ms": 0,
                "median_ms": 0,
                "p95_ms": 0,
                "p99_ms": 0
            }

        return {
            "success_rate": len(times) / len(results) * 100,
            "error_count": len(errors),
            "avg_ms": statistics.mean(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "median_ms": statistics.median(times),
            "p95_ms": sorted(times)[int(len(times) * 0.95)] if times else 0,
            "p99_ms": sorted(times)[int(len(times) * 0.99)] if times else 0
        }

    async def run_test(self, method, path, body=None, num_requests=100, concurrency=10):
        """Run a load test for a specific endpoint."""
        print(f"\nTesting {method} {path} with {num_requests} requests, {concurrency} concurrent")

        results = await self.run_concurrent_requests(method, path, body, num_requests, concurrency)
        stats = self.analyze_results(results)

        print(f"  Success rate: {stats['success_rate']:.2f}%")
        print(f"  Error count: {stats['error_count']}")
        print(f"  Average: {stats['avg_ms']:.2f} ms")
        print(f"  Min: {stats['min_ms']:.2f} ms")
        print(f"  Max: {stats['max_ms']:.2f} ms")
        print(f"  Median: {stats['median_ms']:.2f} ms")
        print(f"  P95: {stats['p95_ms']:.2f} ms")
        print(f"  P99: {stats['p99_ms']:.2f} ms")

        return stats

    async def run_all_tests(self, num_requests=100, concurrency=10):
        """Run all load tests."""
        print("Running load tests...")

        results = {}

        # Test JSON endpoint
        results["GET /json"] = await self.run_test("GET", "/json", num_requests=num_requests, concurrency=concurrency)

        # Test echo endpoint
        results["POST /echo"] = await self.run_test("POST", "/echo", body={"message": "Hello, World!"}, num_requests=num_requests, concurrency=concurrency)

        # Test parameterized endpoint
        results["GET /params/test"] = await self.run_test("GET", "/params/test", num_requests=num_requests, concurrency=concurrency)

        # Test delay endpoint
        results["GET /delay/0.1"] = await self.run_test("GET", "/delay/0.1", num_requests=num_requests, concurrency=concurrency)

        # Test CPU-intensive endpoint
        results["GET /compute/20"] = await self.run_test("GET", "/compute/20", num_requests=20, concurrency=5)

        print("\nAll tests completed!")
        return results

async def main():
    parser = argparse.ArgumentParser(description="Load Test for ProAPI")
    parser.add_argument("--requests", type=int, default=100, help="Number of requests to send")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent requests")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()

    print("Load Test for ProAPI")
    print("===================")
    print(f"ProAPI version: {sys.modules['proapi'].__version__}")
    print(f"Requests: {args.requests}")
    print(f"Concurrency: {args.concurrency}")
    print()

    # Start the server
    server_thread = start_server(port=args.port)

    # Run load tests
    load_test = LoadTest(base_url=f"http://127.0.0.1:{args.port}")
    results = await load_test.run_all_tests(num_requests=args.requests, concurrency=args.concurrency)

    # Print summary
    print("\nSummary:")
    for endpoint, stats in results.items():
        print(f"{endpoint}: {stats['avg_ms']:.2f} ms avg, {stats['p95_ms']:.2f} ms p95, {stats['success_rate']:.2f}% success")

if __name__ == "__main__":
    asyncio.run(main())
