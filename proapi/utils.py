"""
Utility functions for ProAPI framework.
"""

import inspect
import json
import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Union

def json_response(data, status=200, headers=None):
    """
    Create a JSON response.
    
    Args:
        data: Data to serialize to JSON
        status: HTTP status code
        headers: Additional headers
        
    Returns:
        Response object
    """
    from .server import Response
    
    headers = headers or {}
    
    return Response(
        body=json.dumps(data),
        status=status,
        headers=headers,
        content_type="application/json"
    )

def redirect(url, status=302, headers=None):
    """
    Create a redirect response.
    
    Args:
        url: URL to redirect to
        status: HTTP status code (301, 302, 303, 307, 308)
        headers: Additional headers
        
    Returns:
        Response object
    """
    from .server import Response
    
    headers = headers or {}
    headers['Location'] = url
    
    return Response(
        body=f'<html><body>Redirecting to <a href="{url}">{url}</a></body></html>',
        status=status,
        headers=headers
    )

def static_file(file_path, content_type=None, download_name=None):
    """
    Serve a static file.
    
    Args:
        file_path: Path to the file
        content_type: Content type (guessed if not provided)
        download_name: Filename for download (if provided, adds Content-Disposition header)
        
    Returns:
        Response object
    """
    from .server import Response
    import mimetypes
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        return Response(
            body=json.dumps({"error": "File not found"}),
            status=404,
            content_type="application/json"
        )
    
    # Guess content type if not provided
    if content_type is None:
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"
    
    # Read the file
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Create headers
    headers = {}
    if download_name:
        headers['Content-Disposition'] = f'attachment; filename="{download_name}"'
    
    # Return the response
    return Response(
        body=content,
        headers=headers,
        content_type=content_type
    )

def parse_form_data(request):
    """
    Parse multipart form data from a request.
    
    Args:
        request: Request object
        
    Returns:
        Tuple of (fields, files)
    """
    # Check if the content type is multipart/form-data
    content_type = request.headers.get('Content-Type', '')
    if not content_type.startswith('multipart/form-data'):
        return {}, {}
    
    try:
        import cgi
        from io import BytesIO
        
        # Create a file-like object from the request body
        environ = {
            'REQUEST_METHOD': request.method,
            'CONTENT_TYPE': content_type,
            'CONTENT_LENGTH': str(len(request.body))
        }
        
        # Parse the form data
        form = cgi.FieldStorage(
            fp=BytesIO(request.body),
            environ=environ,
            keep_blank_values=True
        )
        
        # Extract fields and files
        fields = {}
        files = {}
        
        for key in form.keys():
            item = form[key]
            
            if isinstance(item, list):
                # Handle multiple values
                if item[0].filename:
                    files[key] = [f for f in item]
                else:
                    fields[key] = [f.value for f in item]
            elif item.filename:
                # Handle file upload
                files[key] = item
            else:
                # Handle regular field
                fields[key] = item.value
        
        return fields, files
    
    except ImportError:
        # cgi module not available
        return {}, {}

def is_async_callable(obj):
    """
    Check if an object is an async callable.
    
    Args:
        obj: Object to check
        
    Returns:
        True if the object is an async callable, False otherwise
    """
    return inspect.iscoroutinefunction(obj) or (
        hasattr(obj, '__call__') and inspect.iscoroutinefunction(obj.__call__)
    )

def run_async(func, *args, **kwargs):
    """
    Run an async function in a synchronous context.
    
    Args:
        func: Async function
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Function result
    """
    import asyncio
    
    # Get or create an event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run the function
    return loop.run_until_complete(func(*args, **kwargs))
