"""
ASGI application module for ProAPI.

This module provides a standalone ASGI application for ProAPI.
"""

import json
import traceback
import importlib
import sys
import os

# Create a global app variable for uvicorn to import
app = None
proapi_app = None

def init_app(app_module, app_var):
    """
    Initialize the ASGI application.
    
    Args:
        app_module: Module name containing the ProAPI application
        app_var: Variable name of the ProAPI application
    """
    global app, proapi_app
    
    # Import the module
    try:
        # Import the ASGIAdapter first to avoid circular imports
        from proapi.server.asgi_adapter_fix import ASGIAdapter
        
        # Use a more robust import approach to avoid circular imports
        import sys
        import importlib.util
        
        # Check if the module is already in sys.modules
        if app_module in sys.modules:
            module = sys.modules[app_module]
        else:
            # Import the module
            module = importlib.import_module(app_module)
        
        # Check if the app variable exists in the module
        if hasattr(module, app_var):
            proapi_app = getattr(module, app_var)
            app = ASGIAdapter(proapi_app)
            return True
        else:
            print(f"Error: Module '{app_module}' has no attribute '{app_var}'")
            return False
    except Exception as e:
        print(f"Error initializing ASGI app: {e}")
        traceback.print_exc()
        return False

async def __call__(scope, receive, send):
    """
    ASGI application callable.
    
    Args:
        scope: ASGI scope
        receive: ASGI receive function
        send: ASGI send function
    """
    global app
    
    # Try to initialize the app if it's not set yet
    # This helps with circular imports where the app might not be initialized yet
    if app is None:
        # Check if we can find the app in the caller's module
        import inspect
        import sys
        
        # Try to find the app in the caller's module
        frame = inspect.currentframe()
        if frame:
            caller_frame = frame.f_back
            if caller_frame:
                caller_globals = caller_frame.f_globals
                # Look for a variable that might be the app
                for var_name, var_val in caller_globals.items():
                    if var_name == 'app' and var_val is not None:
                        # Try to initialize with this app
                        try:
                            from proapi.server.asgi_adapter_fix import ASGIAdapter
                            app = ASGIAdapter(var_val)
                            print(f"Auto-initialized app from caller's module")
                            break
                        except Exception as e:
                            print(f"Failed to auto-initialize app: {e}")
        
        # If app is still None, return an error
        if app is None:
            # Return a 500 error if app is not set
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"application/json")]
            })
            await send({
                "type": "http.response.body",
                "body": json.dumps({
                    "error": "ASGI app not initialized",
                    "hint": "This might be due to a circular import. Make sure your app is defined before importing ASGI modules."
                }).encode("utf-8")
            })
            return
    
    # Call the app
    await app(scope, receive, send)
