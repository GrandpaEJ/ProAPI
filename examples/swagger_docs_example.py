"""
Example of Swagger UI API documentation with ProAPI.
"""

import os
import sys
import time
from datetime import datetime

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create the application with documentation enabled
app = ProAPI(
    debug=True,
    enable_docs=True,
    docs_url="/docs",
    docs_title="ProAPI Swagger Documentation Example"
)

# Define routes with detailed docstrings

@app.get("/")
def index(request):
    """
    Home page.
    
    Returns a welcome message and a list of available endpoints.
    """
    return {
        "message": "Welcome to the ProAPI Swagger documentation example!",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This endpoint"},
            {"path": "/users", "method": "GET", "description": "Get all users"},
            {"path": "/users/{id}", "method": "GET", "description": "Get a user by ID"},
            {"path": "/users", "method": "POST", "description": "Create a new user"},
            {"path": "/users/{id}", "method": "PUT", "description": "Update a user"},
            {"path": "/users/{id}", "method": "DELETE", "description": "Delete a user"},
            {"path": "/products", "method": "GET", "description": "Get all products"},
            {"path": "/products/{id}", "method": "GET", "description": "Get a product by ID"}
        ]
    }

# User routes

@app.get("/users")
def get_users(request):
    """
    Get all users.
    
    Returns a list of all users in the system.
    """
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
    ]
    return {"users": users}

@app.get("/users/{id:int}")
def get_user(id, request):
    """
    Get a user by ID.
    
    Returns a single user with the specified ID.
    """
    # Simulate database lookup
    users = {
        1: {"id": 1, "name": "John Doe", "email": "john@example.com"},
        2: {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        3: {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
    }
    
    if id not in users:
        return {"error": "User not found"}, 404
    
    return {"user": users[id]}

@app.post("/users")
def create_user(request):
    """
    Create a new user.
    
    Creates a new user with the provided information.
    
    Request body should contain:
    - name: User's full name
    - email: User's email address
    """
    data = request.json
    
    # Validate request data
    if not data:
        return {"error": "No data provided"}, 400
    
    required_fields = ["name", "email"]
    for field in required_fields:
        if field not in data:
            return {"error": f"Missing required field: {field}"}, 400
    
    # Simulate user creation
    new_user = {
        "id": 4,  # In a real app, this would be generated
        "name": data["name"],
        "email": data["email"],
        "created_at": datetime.now().isoformat()
    }
    
    return {"user": new_user, "message": "User created successfully"}, 201

@app.put("/users/{id:int}")
def update_user(id, request):
    """
    Update a user.
    
    Updates an existing user with the provided information.
    
    Request body should contain one or more of:
    - name: User's full name
    - email: User's email address
    """
    data = request.json
    
    # Validate request data
    if not data:
        return {"error": "No data provided"}, 400
    
    # Simulate database lookup
    users = {
        1: {"id": 1, "name": "John Doe", "email": "john@example.com"},
        2: {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        3: {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
    }
    
    if id not in users:
        return {"error": "User not found"}, 404
    
    # Update user
    user = users[id]
    for key, value in data.items():
        if key in ["name", "email"]:
            user[key] = value
    
    return {"user": user, "message": "User updated successfully"}

@app.delete("/users/{id:int}")
def delete_user(id, request):
    """
    Delete a user.
    
    Deletes the user with the specified ID.
    """
    # Simulate database lookup
    users = {
        1: {"id": 1, "name": "John Doe", "email": "john@example.com"},
        2: {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        3: {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
    }
    
    if id not in users:
        return {"error": "User not found"}, 404
    
    # Simulate user deletion
    deleted_user = users[id]
    
    return {"message": f"User {deleted_user['name']} deleted successfully"}

# Product routes

@app.get("/products")
def get_products(request):
    """
    Get all products.
    
    Returns a list of all products in the system.
    """
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
        {"id": 2, "name": "Smartphone", "price": 699.99, "category": "Electronics"},
        {"id": 3, "name": "Headphones", "price": 149.99, "category": "Audio"}
    ]
    return {"products": products}

@app.get("/products/{id:int}")
def get_product(id, request):
    """
    Get a product by ID.
    
    Returns a single product with the specified ID.
    """
    # Simulate database lookup
    products = {
        1: {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
        2: {"id": 2, "name": "Smartphone", "price": 699.99, "category": "Electronics"},
        3: {"id": 3, "name": "Headphones", "price": 149.99, "category": "Audio"}
    }
    
    if id not in products:
        return {"error": "Product not found"}, 404
    
    return {"product": products[id]}

# Server info
@app.get("/info")
def api_info(request):
    """
    Get server information.
    
    Returns information about the server and the ProAPI framework.
    """
    import platform
    
    return {
        "framework": "ProAPI",
        "version": "0.1.0",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "host": request.headers.get("Host", "unknown"),
        "remote_addr": request.remote_addr,
        "documentation": f"http://{request.headers.get('Host', 'localhost')}/docs"
    }

if __name__ == "__main__":
    print("Swagger UI Documentation Example")
    print()
    print("Web Interface: http://127.0.0.1:8005")
    print("API Documentation: http://127.0.0.1:8005/docs")
    print()
    
    # Run the application
    app.run(host="127.0.0.1", port=8005)
