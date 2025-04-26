"""
Authentication Example for ProAPI

This example demonstrates the various authentication features in ProAPI:
- Basic user authentication with LoginManager
- JWT authentication
- HTTP Basic and Digest authentication
- Role-based access control with Principal
- User account management with UserManager

To run this example:
    python auth_example.py

Then visit http://localhost:8000/ in your browser.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import (
    ProAPI, render, app_logger,
    # Login
    LoginManager, login_required, login_user, logout_user, current_user, UserMixin,
    # JWT
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    # HTTP Auth
    HTTPBasicAuth, HTTPDigestAuth,
    # RBAC
    Principal, Permission, RoleNeed, UserNeed, admin_permission,
    # User Management
    UserManager
)
from proapi.server.server import Response

# Configure logging
logger = app_logger.bind(name="auth_example")

# Create a ProAPI application with sessions enabled
app = ProAPI(
    debug=True,
    enable_sessions=True,
    session_secret_key="example-secret-key",  # Use a secure key in production
    template_dir=os.path.join(os.path.dirname(__file__), "templates"),
    static_dir=os.path.join(os.path.dirname(__file__), "static")
)

# Initialize authentication components
login_manager = LoginManager(app)
login_manager.login_view = "/login"

jwt = JWTManager(app, secret_key="jwt-secret-key")

basic_auth = HTTPBasicAuth()
digest_auth = HTTPDigestAuth()

principal = Principal(app)

user_manager = UserManager(app, login_manager=login_manager)


# User class
class User(UserMixin):
    """
    User class for the example.

    In a real application, this would typically be a database model.
    """

    def __init__(self, id, username, password, email=None, roles=None):
        self.id = id
        self.username = username
        self.password = password  # In a real app, this would be hashed
        self.email = email
        self.roles = roles or []
        self.email_confirmed = False

    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "roles": self.roles
        }


# Simple user database
users = {
    "1": User(id="1", username="admin", password="admin", email="admin@example.com", roles=["admin"]),
    "2": User(id="2", username="user", password="user", email="user@example.com", roles=["user"]),
    "3": User(id="3", username="editor", password="editor", email="editor@example.com", roles=["editor"])
}


# User loader for LoginManager
@login_manager.user_loader
def load_user(user_id):
    """Load a user from the user database."""
    return users.get(user_id)


# Password verification for HTTPBasicAuth
@basic_auth.verify_password
def verify_basic_password(username, password):
    """Verify username and password for HTTP Basic authentication."""
    for user in users.values():
        if user.username == username and user.password == password:
            return user
    return None


# Password verification for HTTPDigestAuth
@digest_auth.verify_password
def verify_digest_password(username):
    """Get password for HTTP Digest authentication."""
    for user in users.values():
        if user.username == username:
            return user.password
    return None


# Identity loader for Principal
@principal.identity_loader
def load_identity():
    """Load identity for role-based access control."""
    if current_user.is_authenticated:
        return {
            "user_id": current_user.id,
            "roles": current_user.roles
        }
    return None


# Password hasher for UserManager
@user_manager.password_hasher
def hash_password(password):
    """Hash a password (simplified for example)."""
    return password  # In a real app, use a secure hashing algorithm


# Password verifier for UserManager
@user_manager.password_verifier
def verify_password(user, password):
    """Verify a password (simplified for example)."""
    return user.password == password  # In a real app, use secure verification


# User creator for UserManager
@user_manager.user_creator
def create_user(username, email, password):
    """Create a new user."""
    user_id = str(len(users) + 1)
    user = User(id=user_id, username=username, password=password, email=email, roles=["user"])
    users[user_id] = user
    return user


# User finder for UserManager
@user_manager.user_finder
def find_user_by_email(email):
    """Find a user by email."""
    for user in users.values():
        if user.email == email:
            return user
    return None


# Define permissions
admin_only = Permission(RoleNeed('admin'))
editor_only = Permission(RoleNeed('editor'))
user_only = Permission(RoleNeed('user'))


# Routes

@app.get("/")
def index(request):
    """Home page."""
    logger.debug("Rendering home page")

    # Check if user is authenticated
    is_authenticated = current_user.is_authenticated
    username = current_user.username if is_authenticated else "guest"

    # Return a direct HTML response with content type explicitly set
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentication Example</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            nav {{ margin-bottom: 20px; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }}
            nav a {{ margin-right: 10px; text-decoration: none; color: #333; }}
            .card {{ border: 1px solid #ddd; border-radius: 5px; padding: 20px; margin-bottom: 20px; }}
            .card h2 {{ margin-top: 0; }}
            .api-example {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <nav>
            <a href="/">Home</a>
            {'''
            <a href="/profile">Profile</a>
            <a href="/logout">Logout</a>
            ''' if is_authenticated else '''
            <a href="/login">Login</a>
            <a href="/register">Register</a>
            '''}
        </nav>

        <h1>Authentication Example</h1>

        {f'<p>Welcome, {username}!</p>' if is_authenticated else '<p>Welcome, guest! Please <a href="/login">login</a> or <a href="/register">register</a> to access all features.</p>'}

        <div class="card">
            <h2>Authentication Features</h2>
            <p>This example demonstrates the various authentication features in ProAPI:</p>
            <ul>
                <li>Basic user authentication with LoginManager</li>
                <li>JWT authentication for APIs</li>
                <li>HTTP Basic and Digest authentication</li>
                <li>Role-based access control with Principal</li>
                <li>User account management with UserManager</li>
            </ul>
        </div>

        <div class="card">
            <h2>API Endpoints</h2>
            <p>The following API endpoints are available for testing:</p>

            <h3>JWT Authentication</h3>
            <div class="api-example">POST /api/login</div>
            <p>Login and get JWT tokens. Send a JSON body with username and password:</p>
            <pre>
{{
    "username": "admin",
    "password": "admin"
}}
            </pre>

            <div class="api-example">GET /api/protected</div>
            <p>Protected endpoint using JWT authentication. Send the access token in the Authorization header:</p>
            <pre>
Authorization: Bearer &lt;access_token&gt;
            </pre>

            <h3>HTTP Basic Authentication</h3>
            <div class="api-example">GET /api/basic-auth</div>
            <p>Protected endpoint using HTTP Basic authentication. Send username and password in the Authorization header.</p>

            <h3>HTTP Digest Authentication</h3>
            <div class="api-example">GET /api/digest-auth</div>
            <p>Protected endpoint using HTTP Digest authentication.</p>
        </div>

        <div class="card">
            <h2>Role-Based Access Control</h2>
            <p>The following pages are protected by role-based access control:</p>
            <ul>
                <li><a href="/admin">Admin Page</a> - Requires admin role</li>
                <li><a href="/editor">Editor Page</a> - Requires editor role</li>
                <li><a href="/user">User Page</a> - Requires user role</li>
            </ul>
        </div>
    </body>
    </html>
    """

    return Response(
        status=200,
        body=html,
        content_type="text/html"
    )


