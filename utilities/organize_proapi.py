"""
Script to organize ProAPI files into a categorized directory structure.
"""

import os
import shutil
import sys

# Define categories and their files
categories = {
    "core": [
        "core.py",
        "cli.py",
        "logging.py",
        "run.py",
        "__init__.py",
        "__main__.py",
    ],
    "routing": [
        "routing.py",
        "request_proxy.py",
        "middleware.py",
    ],
    "server": [
        "server.py",
        "asgi_adapter.py",
        "asgi_adapter_fix.py",
    ],
    "templates": [
        "templating.py",
    ],
    "session": [
        "session.py",
        "session_proxy.py",
    ],
    "auth": [
        "login.py",
    ],
    "websocket": [
        "websocket.py",
        "websocket_middleware.py",
    ],
    "docs": [
        "docs.py",
        "swagger_ui.py",
    ],
    "performance": [
        "optimized.py",
        "scheduler.py",
    ],
    "utils": [
        "utils.py",
        "helper.py",
        "forwarding.py",
        "worker_manager.py",
        "overload_handler.py",
    ],
}

def organize_files():
    """Organize ProAPI files into a categorized directory structure."""
    # Check if we're in the right directory
    if not os.path.exists("proapi"):
        print("Error: proapi directory not found. Please run this script from the root of the ProAPI project.")
        sys.exit(1)
    
    # Create a backup of the proapi directory
    if os.path.exists("proapi_backup"):
        shutil.rmtree("proapi_backup")
    shutil.copytree("proapi", "proapi_backup")
    print("Created backup of proapi directory in proapi_backup")
    
    # Create category directories
    for category in categories:
        os.makedirs(f"proapi/{category}", exist_ok=True)
        print(f"Created directory: proapi/{category}")
    
    # Move files to their respective categories
    for category, files in categories.items():
        for file in files:
            src = f"proapi/{file}"
            dst = f"proapi/{category}/{file}"
            if os.path.exists(src):
                shutil.move(src, dst)
                print(f"Moved {src} to {dst}")
            else:
                print(f"Warning: {src} not found")
    
    print("Organization complete!")

if __name__ == "__main__":
    organize_files()
