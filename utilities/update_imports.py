"""
Script to update imports in ProAPI files to reflect the new directory structure.
"""

import os
import re
import sys

def update_imports():
    """Update imports in ProAPI files to reflect the new directory structure."""
    # Check if we're in the right directory
    if not os.path.exists("proapi"):
        print("Error: proapi directory not found. Please run this script from the root of the ProAPI project.")
        sys.exit(1)
    
    # Define import mappings
    import_mappings = {
        "from proapi import ": "from proapi.core import ",
        "from proapi.core import ": "from proapi.core import ",
        "from proapi.routing import ": "from proapi.routing import ",
        "from proapi.server import ": "from proapi.server import ",
        "from proapi.templates import ": "from proapi.templates import ",
        "from proapi.session import ": "from proapi.session import ",
        "from proapi.auth import ": "from proapi.auth import ",
        "from proapi.websocket import ": "from proapi.websocket import ",
        "from proapi.performance import ": "from proapi.performance import ",
        "from proapi.utils import ": "from proapi.utils import ",
        
        # Direct imports
        "from proapi.core.core import ": "from proapi.core.core import ",
        "from proapi.core.cli import ": "from proapi.core.cli import ",
        "from proapi.core.logging import ": "from proapi.core.logging import ",
        "from proapi.core.run import ": "from proapi.core.run import ",
        "from proapi.core.docs import ": "from proapi.core.docs import ",
        "from proapi.core.swagger_ui import ": "from proapi.core.swagger_ui import ",
        
        # Old imports to new imports
        "from proapi.routing import ": "from proapi.routing.routing import ",
        "from proapi.request_proxy import ": "from proapi.routing.request_proxy import ",
        "from proapi.middleware import ": "from proapi.routing.middleware import ",
        "from proapi.server import ": "from proapi.server.server import ",
        "from proapi.asgi.asgi import ": "from proapi.server.asgi import ",
        "from proapi.asgi.asgi_adapter import ": "from proapi.server.asgi_adapter import ",
        "from proapi.asgi.asgi_adapter_fix import ": "from proapi.server.asgi_adapter_fix import ",
        "from proapi.templating import ": "from proapi.templates.templating import ",
        "from proapi.session.session import ": "from proapi.session.session import ",
        "from proapi.session.session_proxy import ": "from proapi.session.session_proxy import ",
        "from proapi.login import ": "from proapi.auth.login import ",
        "from proapi.websocket import ": "from proapi.websocket.websocket import ",
        "from proapi.websocket_middleware import ": "from proapi.websocket.websocket_middleware import ",
        "from proapi.optimized import ": "from proapi.performance.optimized import ",
        "from proapi.scheduler import ": "from proapi.performance.scheduler import ",
        "from proapi.utils import ": "from proapi.utils.utils import ",
        "from proapi.forwarding import ": "from proapi.utils.forwarding import ",
        "from proapi.worker_manager import ": "from proapi.utils.worker_manager import ",
    }
    
    # Walk through all Python files in the proapi directory
    for root, dirs, files in os.walk("proapi"):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                update_imports_in_file(file_path, import_mappings)
    
    print("Import updates complete!")

def update_imports_in_file(file_path, import_mappings):
    """Update imports in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Apply import mappings
    for old_import, new_import in import_mappings.items():
        content = content.replace(old_import, new_import)
    
    # Write updated content back to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Updated imports in {file_path}")

if __name__ == "__main__":
    update_imports()
