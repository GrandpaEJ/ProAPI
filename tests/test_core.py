"""
Tests for ProAPI core functionality.
"""

import json
import os
import sys
import unittest

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI
from proapi.server import Request, Response

class TestProAPI(unittest.TestCase):
    """Test ProAPI core functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = ProAPI(debug=True)
        
        @self.app.get("/")
        def index():
            return {"message": "Hello, World!"}
        
        @self.app.get("/hello/{name}")
        def hello(name):
            return {"message": f"Hello, {name}!"}
        
        @self.app.post("/echo")
        def echo(request):
            return request.json
    
    def test_route_registration(self):
        """Test route registration."""
        self.assertEqual(len(self.app.routes), 3)
        
        # Check route methods
        methods = [route.method for route in self.app.routes]
        self.assertEqual(methods.count("GET"), 2)
        self.assertEqual(methods.count("POST"), 1)
        
        # Check route paths
        paths = [route.path for route in self.app.routes]
        self.assertIn("/", paths)
        self.assertIn("/hello/{name}", paths)
        self.assertIn("/echo", paths)
    
    def test_route_matching(self):
        """Test route matching."""
        # Find index route
        route = self.app._find_route("GET", "/")
        self.assertIsNotNone(route)
        self.assertEqual(route.path, "/")
        
        # Find hello route
        route = self.app._find_route("GET", "/hello/john")
        self.assertIsNotNone(route)
        self.assertEqual(route.path, "/hello/{name}")
        
        # Find echo route
        route = self.app._find_route("POST", "/echo")
        self.assertIsNotNone(route)
        self.assertEqual(route.path, "/echo")
        
        # Non-existent route
        route = self.app._find_route("GET", "/nonexistent")
        self.assertIsNone(route)
    
    def test_path_parameter_extraction(self):
        """Test path parameter extraction."""
        route = self.app._find_route("GET", "/hello/john")
        params = route.extract_params("/hello/john")
        self.assertEqual(params, {"name": "john"})
    
    def test_request_handling(self):
        """Test request handling."""
        # GET request
        request = Request(
            method="GET",
            path="/",
            headers={},
            query_params={},
            body=b''
        )
        
        response = self.app.handle_request(request)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(json.loads(response.body), {"message": "Hello, World!"})
        
        # GET request with path parameter
        request = Request(
            method="GET",
            path="/hello/john",
            headers={},
            query_params={},
            body=b''
        )
        
        response = self.app.handle_request(request)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(json.loads(response.body), {"message": "Hello, john!"})
        
        # POST request with JSON body
        request = Request(
            method="POST",
            path="/echo",
            headers={"Content-Type": "application/json"},
            query_params={},
            body=json.dumps({"key": "value"}).encode()
        )
        
        response = self.app.handle_request(request)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(json.loads(response.body), {"key": "value"})
        
        # Non-existent route
        request = Request(
            method="GET",
            path="/nonexistent",
            headers={},
            query_params={},
            body=b''
        )
        
        response = self.app.handle_request(request)
        self.assertEqual(response.status, 404)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(json.loads(response.body), {"error": "Not Found"})

if __name__ == "__main__":
    unittest.main()
