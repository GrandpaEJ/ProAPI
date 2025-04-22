"""
Example of global request and session objects with ProAPI.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, request, session, redirect, jsonify, render

# Create the application with session support enabled
app = ProAPI(
    debug=True,
    enable_sessions=True,
    session_secret_key="your-secret-key-here"  # Use a secure random key in production
)

# Define routes

@app.get("/")
def index():
    """Home page."""
    # Get visit count from session or initialize to 0
    visit_count = session.get("visit_count", 0)
    
    # Increment visit count
    visit_count += 1
    
    # Store updated visit count in session
    session["visit_count"] = visit_count
    
    return {
        "message": "Welcome to the global request and session example!",
        "visit_count": visit_count,
        "method": request.method,
        "path": request.path,
        "user_agent": request.headers.get("User-Agent", "Unknown")
    }

@app.get("/redirect")
def redirect_example():
    """Redirect example."""
    return redirect("/")

@app.get("/json")
def json_example():
    """JSON example."""
    return jsonify({
        "message": "This is a JSON response",
        "session_data": {k: v for k, v in session.data.items()},
        "request_info": {
            "method": request.method,
            "path": request.path,
            "headers": {k: v for k, v in request.headers.items()}
        }
    })

@app.get("/login")
def login_form():
    """Login form."""
    return """
    <html>
        <head><title>Login</title></head>
        <body>
            <h1>Login</h1>
            <form method="post" action="/login">
                <div>
                    <label>Username: <input type="text" name="username"></label>
                </div>
                <div>
                    <label>Password: <input type="password" name="password"></label>
                </div>
                <div>
                    <button type="submit">Login</button>
                </div>
            </form>
        </body>
    </html>
    """

@app.post("/login")
def login_submit():
    """Process login form."""
    username = request.form.get("username")
    password = request.form.get("password")
    
    if username == "admin" and password == "password":
        session["username"] = username
        session["is_authenticated"] = True
        return redirect("/profile")
    else:
        return """
        <html>
            <head><title>Login Failed</title></head>
            <body>
                <h1>Login Failed</h1>
                <p>Invalid username or password.</p>
                <p><a href="/login">Try again</a></p>
            </body>
        </html>
        """

@app.get("/profile")
def profile():
    """User profile page."""
    if not session.get("is_authenticated", False):
        return redirect("/login")
    
    return f"""
    <html>
        <head><title>Profile</title></head>
        <body>
            <h1>Welcome, {session.get("username", "Guest")}!</h1>
            <p>You are logged in.</p>
            <p><a href="/logout">Logout</a></p>
        </body>
    </html>
    """

@app.get("/logout")
def logout():
    """Logout."""
    session.clear()
    return redirect("/")

# Run the application
if __name__ == "__main__":
    app.run()
