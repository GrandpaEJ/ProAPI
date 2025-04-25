"""
Login Example for ProAPI (Final Version)

This example demonstrates how to use the login functionality in ProAPI.
It includes:
- User authentication
- Protected routes
- Login and logout functionality
- User management
- Event loop protection
- ASGI adapter fixes

To run this example:
    python login_example_final.py

Then visit http://localhost:8000/ in your browser.
"""

import os
import sys
import json
import asyncio
from datetime import datetime

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, render, LoginManager, login_required, login_user, logout_user, current_user, UserMixin

# Import task decorators to prevent event loop blocking
try:
    from proapi.scheduler import thread_task, auto_task
    HAVE_TASK_DECORATORS = True
    print("Task decorators available - using them to prevent event loop blocking")
except ImportError:
    HAVE_TASK_DECORATORS = False
    print("Task decorators not available - event loop blocking may occur")

# Create a ProAPI application with sessions enabled
app = ProAPI(
    debug=True,
    enable_sessions=True,
    session_secret_key="example-secret-key",  # Use a secure key in production
    template_dir=os.path.join(os.path.dirname(__file__), "templates"),
    static_dir=os.path.join(os.path.dirname(__file__), "static"),
    protect_event_loop=True,  # Enable event loop protection
    auto_offload_blocking=True  # Automatically offload blocking operations
)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = "/login"
login_manager.login_message = "Please log in to access this page."


# User class
class User(UserMixin):
    """
    User class for the example.
    
    In a real application, this would typically be a database model.
    """
    
    def __init__(self, id, username, password, email=None):
        self.id = id
        self.username = username
        self.password = password  # In a real app, this would be hashed
        self.email = email
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }


# Simple user database (in a real app, this would be a database)
users = {
    "1": User(id="1", username="admin", password="admin", email="admin@example.com"),
    "2": User(id="2", username="user", password="user", email="user@example.com")
}

# User loader function
@login_manager.user_loader
def load_user(user_id):
    """Load a user from the user database."""
    return users.get(user_id)


# Routes

# Define a decorator that uses thread_task if available
def use_thread_task(func):
    """Use thread_task if available, otherwise return the original function."""
    if HAVE_TASK_DECORATORS:
        return thread_task(func)
    return func

@app.get("/")
@use_thread_task
async def index(request):
    """Home page."""
    return render("login_example/index.html", 
                 title="Home",
                 user=current_user if current_user.is_authenticated else None)


@app.get("/login")
@use_thread_task
async def login_page(request):
    """Login page."""
    # Check if user is already logged in
    if current_user.is_authenticated:
        return app.redirect("/profile")
    
    # Get next URL from session or query parameter
    next_url = request.session.get("_next") or request.get_query_param("next", "/")
    
    return render("login_example/login.html", 
                 title="Login",
                 next=next_url)


@app.post("/login")
@use_thread_task
async def login_submit(request):
    """Process login form."""
    username = request.form.get("username")
    password = request.form.get("password")
    remember = request.form.get("remember") == "on"
    
    # Get next URL from session or form
    next_url = request.session.get("_next") or request.form.get("next", "/")
    
    # Find user by username
    user = next((u for u in users.values() if u.username == username), None)
    
    # Check credentials
    if user and user.password == password:  # In a real app, use proper password verification
        # Log in the user
        login_user(user, remember=remember)
        
        # Clear next URL from session
        if "_next" in request.session:
            del request.session["_next"]
        
        # Redirect to next URL
        return app.redirect(next_url)
    else:
        # Invalid credentials
        return render("login_example/login.html", 
                     title="Login",
                     error="Invalid username or password",
                     username=username,
                     next=next_url)


@app.get("/logout")
@use_thread_task
async def logout(request):
    """Log out the current user."""
    logout_user()
    return app.redirect("/")


@app.get("/profile")
@login_required
@use_thread_task
async def profile(request):
    """User profile page (protected)."""
    return render("login_example/profile.html", 
                 title="Profile",
                 user=current_user)


@app.get("/admin")
@login_required
@use_thread_task
async def admin(request):
    """Admin page (protected)."""
    # Check if user is admin
    if current_user.username != "admin":
        return render("login_example/error.html", 
                     title="Access Denied",
                     message="You do not have permission to access this page.")
    
    return render("login_example/admin.html", 
                 title="Admin",
                 users=users.values())


@app.get("/api/user")
@login_required
@use_thread_task
async def api_user(request):
    """API endpoint for user data (protected)."""
    return current_user.to_dict()


# Create template directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), "templates", "login_example"), exist_ok=True)

