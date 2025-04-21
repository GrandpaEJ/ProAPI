"""
Example ProAPI application.

This is a simple example of how to use the ProAPI framework.
"""

from proapi import ProAPI, render

# Create the application
app = ProAPI(debug=True)

# Define routes

@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Welcome to ProAPI!",
        "description": "A lightweight, beginner-friendly yet powerful Python web framework.",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This endpoint"},
            {"path": "/hello/{name}", "method": "GET", "description": "Get a personalized greeting"},
            {"path": "/json", "method": "POST", "description": "Echo JSON data"},
            {"path": "/html", "method": "GET", "description": "HTML example"}
        ]
    }

@app.get("/hello/{name}")
def hello(name, request):
    """Get a personalized greeting."""
    return {"message": f"Hello, {name}!"}

@app.post("/json")
def json_handler(request):
    """Echo JSON data."""
    return {
        "received": request.json,
        "message": "JSON data received successfully"
    }

@app.get("/html")
def html_example(request):
    """HTML example."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ProAPI Example</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <h1>ProAPI Example</h1>
        <p>This is a simple HTML response from ProAPI.</p>

        <h2>Example Code:</h2>
        <pre>
from proapi import ProAPI

app = ProAPI()

@app.get("/")
def index():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run()
        </pre>
    </body>
    </html>
    """

# Add middleware for logging
@app.use
def logging_middleware(request):
    """Log requests."""
    print(f"Request: {request.method} {request.path}")
    return request

# Run the application
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
