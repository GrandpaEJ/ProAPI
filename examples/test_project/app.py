"""
Test Project - A simple blog application built with ProAPI.
"""

import os
import sys
import json
import time
from datetime import datetime

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, render

# Create the application
app = ProAPI(
    debug=True,
    template_dir=os.path.join(os.path.dirname(__file__), "templates"),
    static_dir=os.path.join(os.path.dirname(__file__), "static"),
    enable_docs=True,  # Enable API documentation
    docs_url="/api/docs"  # API documentation URL
)

# In-memory database for posts
# In a real application, you would use a database like SQLite, PostgreSQL, etc.
POSTS = [
    {
        "id": 1,
        "title": "Welcome to ProAPI",
        "content": "This is a test project built with ProAPI, a lightweight Python web framework.",
        "author": "Admin",
        "created_at": datetime.now().isoformat(),
        "tags": ["proapi", "python", "web"]
    },
    {
        "id": 2,
        "title": "Features of ProAPI",
        "content": """
ProAPI is a lightweight, beginner-friendly yet powerful Python web framework.

Features:
- Decorator-based routing
- Template rendering with Jinja2
- Easy server startup
- Optional async support
- Optional Cython compilation
- Minimal dependencies
- Built-in JSON support
- Middleware system
- Automatic API documentation
- Port forwarding to expose apps to the internet
        """,
        "author": "Admin",
        "created_at": (datetime.now().replace(hour=10, minute=30)).isoformat(),
        "tags": ["features", "documentation"]
    }
]

# Simple authentication middleware
@app.use
def auth_middleware(request):
    """
    Simple authentication middleware.
    
    Checks for an API key in the headers and sets request.user if valid.
    """
    from proapi.server import Response
    
    # Get API key from headers
    api_key = request.headers.get('X-API-Key')
    
    # Skip auth for non-admin routes
    if not request.path.startswith('/admin') and not request.path.startswith('/api/admin'):
        return request
    
    # Check if API key is valid
    if api_key != "test-api-key":
        if request.path.startswith('/api/'):
            # Return JSON error for API routes
            return Response(
                status=401,
                body=json.dumps({"error": "Unauthorized. Invalid or missing API key."}),
                content_type="application/json"
            )
        else:
            # Redirect to login page for web routes
            return Response(
                status=302,
                headers={"Location": "/login"},
                body="Redirecting to login page..."
            )
    
    # Set user on request
    request.user = {"username": "admin"}
    return request

# Logging middleware
@app.use
def logging_middleware(request):
    """Log request details."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.path}")
    request.start_time = time.time()
    return request

# Web Routes

@app.get("/")
def index(request):
    """Home page with a list of posts."""
    return render("index.html", 
                 title="Blog Home",
                 posts=POSTS)

@app.get("/posts/{post_id:int}")
def post_detail(post_id, request):
    """Individual post page."""
    # Find the post
    post = next((p for p in POSTS if p["id"] == post_id), None)
    
    if not post:
        return render("error.html", 
                     title="Post Not Found",
                     message=f"Post with ID {post_id} not found.")
    
    return render("post.html", 
                 title=post["title"],
                 post=post)

@app.get("/about")
def about(request):
    """About page."""
    return render("about.html", 
                 title="About",
                 framework="ProAPI",
                 version="0.1.0")

@app.get("/login")
def login_page(request):
    """Login page."""
    return render("login.html", 
                 title="Login")

@app.post("/login")
def login_submit(request):
    """Process login form."""
    username = request.form.get("username")
    password = request.form.get("password")
    
    # Simple authentication (in a real app, you would check against a database)
    if username == "admin" and password == "password":
        return render("login_success.html", 
                     title="Login Successful",
                     username=username)
    else:
        return render("login.html", 
                     title="Login",
                     error="Invalid username or password")

@app.get("/admin")
def admin_page(request):
    """Admin page for managing posts."""
    return render("admin.html", 
                 title="Admin",
                 username=request.user["username"],
                 posts=POSTS)

@app.get("/admin/new")
def new_post_page(request):
    """Page for creating a new post."""
    return render("new_post.html", 
                 title="New Post",
                 username=request.user["username"])

# API Routes

@app.get("/api/posts")
def api_posts(request):
    """Get all posts."""
    return {"posts": POSTS}

@app.get("/api/posts/{post_id:int}")
def api_post(post_id, request):
    """Get a specific post."""
    post = next((p for p in POSTS if p["id"] == post_id), None)
    
    if not post:
        return {"error": "Post not found"}, 404
    
    return {"post": post}

@app.post("/api/admin/posts")
def api_create_post(request):
    """Create a new post."""
    data = request.json
    
    # Validate data
    if not data:
        return {"error": "No data provided"}, 400
    
    required_fields = ["title", "content", "author"]
    for field in required_fields:
        if field not in data:
            return {"error": f"Missing required field: {field}"}, 400
    
    # Create new post
    new_post = {
        "id": max(p["id"] for p in POSTS) + 1 if POSTS else 1,
        "title": data["title"],
        "content": data["content"],
        "author": data["author"],
        "created_at": datetime.now().isoformat(),
        "tags": data.get("tags", [])
    }
    
    # Add to database
    POSTS.append(new_post)
    
    return {"post": new_post, "message": "Post created successfully"}, 201

@app.put("/api/admin/posts/{post_id:int}")
def api_update_post(post_id, request):
    """Update a post."""
    data = request.json
    
    # Validate data
    if not data:
        return {"error": "No data provided"}, 400
    
    # Find the post
    post_index = next((i for i, p in enumerate(POSTS) if p["id"] == post_id), None)
    
    if post_index is None:
        return {"error": "Post not found"}, 404
    
    # Update post
    post = POSTS[post_index]
    
    for key, value in data.items():
        if key != "id" and key != "created_at":  # Don't allow changing id or created_at
            post[key] = value
    
    return {"post": post, "message": "Post updated successfully"}

@app.delete("/api/admin/posts/{post_id:int}")
def api_delete_post(post_id, request):
    """Delete a post."""
    # Find the post
    post_index = next((i for i, p in enumerate(POSTS) if p["id"] == post_id), None)
    
    if post_index is None:
        return {"error": "Post not found"}, 404
    
    # Delete post
    deleted_post = POSTS.pop(post_index)
    
    return {"message": f"Post '{deleted_post['title']}' deleted successfully"}

# Server info
@app.get("/api/info")
def api_info(request):
    """Get server information."""
    import platform
    
    return {
        "framework": "ProAPI",
        "version": "0.1.0",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "host": request.headers.get("Host", "unknown"),
        "remote_addr": request.remote_addr
    }

if __name__ == "__main__":
    print("Test Project - A simple blog application built with ProAPI")
    print()
    print("Web Interface: http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/api/docs")
    print()
    print("Admin Access:")
    print("  Username: admin")
    print("  Password: password")
    print("  API Key: test-api-key")
    print()
    print("To expose the app to the internet, run:")
    print("  python -m proapi run test_project/app.py --forward")
    print()
    
    # Run the application
    app.run(host="127.0.0.1", port=8000)
