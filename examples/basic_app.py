"""
Basic example application for ProAPI.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, render

app = ProAPI(debug=True)

# Basic route
@app.get("/")
def index():
    return {"message": "Welcome to ProAPI!"}

# Route with path parameter
@app.get("/hello/{name}")
def hello(name):
    return {"message": f"Hello, {name}!"}

# Route with typed path parameter
@app.get("/users/{user_id:int}")
def get_user(user_id):
    # user_id will be converted to an integer
    return {"user_id": user_id, "name": f"User {user_id}"}

# POST route with JSON body
@app.post("/echo")
def echo(request):
    return request.json

# Route with template rendering
@app.get("/html")
def html_example():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ProAPI Example</title>
    </head>
    <body>
        <h1>ProAPI Example</h1>
        <p>This is a simple HTML response.</p>
    </body>
    </html>
    """

# Add middleware
@app.use
def logging_middleware(request):
    print(f"Request: {request.method} {request.path}")
    return request

if __name__ == "__main__":
    # Run the application
    app.run(host="127.0.0.1", port=8000)
