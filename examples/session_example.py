"""
Example of session functionality with ProAPI.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, render

# Create the application with session support enabled
app = ProAPI(
    debug=True,
    enable_sessions=True,
    session_secret_key="your-secret-key-here",  # In production, use a secure random key
    session_max_age=3600,  # 1 hour
    session_backend="memory"  # Use in-memory session storage
)

# Define routes

@app.get("/")
def index(request):
    """Home page."""
    # Get visit count from session or initialize to 0
    visit_count = request.session.get("visit_count", 0)
    
    # Increment visit count
    visit_count += 1
    
    # Store updated visit count in session
    request.session["visit_count"] = visit_count
    
    return {
        "message": "Welcome to the session example!",
        "visit_count": visit_count,
        "session_id": request.session.session_id
    }

@app.get("/set/{key}/{value}")
def set_session(key, value, request):
    """Set a session value."""
    request.session[key] = value
    return {
        "message": f"Session value set: {key} = {value}",
        "session_data": request.session.data
    }

@app.get("/get/{key}")
def get_session(key, request):
    """Get a session value."""
    value = request.session.get(key, "Not found")
    return {
        "key": key,
        "value": value
    }

@app.get("/clear")
def clear_session(request):
    """Clear the session."""
    # Store the old session data for display
    old_data = dict(request.session.data)
    
    # Clear the session
    request.session.clear()
    
    return {
        "message": "Session cleared",
        "old_data": old_data,
        "current_data": request.session.data
    }

@app.get("/logout")
def logout(request):
    """Log out by deleting the session."""
    from proapi.server import Response
    
    # Create a response
    response = Response(
        body={"message": "Logged out successfully"},
        content_type="application/json"
    )
    
    # Delete the session (this will clear the session cookie)
    request.save_session(response)
    request.session.clear()
    
    return response

# Run the application
if __name__ == "__main__":
    app.run()