# Login routes

@app.get("/login")
def login_get(request):
    """Login page."""
    next_url = request.query_params.get('next', '/')
    logger.debug("Rendering login page")

    # Return a direct HTML response with content type explicitly set
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; }}
            input {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
            button {{ background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>Login</h1>
        <form method="post" action="/login">
            <input type="hidden" name="next" value="{next_url}">

            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
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

            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="/register">Register</a></p>
    </body>
    </html>
    """

    return Response(
        status=200,
        body=html,
        content_type="text/html"
    )


@app.post("/login")
def login_post(request):
    """Handle login form submission."""
    data = request.form
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember') == 'on'
    next_url = data.get('next', '/')

    # Find user by username
    user = None
    for u in users.values():
        if u.username == username:
            user = u
            break

    # Check credentials
    if user and user.password == password:  # In a real app, use proper password verification
        # Log in the user
        login_user(user, remember=remember)

        # Redirect to next URL
        return app.redirect(next_url)
    else:
        # Invalid credentials
        return render("auth_example/login.html",
                     title="Login",
                     error="Invalid username or password",
                     username=username,
                     next=next_url)


@app.get("/logout")
def logout(request):
    """Log out the current user."""
    logout_user()
    return app.redirect("/")


@app.get("/profile")
@login_required
def profile(request):
    """User profile page (protected)."""
    logger.debug("Rendering profile page")

    # Return a direct HTML response with content type explicitly set
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Profile</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            nav {{ margin-bottom: 20px; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }}
            nav a {{ margin-right: 10px; text-decoration: none; color: #333; }}
            .card {{ border: 1px solid #ddd; border-radius: 5px; padding: 20px; margin-bottom: 20px; }}
            .card h2 {{ margin-top: 0; }}
            .profile-info {{ margin-bottom: 20px; }}
            .profile-info p {{ margin: 5px 0; }}
            .profile-info strong {{ display: inline-block; width: 100px; }}
            .badge {{ display: inline-block; padding: 3px 8px; background-color: #4CAF50; color: white; border-radius: 4px; margin-right: 5px; }}
        </style>
    </head>
    <body>
        <nav>
            <a href="/">Home</a>
            <a href="/profile">Profile</a>
            <a href="/logout">Logout</a>
        </nav>

        <h1>Profile</h1>

        <div class="card">
            <h2>User Profile</h2>
            <div class="profile-info">
                <p><strong>Username:</strong> {current_user.username}</p>
                <p><strong>Email:</strong> {current_user.email if hasattr(current_user, 'email') else 'N/A'}</p>
                <p><strong>ID:</strong> {current_user.id}</p>
                <p>
                    <strong>Roles:</strong>
                    {' '.join([f'<span class="badge">{role}</span>' for role in current_user.roles]) if hasattr(current_user, 'roles') else 'N/A'}
                </p>
            </div>
        </div>

        <div class="card">
            <h2>Available Pages</h2>
            <p>Based on your roles, you can access the following pages:</p>
            <ul>
                {f'<li><a href="/admin">Admin Page</a></li>' if hasattr(current_user, 'roles') and 'admin' in current_user.roles else ''}
                {f'<li><a href="/editor">Editor Page</a></li>' if hasattr(current_user, 'roles') and 'editor' in current_user.roles else ''}
                {f'<li><a href="/user">User Page</a></li>' if hasattr(current_user, 'roles') and 'user' in current_user.roles else ''}
            </ul>
        </div>

        <div class="card">
            <h2>API Access</h2>
            <p>You can access the API endpoints using your credentials:</p>
            <ul>
                <li>JWT Authentication: <code>POST /api/login</code> with your username and password</li>
                <li>HTTP Basic Authentication: <code>GET /api/basic-auth</code> with your username and password</li>
                <li>HTTP Digest Authentication: <code>GET /api/digest-auth</code> with your username and password</li>
            </ul>
        </div>
    </body>
    </html>
    """

    return Response(
        status=200,
        body=html,
        content_type="text/html"
    )


# JWT routes

@app.post("/api/login")
def api_login(request):
    """API login endpoint that returns JWT tokens."""
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    # Find user by username
    user = None
    for u in users.values():
        if u.username == username:
            user = u
            break

    # Check credentials
    if user and user.password == password:  # In a real app, use proper password verification
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }
    else:
        return {"error": "Invalid credentials"}, 401


@app.get("/api/protected")
@jwt_required
def api_protected(request):
    """Protected API endpoint using JWT authentication."""
    from proapi.auth.jwt import get_jwt_identity
    user_id = get_jwt_identity()
    user = users.get(user_id)

    if user:
        return {
            "message": f"Hello, {user.username}!",
            "user": user.to_dict()
        }

    return {"error": "User not found"}, 404


@app.post("/api/refresh")
@jwt_required(refresh=True)
def refresh_token(request):
    """Refresh token endpoint."""
    from proapi.auth.jwt import get_jwt_identity
    user_id = get_jwt_identity()

    # Create new access token
    access_token = create_access_token(identity=user_id, fresh=False)

    return {"access_token": access_token}


# HTTP Basic Auth routes

@app.get("/api/basic-auth")
@basic_auth.login_required
def basic_auth_protected(request):
    """Protected API endpoint using HTTP Basic authentication."""
    user = basic_auth.current_user
    return {
        "message": f"Hello, {user.username}!",
        "user": user.to_dict()
    }


# HTTP Digest Auth routes

@app.get("/api/digest-auth")
@digest_auth.login_required
def digest_auth_protected(request):
    """Protected API endpoint using HTTP Digest authentication."""
    username = digest_auth.current_user

    # Find user by username
    user = None
    for u in users.values():
        if u.username == username:
            user = u
            break

    if user:
        return {
            "message": f"Hello, {user.username}!",
            "user": user.to_dict()
        }

    return {"error": "User not found"}, 404


# Role-based access control routes

@app.get("/admin")
@login_required
@admin_only.require()
def admin_page(request):
    """Admin page (requires admin role)."""
    return render("auth_example/admin.html",
                 title="Admin Page",
                 user=current_user)


@app.get("/editor")
@login_required
@editor_only.require()
def editor_page(request):
    """Editor page (requires editor role)."""
    return render("auth_example/editor.html",
                 title="Editor Page",
                 user=current_user)


@app.get("/user")
@login_required
@user_only.require()
def user_page(request):
    """User page (requires user role)."""
    return render("auth_example/user.html",
                 title="User Page",
                 user=current_user)


# User management routes

@app.get("/registe")
def registe_get(request):
    """Registration page (alternative URL)."""
    logger.debug("Rendering registration page (alternative URL)")

    # Return a simple HTML string directly
    html = f"""
    <html>
    <head>
        <title>Register</title>
    </head>
    <body>
        <h1>Register</h1>
        <form method="post" action="/register">
            <div>
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div>
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div>
                <label for="confirm_password">Confirm Password:</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="/login">Login</a></p>
    </body>
    </html>
    """
    return Response(
        status=200,
        body=html,
        content_type="text/html"
    )


@app.get("/register")
def register_get_direct(request):
    """Registration page (original URL)."""
    logger.debug("Rendering registration page (original URL)")

    # Return a full HTML registration form
    return """
    <html>
    <head>
        <title>Register</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input { width: 300px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Register</h1>
        <form method="post" action="/register">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="confirm_password">Confirm Password:</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="/login">Login</a></p>
    </body>
    </html>
    """


@app.get("/register-alt")
def register_alt_get(request):
    """Registration page with different function name but same path structure."""
    logger.debug("Rendering registration page with different function name")

    # Return a simple HTML string directly without using Response
    return """<!DOCTYPE html>
<html>
<head>
    <title>Register Alt</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
    </style>
</head>
<body>
    <h1>Register Alt Page</h1>
    <p>This is a test to see if direct HTML return works with a different function name.</p>
    <form method="post" action="/register">
        <div>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <div>
            <label for="confirm_password">Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required>
        </div>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="/login">Login</a></p>
</body>
</html>"""


@app.get("/register2")
def register_get2(request):
    """Test registration page with same function name but different path."""
    logger.debug("Rendering registration page with same function name but different path")

    # Return a simple HTML string directly without using Response
    return """<!DOCTYPE html>
<html>
<head>
    <title>Register 2</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
    </style>
</head>
<body>
    <h1>Register 2 Page</h1>
    <p>This is a test to see if direct HTML return works with the same function name but different path.</p>
    <form method="post" action="/register">
        <div>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <div>
            <label for="confirm_password">Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required>
        </div>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="/login">Login</a></p>
</body>
</html>"""


@app.get("/test-register")
def test_register_get(request):
    """Test registration page with direct HTML return."""
    logger.debug("Rendering test registration page")

    # Return a simple HTML string directly without using Response
    return """<!DOCTYPE html>
<html>
<head>
    <title>Test Register</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
    </style>
</head>
<body>
    <h1>Test Register Page</h1>
    <p>This is a test to see if direct HTML return works on a different path.</p>
    <form method="post" action="/register">
        <div>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <div>
            <label for="confirm_password">Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required>
        </div>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="/login">Login</a></p>
</body>
</html>"""


@app.get("/user/register")
def user_register_get(request):
    """Test registration page with a different path structure."""
    logger.debug("Rendering user registration page")

    # Return a simple HTML string directly without using Response
    return """<!DOCTYPE html>
<html>
<head>
    <title>User Register</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
    </style>
</head>
<body>
    <h1>User Register Page</h1>
    <p>This is a test to see if direct HTML return works on a different path structure.</p>
    <form method="post" action="/register">
        <div>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <div>
            <label for="confirm_password">Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required>
        </div>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="/login">Login</a></p>
</body>
</html>"""


@app.get("/signup")
def signup_get(request):
    """Registration page (another alternative URL)."""
    logger.debug("Rendering registration page (another alternative URL)")

    # Return a simple HTML string directly with Response
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Register</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
    </style>
</head>
<body>
    <h1>Register</h1>
    <form method="post" action="/register">
        <div>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <div>
            <label for="confirm_password">Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required>
        </div>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="/login">Login</a></p>
</body>
</html>"""

    return Response(
        status=200,
        body=html,
        content_type="text/html"
    )


@app.post("/register")
def register_post(request):
    """Handle registration form submission."""
    # Debug: Print request information
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request content type: {request.headers.get('Content-Type')}")
    logger.debug(f"Request body: {request.body}")

    # Try different ways to access form data
    form_data = request.form
    logger.debug(f"Form data: {form_data}")

    # Try to parse form data manually if needed
    if not form_data and request.body:
        try:
            from urllib.parse import parse_qs
            body_str = request.body.decode('utf-8')
            parsed_data = parse_qs(body_str)
            logger.debug(f"Manually parsed form data: {parsed_data}")

            # Extract values from parsed data
            username = parsed_data.get('username', [''])[0]
            email = parsed_data.get('email', [''])[0]
            password = parsed_data.get('password', [''])[0]
            confirm_password = parsed_data.get('confirm_password', [''])[0]
        except Exception as e:
            logger.error(f"Error parsing form data: {str(e)}")
            username = email = password = confirm_password = None
    else:
        # Use regular form data
        username = form_data.get('username')
        email = form_data.get('email')
        password = form_data.get('password')
        confirm_password = form_data.get('confirm_password')

    logger.debug(f"Username: {username}")
    logger.debug(f"Email: {email}")
    logger.debug(f"Password: {'*' * len(password) if password else None}")
    logger.debug(f"Confirm Password: {'*' * len(confirm_password) if confirm_password else None}")

    # Validate data
    if not all([username, email, password, confirm_password]):
        return render("auth_example/register.html",
                     title="Register",
                     error="All fields are required",
                     username=username,
                     email=email)

    if password != confirm_password:
        return render("auth_example/register.html",
                     title="Register",
                     error="Passwords do not match",
                     username=username,
                     email=email)

    # Check if user already exists
    for user in users.values():
        if user.username == username:
            return render("auth_example/register.html",
                         title="Register",
                         error="Username already taken",
                         email=email)

        if user.email == email:
            return render("auth_example/register.html",
                         title="Register",
                         error="Email already registered",
                         username=username)

    # Create user
    user = user_manager.create_user(username, email, password)

    # Log in the user
    login_user(user)

    # Redirect to profile page
    return app.redirect("/profile")


# Start the server
if __name__ == "__main__":
    app.run(port=8000)