# Create templates if they don't exist
templates = {
    "index.html": """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - ProAPI Login Example</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; }
        nav { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #ddd; }
        nav a { margin-right: 15px; text-decoration: none; color: #0066cc; }
        .message { padding: 10px; background-color: #e8f4f8; border-left: 5px solid #0066cc; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <a href="/">Home</a>
            {% if user %}
                <a href="/profile">Profile</a>
                {% if user.username == 'admin' %}
                    <a href="/admin">Admin</a>
                {% endif %}
                <a href="/logout">Logout</a>
            {% else %}
                <a href="/login">Login</a>
            {% endif %}
        </nav>
        
        <h1>Welcome to ProAPI Login Example</h1>
        
        <div class="message">
            {% if user %}
                <p>You are logged in as <strong>{{ user.username }}</strong>.</p>
            {% else %}
                <p>You are not logged in. <a href="/login">Login</a> to access protected pages.</p>
            {% endif %}
        </div>
        
        <h2>Available Pages</h2>
        <ul>
            <li><a href="/">Home</a> - Public page</li>
            <li><a href="/profile">Profile</a> - Protected page (requires login)</li>
            <li><a href="/admin">Admin</a> - Protected page (requires admin login)</li>
            <li><a href="/api/user">API User</a> - Protected API endpoint (requires login)</li>
        </ul>
        
        <h2>Test Users</h2>
        <ul>
            <li>Admin: username=<code>admin</code>, password=<code>admin</code></li>
            <li>Regular User: username=<code>user</code>, password=<code>user</code></li>
        </ul>
    </div>
</body>
</html>
    """,
    
    "login.html": """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - ProAPI Login Example</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; }
        nav { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #ddd; }
        nav a { margin-right: 15px; text-decoration: none; color: #0066cc; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 8px; box-sizing: border-box; }
        button { padding: 8px 16px; background-color: #0066cc; color: white; border: none; cursor: pointer; }
        .error { color: red; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <a href="/">Home</a>
            <a href="/login">Login</a>
        </nav>
        
        <h1>Login</h1>
        
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="post" action="/login">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" value="{{ username or '' }}" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="remember"> Remember me
                </label>
            </div>
            
            <input type="hidden" name="next" value="{{ next }}">
            
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
    """,
    
    "profile.html": """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - ProAPI Login Example</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; }
        nav { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #ddd; }
        nav a { margin-right: 15px; text-decoration: none; color: #0066cc; }
        .user-info { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }
        .user-info dt { font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <a href="/">Home</a>
            <a href="/profile">Profile</a>
            {% if user.username == 'admin' %}
                <a href="/admin">Admin</a>
            {% endif %}
            <a href="/logout">Logout</a>
        </nav>
        
        <h1>User Profile</h1>
        
        <div class="user-info">
            <dl>
                <dt>Username:</dt>
                <dd>{{ user.username }}</dd>
                
                <dt>Email:</dt>
                <dd>{{ user.email or 'Not set' }}</dd>
                
                <dt>User ID:</dt>
                <dd>{{ user.id }}</dd>
            </dl>
        </div>
    </div>
</body>
</html>
    """,
    
    "admin.html": """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - ProAPI Login Example</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; }
        nav { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #ddd; }
        nav a { margin-right: 15px; text-decoration: none; color: #0066cc; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <a href="/">Home</a>
            <a href="/profile">Profile</a>
            <a href="/admin">Admin</a>
            <a href="/logout">Logout</a>
        </nav>
        
        <h1>Admin Panel</h1>
        
        <h2>User Management</h2>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                    <tr>
                        <td>{{ user.id }}</td>
                        <td>{{ user.username }}</td>
                        <td>{{ user.email or 'Not set' }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
    """,
    
    "error.html": """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - ProAPI Login Example</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; }
        nav { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #ddd; }
        nav a { margin-right: 15px; text-decoration: none; color: #0066cc; }
        .error { color: red; padding: 15px; background-color: #ffeeee; border-left: 5px solid red; }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <a href="/">Home</a>
            {% if current_user.is_authenticated %}
                <a href="/profile">Profile</a>
                {% if current_user.username == 'admin' %}
                    <a href="/admin">Admin</a>
                {% endif %}
                <a href="/logout">Logout</a>
            {% else %}
                <a href="/login">Login</a>
            {% endif %}
        </nav>
        
        <h1>{{ title }}</h1>
        
        <div class="error">
            <p>{{ message }}</p>
        </div>
        
        <p><a href="/">Return to Home</a></p>
    </div>
</body>
</html>
    """
}

# Create template files
for template_name, template_content in templates.items():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "login_example", template_name)
    if not os.path.exists(template_path):
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        with open(template_path, "w") as f:
            f.write(template_content)


if __name__ == "__main__":
    print("Login Example running at http://localhost:8000/")
    print("Available users:")
    print("  - Admin: username=admin, password=admin")
    print("  - User: username=user, password=user")
    
    # Use the fixed ASGI adapter
    try:
        from proapi.asgi_adapter_fix import set_app
        set_app(app)
        print("Using fixed ASGI adapter")
    except ImportError:
        print("Fixed ASGI adapter not available, using default adapter")
    
    # Enable loop protection to prevent event loop blocking
    try:
        from proapi.loop_protection import start_loop_monitoring
        start_loop_monitoring(warning_threshold=0.5, critical_threshold=1.0)
        print("Event loop protection enabled")
    except ImportError:
        print("Event loop protection not available")
    
    # Run the application
    app.run(host="localhost", port=8000)
