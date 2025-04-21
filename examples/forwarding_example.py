"""
Example of port forwarding with ProAPI.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create the application with port forwarding enabled
app = ProAPI(
    debug=True,
    enable_forwarding=True,  # Enable port forwarding by default
    forwarding_type="ngrok"  # Use ngrok (or "localtunnel")
)

@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Welcome to the port forwarding example!",
        "host": request.headers.get("Host", "unknown"),
        "remote_addr": request.remote_addr
    }

@app.get("/hello/{name}")
def hello(name, request):
    """Hello endpoint."""
    return {
        "message": f"Hello, {name}!",
        "host": request.headers.get("Host", "unknown")
    }

@app.get("/info")
def info(request):
    """Server information."""
    import platform
    import socket
    
    # Try to get local IP
    local_ip = "unknown"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        pass
    
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "local_ip": local_ip,
        "host": request.headers.get("Host", "unknown"),
        "remote_addr": request.remote_addr,
        "headers": {k: v for k, v in request.headers.items()}
    }

if __name__ == "__main__":
    print("This is a port forwarding example for ProAPI.")
    print("The application will be accessible from the internet.")
    print()
    print("You can run this example in different ways:")
    print()
    print("  # Run with default settings (forwarding enabled)")
    print("  python examples/forwarding_example.py")
    print()
    print("  # Run with CLI and explicit forwarding")
    print("  python -m proapi run examples/forwarding_example.py --forward")
    print()
    print("  # Run with CLI and localtunnel")
    print("  python -m proapi run examples/forwarding_example.py --forward --forward-type localtunnel")
    print()
    print("  # Run without forwarding")
    print("  python -m proapi run examples/forwarding_example.py")
    print()
    
    # Run the application
    app.run(host="0.0.0.0", port=8007)
