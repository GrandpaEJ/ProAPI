"""
High Load Test for ProAPI

This script tests how ProAPI handles high load with up to 500 concurrent users.
It measures the Requests Per Second (RPS) at different concurrency levels.
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
import matplotlib.pyplot as plt
import numpy as np

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
    time.sleep(min(seconds, 0.1))  # Limit to 0.1 seconds max for high load testing
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
    
    result = fib(min(n, 15))  # Limit to avoid excessive computation
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

# High load test client
class HighLoadTest:
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
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Calculate RPS
        total_time = end_time - start_time
        rps = num_requests / total_time if total_time > 0 else 0
        
        return results, rps
    
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
        
        results, rps = await self.run_concurrent_requests(method, path, body, num_requests, concurrency)
        stats = self.analyze_results(results)
        
        print(f"  Success rate: {stats['success_rate']:.2f}%")
        print(f"  Error count: {stats['error_count']}")
        print(f"  Average: {stats['avg_ms']:.2f} ms")
        print(f"  Min: {stats['min_ms']:.2f} ms")
        print(f"  Max: {stats['max_ms']:.2f} ms")
        print(f"  Median: {stats['median_ms']:.2f} ms")
        print(f"  P95: {stats['p95_ms']:.2f} ms")
        print(f"  P99: {stats['p99_ms']:.2f} ms")
        print(f"  RPS: {rps:.2f} requests/second")
        
        return stats, rps
    
    async def run_rps_test(self, method, path, body=None, num_requests=100, concurrency_levels=None):
        """Run a test with different concurrency levels to measure RPS."""
        if concurrency_levels is None:
            concurrency_levels = [1, 5, 10, 25, 50, 100, 200, 300, 400, 500]
        
        results = []
        
        for concurrency in concurrency_levels:
            # Adjust number of requests based on concurrency
            adjusted_requests = min(num_requests, concurrency * 10)
            
            print(f"\nTesting {method} {path} with {adjusted_requests} requests, {concurrency} concurrent")
            
            try:
                test_results, rps = await self.run_concurrent_requests(method, path, body, adjusted_requests, concurrency)
                stats = self.analyze_results(test_results)
                
                print(f"  Success rate: {stats['success_rate']:.2f}%")
                print(f"  Average: {stats['avg_ms']:.2f} ms")
                print(f"  RPS: {rps:.2f} requests/second")
                
                results.append({
                    "concurrency": concurrency,
                    "rps": rps,
                    "success_rate": stats['success_rate'],
                    "avg_ms": stats['avg_ms'],
                    "p95_ms": stats['p95_ms']
                })
            except Exception as e:
                print(f"  Error at concurrency {concurrency}: {e}")
                results.append({
                    "concurrency": concurrency,
                    "rps": 0,
                    "success_rate": 0,
                    "avg_ms": 0,
                    "p95_ms": 0
                })
        
        return results
    
    def plot_rps_results(self, results, title="RPS vs Concurrency"):
        """Plot the RPS results."""
        try:
            concurrency = [r["concurrency"] for r in results]
            rps = [r["rps"] for r in results]
            success_rate = [r["success_rate"] for r in results]
            
            fig, ax1 = plt.subplots(figsize=(10, 6))
            
            color = 'tab:blue'
            ax1.set_xlabel('Concurrency')
            ax1.set_ylabel('RPS', color=color)
            ax1.plot(concurrency, rps, 'o-', color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            
            ax2 = ax1.twinx()
            color = 'tab:red'
            ax2.set_ylabel('Success Rate (%)', color=color)
            ax2.plot(concurrency, success_rate, 'o-', color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            
            fig.tight_layout()
            plt.title(title)
            plt.savefig(f"{title.replace(' ', '_').lower()}.png")
            print(f"Plot saved as {title.replace(' ', '_').lower()}.png")
        except Exception as e:
            print(f"Error plotting results: {e}")
    
    async def run_all_rps_tests(self, num_requests=1000, concurrency_levels=None):
        """Run RPS tests for all endpoints."""
        if concurrency_levels is None:
            concurrency_levels = [1, 5, 10, 25, 50, 100, 200, 300, 400, 500]
        
        print("Running RPS tests...")
        
        # Test JSON endpoint
        json_results = await self.run_rps_test("GET", "/json", num_requests=num_requests, concurrency_levels=concurrency_levels)
        self.plot_rps_results(json_results, "JSON Endpoint RPS vs Concurrency")
        
        # Test echo endpoint
        echo_results = await self.run_rps_test("POST", "/echo", body={"message": "Hello, World!"}, num_requests=num_requests, concurrency_levels=concurrency_levels)
        self.plot_rps_results(echo_results, "Echo Endpoint RPS vs Concurrency")
        
        # Test parameterized endpoint
        params_results = await self.run_rps_test("GET", "/params/test", num_requests=num_requests, concurrency_levels=concurrency_levels)
        self.plot_rps_results(params_results, "Params Endpoint RPS vs Concurrency")
        
        # Test delay endpoint with small delay
        delay_results = await self.run_rps_test("GET", "/delay/0.01", num_requests=num_requests, concurrency_levels=concurrency_levels)
        self.plot_rps_results(delay_results, "Delay Endpoint RPS vs Concurrency")
        
        # Test compute endpoint with small computation
        compute_results = await self.run_rps_test("GET", "/compute/10", num_requests=min(num_requests, 500), concurrency_levels=concurrency_levels[:6])  # Limit for compute endpoint
        self.plot_rps_results(compute_results, "Compute Endpoint RPS vs Concurrency")
        
        print("\nAll RPS tests completed!")
        
        # Return all results
        return {
            "json": json_results,
            "echo": echo_results,
            "params": params_results,
            "delay": delay_results,
            "compute": compute_results
        }

async def main():
    parser = argparse.ArgumentParser(description="High Load Test for ProAPI")
    parser.add_argument("--requests", type=int, default=1000, help="Maximum number of requests to send")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--max-concurrency", type=int, default=500, help="Maximum concurrency level")
    args = parser.parse_args()
    
    # Generate concurrency levels
    if args.max_concurrency <= 10:
        concurrency_levels = list(range(1, args.max_concurrency + 1))
    else:
        # Generate logarithmic concurrency levels
        concurrency_levels = [1, 5, 10, 25, 50, 100]
        if args.max_concurrency > 100:
            concurrency_levels.extend([200, 300, 400, 500][:int((args.max_concurrency - 100) / 100) + 1])
    
    print("High Load Test for ProAPI")
    print("========================")
    print(f"ProAPI version: {sys.modules['proapi'].__version__}")
    print(f"Maximum requests: {args.requests}")
    print(f"Concurrency levels: {concurrency_levels}")
    print()
    
    # Start the server
    server_thread = start_server(port=args.port)
    
    # Run load tests
    load_test = HighLoadTest(base_url=f"http://127.0.0.1:{args.port}")
    results = await load_test.run_all_rps_tests(num_requests=args.requests, concurrency_levels=concurrency_levels)
    
    # Print summary
    print("\nSummary:")
    for endpoint, endpoint_results in results.items():
        max_rps = max([r["rps"] for r in endpoint_results])
        max_concurrency = endpoint_results[[r["rps"] for r in endpoint_results].index(max_rps)]["concurrency"]
        print(f"{endpoint}: Max RPS: {max_rps:.2f} at concurrency {max_concurrency}")

if __name__ == "__main__":
    asyncio.run(main())
