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
        module = importlib.import_module(app_module)
        proapi_app = getattr(module, app_var)
        
        # Import the ASGIAdapter
        from proapi.server.asgi_adapter_fix import ASGIAdapter
        app = ASGIAdapter(proapi_app)
        
        return True
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
    
    if app is None:
        # Return a 500 error if app is not set
        await send({
            "type": "http.response.start",
            "status": 500,
            "headers": [(b"content-type", b"application/json")]
        })
        await send({
            "type": "http.response.body",
            "body": json.dumps({"error": "ASGI app not initialized"}).encode("utf-8")
        })
        return
    
    # Call the app
    await app(scope, receive, send)
