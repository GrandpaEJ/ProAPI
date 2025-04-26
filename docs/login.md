# User Authentication in ProAPI

ProAPI includes built-in support for user authentication similar to Flask-Login. This guide explains how to implement user authentication in your application.

## Basic Setup

First, enable sessions and create a login manager:

```python
from proapi import ProAPI, LoginManager

app = ProAPI(
    enable_sessions=True,
    session_secret_key="your-secret-key-here"  # Use a secure random key in production
)

login_manager = LoginManager(app)
login_manager.login_view = "/login"  # Where to redirect when login is required
```

## Creating a User Class

Create a user class that implements the required methods:

```python
from proapi import UserMixin

class User(UserMixin):
    def __init__(self, id, username, email=None):
        self.id = id
        self.username = username
        self.email = email

    # UserMixin provides these methods:
    # - is_authenticated (returns True)
    # - is_active (returns True)
    # - is_anonymous (returns False)
    # - get_id (returns str(self.id))
```

## User Loader Function

Register a function that loads a user from the user ID:

```python
@login_manager.user_loader
def load_user(user_id):
    # Load user from database
    return User.get(user_id)
```

## Login and Logout

Use the `login_user` and `logout_user` functions to log users in and out:

```python
from proapi import login_user, logout_user

@app.post("/login")
def login(request):
    username = request.form.get("username")
    password = request.form.get("password")
    remember = request.form.get("remember") == "on"

    # Find user and verify password
    user = find_user(username)
    if user and verify_password(user, password):
        login_user(user, remember=remember)
        return redirect("/dashboard")
    else:
        return {"error": "Invalid credentials"}

@app.get("/logout")
def logout(request):
    logout_user()
    return redirect("/")
```

## Protecting Routes

Use the `login_required` decorator to protect routes:

```python
from proapi import login_required

@app.get("/profile")
@login_required
def profile(request):
    return {"user": current_user.username}

# You can also specify a custom redirect URL
@app.get("/admin")
@login_required(redirect_to="/login?next=/admin")
def admin(request):
    return {"message": "Admin area"}
```

## Accessing the Current User

The `current_user` proxy provides access to the current user:

```python
from proapi import current_user

@app.get("/")
def index(request):
    if current_user.is_authenticated:
        return {"message": f"Hello, {current_user.username}!"}
    else:
        return {"message": "Hello, guest!"}
```

## HTML Responses in Login Routes

When creating login pages or other authentication-related pages, you can return HTML content in two ways:

### Method 1: Direct HTML Return

You can return HTML content directly as a string:

```python
@app.get("/login")
def login_page(request):
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

### Method 2: Using Response Class

For more control over the response, you can use the Response class with an explicit content type:

```python
from proapi.server.server import Response

@app.get("/login")
def login_page(request):
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

### Method 3: Using Template Rendering

For more complex pages, you can use template rendering:

```python
from proapi import render

@app.get("/login")
def login_page(request):
    return render("login.html",
                 title="Login",
                 error=None)
```

## Complete Example

Here's a complete example of user authentication in ProAPI:

```python
from proapi import ProAPI, LoginManager, UserMixin, login_required, login_user, logout_user, current_user

app = ProAPI(
    enable_sessions=True,
    session_secret_key="your-secret-key-here"
)

login_manager = LoginManager(app)
login_manager.login_view = "/login"

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password  # In a real app, this would be hashed

# Simple user database
users = {
    "1": User(id="1", username="admin", password="admin"),
    "2": User(id="2", username="user", password="user")
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.get("/")
def index(request):
    if current_user.is_authenticated:
        return {"message": f"Hello, {current_user.username}!"}
    else:
        return {"message": "Hello, guest!"}

@app.get("/login")
def login_page(request):
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

@app.post("/login")
def login_submit(request):
    username = request.form.get("username")
    password = request.form.get("password")

    # Find user by username
    user = next((u for u in users.values() if u.username == username), None)

    if user and user.password == password:
        login_user(user)
        return app.redirect("/")
    else:
        # Return error message with login form
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .form-group {{ margin-bottom: 15px; }}
                label {{ display: block; margin-bottom: 5px; }}
                input {{ width: 300px; padding: 8px; border: 1px solid #ddd; }}
                button {{ background-color: #4CAF50; color: white; padding: 10px 15px; border: none; }}
                .error {{ color: red; margin-bottom: 15px; }}
            </style>
        </head>
        <body>
            <h1>Login</h1>
            <div class="error">Invalid credentials</div>
            <form method="post" action="/login">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" value="{username}" required>
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
        return html

@app.get("/logout")
def logout(request):
    logout_user()
    return app.redirect("/")

@app.get("/profile")
@login_required
def profile(request):
    return {"user": current_user.username}

if __name__ == "__main__":
    app.run()
```

## Advanced Configuration

### Custom Anonymous User

You can customize the anonymous user class:

```python
class CustomAnonymousUser:
    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return ""

    # Custom properties
    @property
    def role(self):
        return "guest"

login_manager.anonymous_user = CustomAnonymousUser
```

### Custom Login Messages

You can customize the login messages:

```python
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"
```

## Integration with Session System

The login system integrates with ProAPI's session system. Make sure to enable sessions when using the login system:

```python
app = ProAPI(
    enable_sessions=True,
    session_secret_key="your-secret-key-here"
)
```

The login system stores the user ID in the session, and loads the user from the user ID on each request.
