"""
Benchmark for ProAPI.
"""

import os
import sys
import time
import re
import random
import string
from typing import List, Dict, Any, Callable

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import Cython-optimized functions
try:
    from proapi.cython_ext.core_cy import match_route, extract_params, json_dumps, json_loads
    USING_CYTHON = True
except ImportError:
    # Fall back to pure Python implementations
    USING_CYTHON = False
    
    def match_route(method, path, route_method, pattern):
        return method.upper() == route_method and pattern.match(path) is not None
    
    def extract_params(pattern, path):
        params = {}
        match = pattern.match(path)
        if not match:
            return params
        
        params = match.groupdict()
        
        # Convert parameters to appropriate types
        for param, value in list(params.items()):
            if param.endswith(':int'):
                clean_param = param.rsplit(':', 1)[0]
                params[clean_param] = int(value)
                del params[param]
            elif param.endswith(':float'):
                clean_param = param.rsplit(':', 1)[0]
                params[clean_param] = float(value)
                del params[param]
        
        return params
    
    def json_dumps(data):
        import json
        return json.dumps(data)
    
    def json_loads(data):
        import json
        return json.loads(data)

def benchmark(func: Callable, *args, **kwargs) -> float:
    """
    Benchmark a function.
    
    Args:
        func: Function to benchmark
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Execution time in seconds
    """
    start_time = time.time()
    func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time

def generate_random_string(length: int) -> str:
    """
    Generate a random string.
    
    Args:
        length: Length of the string
        
    Returns:
        Random string
    """
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_random_dict(keys: int, value_length: int) -> Dict[str, str]:
    """
    Generate a random dictionary.
    
    Args:
        keys: Number of keys
        value_length: Length of each value
        
    Returns:
        Random dictionary
    """
    return {
        f"key_{i}": generate_random_string(value_length)
        for i in range(keys)
    }

def benchmark_route_matching() -> Dict[str, float]:
    """
    Benchmark route matching.
    
    Returns:
        Dictionary of benchmark results
    """
    print("Benchmarking route matching...")
    
    # Compile regex patterns
    patterns = [
        re.compile(r'^/$'),
        re.compile(r'^/users/(?P<id>[0-9]+)$'),
        re.compile(r'^/users/(?P<username>[a-zA-Z0-9_-]+)$'),
        re.compile(r'^/products/(?P<id>[0-9]+)/reviews/(?P<review_id>[0-9]+)$'),
        re.compile(r'^/(?P<path>.*)$')
    ]
    
    # Generate test cases
    test_cases = [
        ("GET", "/", "GET", patterns[0]),
        ("POST", "/", "POST", patterns[0]),
        ("GET", "/users/123", "GET", patterns[1]),
        ("GET", "/users/john_doe", "GET", patterns[2]),
        ("GET", "/products/123/reviews/456", "GET", patterns[3]),
        ("GET", "/some/random/path", "GET", patterns[4])
    ]
    
    # Run benchmarks
    iterations = 100000
    total_time = 0
    
    for _ in range(iterations):
        method, path, route_method, pattern = random.choice(test_cases)
        total_time += benchmark(match_route, method, path, route_method, pattern)
    
    avg_time = total_time / iterations
    print(f"Average time per match: {avg_time * 1000000:.2f} µs")
    
    return {"route_matching": avg_time}

def benchmark_param_extraction() -> Dict[str, float]:
    """
    Benchmark parameter extraction.
    
    Returns:
        Dictionary of benchmark results
    """
    print("Benchmarking parameter extraction...")
    
    # Compile regex patterns
    patterns = [
        re.compile(r'^/users/(?P<id>[0-9]+)$'),
        re.compile(r'^/users/(?P<username>[a-zA-Z0-9_-]+)$'),
        re.compile(r'^/products/(?P<id>[0-9]+)/reviews/(?P<review_id>[0-9]+)$'),
        re.compile(r'^/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})$'),
        re.compile(r'^/search/(?P<query>[^/]+)$')
    ]
    
    # Generate test cases
    test_cases = [
        (patterns[0], "/users/123"),
        (patterns[1], "/users/john_doe"),
        (patterns[2], "/products/123/reviews/456"),
        (patterns[3], "/2023/04/21"),
        (patterns[4], "/search/python+web+framework")
    ]
    
    # Run benchmarks
    iterations = 100000
    total_time = 0
    
    for _ in range(iterations):
        pattern, path = random.choice(test_cases)
        total_time += benchmark(extract_params, pattern, path)
    
    avg_time = total_time / iterations
    print(f"Average time per extraction: {avg_time * 1000000:.2f} µs")
    
    return {"param_extraction": avg_time}

def benchmark_json_serialization() -> Dict[str, float]:
    """
    Benchmark JSON serialization.
    
    Returns:
        Dictionary of benchmark results
    """
    print("Benchmarking JSON serialization...")
    
    # Generate test data
    test_data = [
        {"message": "Hello, World!"},
        {"id": 123, "name": "John Doe", "email": "john@example.com"},
        {"users": [{"id": i, "name": f"User {i}"} for i in range(10)]},
        generate_random_dict(100, 20),
        [generate_random_dict(10, 20) for _ in range(10)]
    ]
    
    # Run benchmarks
    iterations = 10000
    total_time = 0
    
    for _ in range(iterations):
        data = random.choice(test_data)
        total_time += benchmark(json_dumps, data)
    
    avg_time = total_time / iterations
    print(f"Average time per serialization: {avg_time * 1000000:.2f} µs")
    
    return {"json_serialization": avg_time}

def benchmark_json_deserialization() -> Dict[str, float]:
    """
    Benchmark JSON deserialization.
    
    Returns:
        Dictionary of benchmark results
    """
    print("Benchmarking JSON deserialization...")
    
    # Generate test data
    test_data = [
        json_dumps({"message": "Hello, World!"}),
        json_dumps({"id": 123, "name": "John Doe", "email": "john@example.com"}),
        json_dumps({"users": [{"id": i, "name": f"User {i}"} for i in range(10)]}),
        json_dumps(generate_random_dict(100, 20)),
        json_dumps([generate_random_dict(10, 20) for _ in range(10)])
    ]
    
    # Run benchmarks
    iterations = 10000
    total_time = 0
    
    for _ in range(iterations):
        data = random.choice(test_data)
        total_time += benchmark(json_loads, data)
    
    avg_time = total_time / iterations
    print(f"Average time per deserialization: {avg_time * 1000000:.2f} µs")
    
    return {"json_deserialization": avg_time}

def main():
    """Run benchmarks."""
    print(f"ProAPI Benchmark")
    print(f"Using Cython: {USING_CYTHON}")
    print()
    
    results = {}
    
    # Run benchmarks
    results.update(benchmark_route_matching())
    print()
    
    results.update(benchmark_param_extraction())
    print()
    
    results.update(benchmark_json_serialization())
    print()
    
    results.update(benchmark_json_deserialization())
    print()
    
    # Print summary
    print("Summary:")
    for name, time in results.items():
        print(f"  {name}: {time * 1000000:.2f} µs")

if __name__ == "__main__":
    main()
