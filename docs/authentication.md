# Authentication in ProAPI

ProAPI includes comprehensive authentication and authorization features similar to popular Flask extensions. This guide explains how to use these features in your application.

## Table of Contents

- [Basic Authentication with LoginManager](#basic-authentication-with-loginmanager)
- [JWT Authentication](#jwt-authentication)
- [HTTP Basic and Digest Authentication](#http-basic-and-digest-authentication)
- [Role-Based Access Control](#role-based-access-control)
- [User Account Management](#user-account-management)
- [Complete Example](#complete-example)

## Basic Authentication with LoginManager

LoginManager provides session-based authentication similar to Flask-Login.

### Setup

```python
from proapi import ProAPI, LoginManager, UserMixin, login_required, login_user, logout_user, current_user

app = ProAPI(
    enable_sessions=True,
    session_secret_key="your-secret-key-here"
)

login_manager = LoginManager(app)
login_manager.login_view = "/login"  # Where to redirect when login is required

# User class
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password  # In a real app, this would be hashed

# User database
users = {
    "1": User(id="1", username="admin", password="admin")
}

# User loader
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)
```

### Login and Logout

```python
@app.post("/login")
def login(request):
    username = request.form.get("username")
    password = request.form.get("password")
    remember = request.form.get("remember") == "on"

    # Find user by username
    user = None
    for u in users.values():
        if u.username == username:
            user = u
            break

    # Check credentials
    if user and user.password == password:  # In a real app, use proper password verification
        login_user(user, remember=remember)
        return app.redirect("/")
    else:
        return {"error": "Invalid credentials"}

@app.get("/logout")
def logout(request):
    logout_user()
    return app.redirect("/")
```

### Protecting Routes

```python
@app.get("/profile")
@login_required
def profile(request):
    return {"user": current_user.username}
```

### Accessing the Current User

```python
@app.get("/")
def index(request):
    if current_user.is_authenticated:
        return {"message": f"Hello, {current_user.username}!"}
    else:
        return {"message": "Hello, guest!"}
```

## JWT Authentication

JWTManager provides JSON Web Token authentication for APIs.

### Setup

```python
from proapi import ProAPI, JWTManager, jwt_required, create_access_token, create_refresh_token

app = ProAPI()
jwt = JWTManager(app, secret_key="your-jwt-secret-key")
```

### Login and Token Creation

```python
@app.post("/api/login")
def api_login(request):
    username = request.json.get("username")
    password = request.json.get("password")

    # Check credentials
    if username == "admin" and password == "admin":
        # Create tokens
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    else:
        return {"error": "Invalid credentials"}, 401
```

### Protecting Routes

```python
@app.get("/api/protected")
@jwt_required
def protected(request):
    from proapi.auth.jwt import get_jwt_identity
    current_user = get_jwt_identity()
    return {"message": f"Hello, {current_user}!"}

@app.get("/api/fresh-protected")
@jwt_required(fresh=True)
def fresh_protected(request):
    from proapi.auth.jwt import get_jwt_identity
    current_user = get_jwt_identity()
    return {"message": f"Hello, {current_user}! This endpoint requires a fresh token."}

@app.post("/api/refresh")
@jwt_required(refresh=True)
def refresh(request):
    from proapi.auth.jwt import get_jwt_identity
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return {"access_token": access_token}
```

## HTTP Basic and Digest Authentication

HTTPBasicAuth and HTTPDigestAuth provide HTTP authentication for APIs.

### HTTP Basic Authentication

```python
from proapi import ProAPI, HTTPBasicAuth

app = ProAPI()
basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(username, password):
    if username == "admin" and password == "admin":
        return username
    return None

@app.get("/api/basic-auth")
@basic_auth.login_required
def basic_auth_protected(request):
    return {"message": f"Hello, {basic_auth.current_user}!"}
```

### HTTP Digest Authentication

```python
from proapi import ProAPI, HTTPDigestAuth

app = ProAPI()
digest_auth = HTTPDigestAuth()

@digest_auth.verify_password
def verify_password(username):
    if username == "admin":
        return "admin"  # Return the password for the user
    return None

@app.get("/api/digest-auth")
@digest_auth.login_required
def digest_auth_protected(request):
    return {"message": f"Hello, {digest_auth.current_user}!"}
```

## Role-Based Access Control

Principal provides role-based access control similar to Flask-Principal.

### Setup

```python
from proapi import ProAPI, LoginManager, login_required, current_user, Principal, Permission, RoleNeed, UserNeed

app = ProAPI(enable_sessions=True)
login_manager = LoginManager(app)
principal = Principal(app)

# Define permissions
admin_permission = Permission(RoleNeed('admin'))
editor_permission = Permission(RoleNeed('editor'))
```

### Identity Loader

```python
@principal.identity_loader
def load_identity():
    if current_user.is_authenticated:
        # Return the identity with the user's roles
        return {
            'user_id': current_user.id,
            'roles': current_user.roles
        }
    return None
```

### Protecting Routes

```python
@app.get("/admin")
@login_required
@admin_permission.require()
def admin_page(request):
    return {"message": "Admin page"}

@app.get("/editor")
@login_required
@editor_permission.require()
def editor_page(request):
    return {"message": "Editor page"}
```

## User Account Management

UserManager provides user account management features similar to Flask-User.

### Setup

```python
from proapi import ProAPI, LoginManager, UserManager, UserMixin

app = ProAPI(enable_sessions=True)
login_manager = LoginManager(app)
user_manager = UserManager(app, login_manager=login_manager)

# User class
class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.email_confirmed = False

# User database
users = {}
```

### Callback Functions

```python
@user_manager.password_hasher
def hash_password(password):
    # In a real app, use a secure password hashing algorithm
    return password

@user_manager.password_verifier
def verify_password(user, password):
    # In a real app, use a secure password verification
    return user.password == password

@user_manager.user_creator
def create_user(username, email, password):
    user_id = str(len(users) + 1)
    user = User(id=user_id, username=username, email=email, password=password)
    users[user_id] = user
    return user

@user_manager.user_finder
def find_user_by_email(email):
    for user in users.values():
        if user.email == email:
            return user
    return None
```

### Registration and Email Confirmation

```python
# Registration is handled automatically by UserManager
# You can customize the templates and routes as needed

# To send a confirmation email
user_manager.send_confirmation_email(user)

# To verify a confirmation token
token = request.query_params.get('token')
data = user_manager.verify_token(token)
if data and data.get('action') == 'confirm_email':
    user_id = data.get('user_id')
    user = login_manager._load_user(user_id)
    if user:
        user.email_confirmed = True
```

## HTML Responses in Authentication Routes

When creating authentication routes that return HTML content, you can use either direct string returns or the Response class with explicit content type:

### Direct HTML Return

```python
@app.get("/login")
def login_get(request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input { width: 300px; padding: 8px; border: 1px solid #ddd; }
            button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; }
        </style>
    </head>
    <body>
        <h1>Login</h1>
        <form method="post" action="/login">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """
```

### Using Response Class

```python
from proapi.server.server import Response

@app.get("/login")
def login_get(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input { width: 300px; padding: 8px; border: 1px solid #ddd; }
            button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; }
        </style>
    </head>
    <body>
        <h1>Login</h1>
        <form method="post" action="/login">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """

    return Response(
        status=200,
        body=html,
        content_type="text/html"
    )
```

## Complete Example

For a complete example of all authentication features, see the [auth_example.py](../examples/auth_example.py) file in the examples directory.

```bash
# Run the example
python examples/auth_example.py
```

Then visit http://localhost:8000/ in your browser.

## Additional Resources

- [Login Documentation](login.md) - Detailed documentation for LoginManager
- [JWT Documentation](jwt.md) - Detailed documentation for JWTManager
- [HTTP Auth Documentation](http_auth.md) - Detailed documentation for HTTP authentication
- [Principal Documentation](principal.md) - Detailed documentation for Principal
- [User Management Documentation](user.md) - Detailed documentation for UserManager
