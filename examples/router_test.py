"""
Router Test for ProAPI

This script tests the basic routing functionality of ProAPI, focusing on GET and POST routes.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import proapi
from proapi import ProAPI
import proapi.asgi_adapter_fix as asgi_fix

# Create a ProAPI application
app = ProAPI(
    debug=True,  # Enable debug mode for better error messages
    fast_mode=True,  # Enable fast mode for better performance
    enable_docs=True  # Enable API documentation
)

# Set the global app variable for uvicorn to import
asgi_fix.set_app(app)

# Basic GET routes
@app.get("/")
def index(request):
    """Root endpoint that returns a welcome message."""
    return {
        "message": "Welcome to ProAPI Router Test",
        "version": proapi.__version__,
        "timestamp": datetime.now().isoformat(),
        "available_routes": [
            {"method": "GET", "path": "/"},
            {"method": "GET", "path": "/hello"},
            {"method": "GET", "path": "/hello/{name}"},
            {"method": "GET", "path": "/query"},
            {"method": "GET", "path": "/headers"},
            {"method": "POST", "path": "/echo"},
            {"method": "POST", "path": "/form"},
            {"method": "GET", "path": "/html"},
            {"method": "GET", "path": "/text"},
            {"method": "GET", "path": "/redirect"},
            {"method": "GET", "path": "/error"}
        ]
    }

@app.get("/hello")
def hello(request):
    """Simple hello endpoint."""
    return {"message": "Hello, World!"}

@app.get("/hello/{name}")
def hello_name(name, request):
    """Hello endpoint with a path parameter."""
    return {"message": f"Hello, {name}!"}

@app.get("/query")
def query_params(request):
    """Endpoint that returns query parameters."""
    return {
        "query_params": request.query_params,
        "example": "Try /query?name=John&age=30"
    }

@app.get("/headers")
def headers(request):
    """Endpoint that returns request headers."""
    return {"headers": request.headers}

# Basic POST routes
@app.post("/echo")
def echo(request):
    """Echo endpoint that returns the request body."""
    try:
        # Print request details for debugging
        print(f"Echo endpoint received request with body: {request.body}")
        print(f"Content-Type: {request.headers.get('content-type')}")

        # Try to parse JSON manually
        import json
        body_str = request.body.decode('utf-8')
        if body_str.strip():
            data = json.loads(body_str)
            print(f"Parsed JSON: {data}")
            return data
        else:
            return {"message": "Received empty body"}
    except Exception as e:
        print(f"Error parsing JSON: {str(e)}")
        return {"error": f"Invalid JSON: {str(e)}"}

@app.post("/form")
def form(request):
    """Endpoint that handles form data."""
    try:
        # Parse form data
        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type:
            # Simple form parsing
            form_data = {}
            body = request.body.decode("utf-8")
            for item in body.split("&"):
                if "=" in item:
                    key, value = item.split("=", 1)
                    form_data[key] = value
            return {"form_data": form_data}
        else:
            return {"error": "Expected application/x-www-form-urlencoded"}
    except Exception as e:
        return {"error": f"Error parsing form data: {str(e)}"}

# Different response types
@app.get("/html")
def html_response(request):
    """Endpoint that returns HTML."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ProAPI HTML Response</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #4CAF50; }
            pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>ProAPI HTML Response</h1>
        <p>This is an HTML response from ProAPI.</p>
        <h2>Available Routes:</h2>
        <pre>
GET  /
GET  /hello
GET  /hello/{name}
GET  /query
GET  /headers
POST /echo
POST /form
GET  /html
GET  /text
GET  /redirect
GET  /error
        </pre>
    </body>
    </html>
    """
    from proapi.server import Response
    return Response(body=html, content_type="text/html")

@app.get("/text")
def text_response(request):
    """Endpoint that returns plain text."""
    from proapi.server import Response
    return Response(body="This is a plain text response from ProAPI.", content_type="text/plain")

# Redirect and error responses
@app.get("/redirect")
def redirect_response(request):
    """Endpoint that redirects to the root endpoint."""
    from proapi.utils import redirect
    return redirect("/")

@app.get("/error")
def error_response(request):
    """Endpoint that returns an error response."""
    from proapi.server import Response
    return Response(body={"error": "This is an error response"}, status=500, content_type="application/json")

if __name__ == "__main__":
    print("Router Test for ProAPI")
    print("=====================")
    print(f"ProAPI version: {proapi.__version__}")
    print()
    print("Available endpoints:")
    print("  - GET  /")
    print("  - GET  /hello")
    print("  - GET  /hello/{name}")
    print("  - GET  /query")
    print("  - GET  /headers")
    print("  - POST /echo")
    print("  - POST /form")
    print("  - GET  /html")
    print("  - GET  /text")
    print("  - GET  /redirect")
    print("  - GET  /error")
    print()
    print("Open http://localhost:8000/ in your browser to test the endpoints")
    print("API documentation is available at http://localhost:8000/.docs")
    print()

    # Run the application with uvicorn directly
    import uvicorn
    uvicorn.run("proapi.asgi_adapter_fix:app", host="127.0.0.1", port=8000, reload=True)
