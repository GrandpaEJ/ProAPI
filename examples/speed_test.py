"""
Speed Test for ProAPI

This script tests the performance of ProAPI by measuring request processing time.
"""

import os
import sys
import time
import json
import statistics
from datetime import datetime

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

    result = fib(min(n, 20))  # Limit to avoid excessive computation
    return {"result": result, "n": n}

# Test client to measure performance
class SpeedTest:
    def __init__(self, app):
        self.app = app
        self.results = {}

    def test_endpoint(self, method, path, body=None, iterations=100):
        """Test an endpoint and measure response time."""
        from proapi.server import Request

        # Create a request
        request = Request(
            method=method,
            path=path,
            headers={"Content-Type": "application/json"},
            query_params={},
            body=json.dumps(body).encode() if body else b"",
            remote_addr="127.0.0.1"
        )

        # Warm up
        for _ in range(10):
            self.app.handle_request(request)

        # Measure response time
        times = []
        for _ in range(iterations):
            start = time.time()
            response = self.app.handle_request(request)
            end = time.time()
            times.append((end - start) * 1000)  # Convert to milliseconds

        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        p95_time = sorted(times)[int(iterations * 0.95)]

        # Store results
        self.results[f"{method} {path}"] = {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "median_ms": median_time,
            "p95_ms": p95_time,
            "iterations": iterations
        }

        return {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "median_ms": median_time,
            "p95_ms": p95_time,
            "iterations": iterations
        }

    def run_all_tests(self):
        """Run all tests."""
        print("Running speed tests...")

        # Test JSON endpoint
        print("\nTesting GET /json")
        result = self.test_endpoint("GET", "/json")
        print(f"  Average: {result['avg_ms']:.2f} ms")
        print(f"  Min: {result['min_ms']:.2f} ms")
        print(f"  Max: {result['max_ms']:.2f} ms")
        print(f"  Median: {result['median_ms']:.2f} ms")
        print(f"  P95: {result['p95_ms']:.2f} ms")

        # Test echo endpoint
        print("\nTesting POST /echo")
        result = self.test_endpoint("POST", "/echo", body={"message": "Hello, World!"})
        print(f"  Average: {result['avg_ms']:.2f} ms")
        print(f"  Min: {result['min_ms']:.2f} ms")
        print(f"  Max: {result['max_ms']:.2f} ms")
        print(f"  Median: {result['median_ms']:.2f} ms")
        print(f"  P95: {result['p95_ms']:.2f} ms")

        # Test parameterized endpoint
        print("\nTesting GET /params/test")
        result = self.test_endpoint("GET", "/params/test")
        print(f"  Average: {result['avg_ms']:.2f} ms")
        print(f"  Min: {result['min_ms']:.2f} ms")
        print(f"  Max: {result['max_ms']:.2f} ms")
        print(f"  Median: {result['median_ms']:.2f} ms")
        print(f"  P95: {result['p95_ms']:.2f} ms")

        # Test CPU-intensive endpoint
        print("\nTesting GET /compute/20")
        result = self.test_endpoint("GET", "/compute/20", iterations=10)
        print(f"  Average: {result['avg_ms']:.2f} ms")
        print(f"  Min: {result['min_ms']:.2f} ms")
        print(f"  Max: {result['max_ms']:.2f} ms")
        print(f"  Median: {result['median_ms']:.2f} ms")
        print(f"  P95: {result['p95_ms']:.2f} ms")

        print("\nAll tests completed!")
        return self.results

if __name__ == "__main__":
    print("Speed Test for ProAPI")
    print("=====================")
    print(f"ProAPI version: {sys.modules['proapi'].__version__}")
    print(f"Fast mode: {app._fast_mode}")
    print(f"Debug mode: {app.debug}")
    print()

    # Run speed tests
    speed_test = SpeedTest(app)
    results = speed_test.run_all_tests()

    # Print summary
    print("\nSummary:")
    for endpoint, stats in results.items():
        print(f"{endpoint}: {stats['avg_ms']:.2f} ms avg, {stats['p95_ms']:.2f} ms p95")
