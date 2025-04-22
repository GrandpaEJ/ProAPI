"""
Example ProAPI application.

This is a simple example of how to use the ProAPI framework.
"""

from proapi import ProAPI, render

# Create the application
app = ProAPI(debug=True)

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
        "message": "Welcome to ProAPI with Sessions!",
        "description": "A lightweight, beginner-friendly yet powerful Python web framework.",
        "visit_count": visit_count,
        "user_agent": request.headers.get("User-Agent", "Unknown"),
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This endpoint"},
            {"path": "/hello/{name}", "method": "GET", "description": "Get a personalized greeting"},
            {"path": "/json", "method": "POST", "description": "Echo JSON data"},
            {"path": "/html", "method": "GET", "description": "HTML example"},
            {"path": "/login", "method": "GET", "description": "Login page"},
            {"path": "/admin", "method": "GET", "description": "Admin page (requires login)"},
            {"path": "/logout", "method": "GET", "description": "Logout"}
        ]
    }

@app.get("/hello/{name}")
def hello(name):
    """Get a personalized greeting."""
    # Get the previous names from session or initialize to empty list
    previous_names = session.get("previous_names", [])

    # Add the current name if it's not already in the list
    if name not in previous_names:
        previous_names.append(name)
        session["previous_names"] = previous_names

    return {
        "message": f"Hello, {name}!",
        "previous_names": previous_names
    }

@app.post("/json")
def json_handler():
    """Echo JSON data."""
    return jsonify({
        "received": request.json,
        "message": "JSON data received successfully",
        "session_data": {k: v for k, v in session.data.items()}
    })

@app.get("/html")
def html_example():
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

# Login routes
@app.get("/login")
def login():
    """Login page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - ProAPI Test</title>
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
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            input[type="text"],
            input[type="password"] {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
            .error {
                color: red;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <h1>Login</h1>

        <div class="content">
            <h2>Login to Your Account</h2>

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

            <p><small>Hint: Use "admin" / "password" to login</small></p>
        </div>
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
        return redirect("/admin")
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Failed</title>
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
                .error {
                    color: red;
                    margin-bottom: 15px;
                }
            </style>
        </head>
        <body>
            <h1>Login Failed</h1>
            <div class="error">Invalid username or password.</div>
            <p><a href="/login">Try again</a></p>
        </body>
        </html>
        """

@app.get("/admin")
def admin():
    """Admin page."""
    if "username" not in session:
        return redirect("/login")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - ProAPI Test</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #333;
            }}
            .dashboard {{
                margin-top: 20px;
            }}
            .dashboard-item {{
                background-color: white;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .logout {{
                display: inline-block;
                background-color: #cc0000;
                color: white;
                text-decoration: none;
                padding: 8px 15px;
                border-radius: 4px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Admin Dashboard</h1>

        <div class="content">
            <h2>Welcome, {session["username"]}!</h2>
            <p>You are logged in to the admin dashboard.</p>

            <div class="dashboard">
                <div class="dashboard-item">
                    <h3>Session Data</h3>
                    <pre>{str(session.data)}</pre>
                </div>
            </div>

            <a href="/logout" class="logout">Logout</a>
        </div>
    </body>
    </html>
    """

@app.get("/logout")
def logout():
    """Logout."""
    session.clear()
    return redirect("/")

# Add middleware for logging
@app.use
def logging_middleware(request):
    """Log requests."""
    print(f"Request: {request.method} {request.path}")
    return request

# Run the application
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
