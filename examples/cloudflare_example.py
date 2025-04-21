"""
Example of Cloudflare Tunnel with ProAPI.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI

# Create the application with Cloudflare Tunnel enabled
app = ProAPI(
    debug=True,
    enable_forwarding=True,  # Enable port forwarding by default
    forwarding_type="cloudflare"  # Use Cloudflare Tunnel
)

@app.get("/")
def index(request):
    """Home page."""
    return {
        "message": "Welcome to the Cloudflare Tunnel example!",
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
    print("This is a Cloudflare Tunnel example for ProAPI.")
    print("The application will be accessible from the internet via Cloudflare.")
    print()
    print("You can run this example in different ways:")
    print()
    print("  # Run with default settings (Cloudflare Tunnel)")
    print("  python examples/cloudflare_example.py")
    print()
    print("  # Run with CLI and explicit Cloudflare Tunnel")
    print("  python -m proapi run examples/cloudflare_example.py --forward --forward-type cloudflare")
    print()
    print("  # Run with authenticated tunnel (requires Cloudflare account)")
    print("  python -m proapi run examples/cloudflare_example.py --forward --forward-type cloudflare --cf-token YOUR_TOKEN")
    print()
    print("Note: Authenticated tunnels require a Cloudflare account and a tunnel token.")
    print("You can create a tunnel in the Cloudflare Zero Trust dashboard:")
    print("https://one.dash.cloudflare.com/")
    print()
    
    # Run the application
    app.run(host="0.0.0.0", port=8008)
