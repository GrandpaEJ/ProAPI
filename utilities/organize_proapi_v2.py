"""
Script to organize ProAPI files into a categorized directory structure.
"""

import os
import shutil
import sys

# Define categories and their files
categories = {
    "core": [
        "core/core.py",
        "core/cli.py",
        "core/logging.py",
        "core/run.py",
        "core/docs.py",
        "core/swagger_ui.py",
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
        "asgi/asgi.py",
        "asgi/asgi_adapter.py",
        "asgi/asgi_adapter_fix.py",
    ],
    "templates": [
        "templating.py",
        "templates/",
    ],
    "session": [
        "session/session.py",
        "session/session_proxy.py",
    ],
    "auth": [
        "login.py",
    ],
    "websocket": [
        "websocket.py",
        "websocket_middleware.py",
    ],
    "performance": [
        "optimized.py",
        "scheduler.py",
        "cython_ext/",
    ],
    "utils": [
        "utils.py",
        "forwarding.py",
        "worker_manager.py",
    ],
}

def organize_files():
    """Organize ProAPI files into a categorized directory structure."""
    # Check if we're in the right directory
    if not os.path.exists("proapi_backup"):
        print("Error: proapi_backup directory not found. Please run this script from the root of the ProAPI project.")
        sys.exit(1)

    # Create a new proapi directory
    if os.path.exists("proapi"):
        shutil.rmtree("proapi")
    os.makedirs("proapi")
    print("Created new proapi directory")

    # Create category directories
    for category in categories:
        os.makedirs(f"proapi/{category}", exist_ok=True)
        print(f"Created directory: proapi/{category}")

    # Copy files to their respective categories
    for category, files in categories.items():
        for file in files:
            src = f"proapi_backup/{file}"
            dst = f"proapi/{category}/{os.path.basename(file)}"

            # Handle directories
            if file.endswith('/'):
                src_dir = f"proapi_backup/{file}"
                dst_dir = f"proapi/{category}/{os.path.basename(file.rstrip('/'))}"
                if os.path.exists(src_dir):
                    shutil.copytree(src_dir, dst_dir)
                    print(f"Copied directory {src_dir} to {dst_dir}")
                else:
                    print(f"Warning: Directory {src_dir} not found")
                continue

            # Handle files
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                print(f"Copied {src} to {dst}")
            else:
                print(f"Warning: {src} not found")

    print("Organization complete!")

if __name__ == "__main__":
    organize_files()
