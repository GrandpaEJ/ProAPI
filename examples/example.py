"""
Example ProAPI application demonstrating the new features.

To run this example:
    python example.py

Or using the CLI:
    proapi run example.py --fast --debug

View the API documentation at http://localhost:8000/.docs
"""

from proapi import ProAPI

# Create a ProAPI application with debug mode and fast mode enabled
app = ProAPI(
    debug=True,           # Enable debug mode for detailed error messages
    fast_mode=True,       # Enable fast mode for better performance
    enable_docs=True,     # Enable API documentation (already true by default)
    docs_url="/.docs"     # Set documentation URL (already /.docs by default)
)

# Basic route
@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

# Route with path parameter
@app.get("/hello/{name}")
def hello(name, request):
    return {"message": f"Hello, {name}!"}

# POST route
@app.post("/echo")
def echo(request):
    return {"received": request.json}

# Route with query parameters
@app.get("/search")
def search(request):
    query = request.query_params.get("q", [""])[0]
    return {"query": query, "results": [f"Result for {query}"]}

# Route with error handling
@app.get("/error")
def error(request):
    # This will trigger an error that will be handled by ProAPI
    return 1 / 0

if __name__ == "__main__":
    # Run the application with various options
    app.run(
        port=8000,            # Set port (default: 8000)
        forward=False,        # Enable Cloudflare port forwarding (requires proapi[cloudflare])
        use_reloader=True     # Enable auto-reloading for development
    )
