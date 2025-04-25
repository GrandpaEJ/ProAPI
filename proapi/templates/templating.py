"""
Templating module for ProAPI framework.

Provides Jinja2 template rendering functionality.
"""

import os
from typing import Any, Dict, Optional, Union

# Flag to track if Jinja2 is available
_has_jinja2 = False

try:
    import jinja2
    _has_jinja2 = True
except ImportError:
    pass

# Global Jinja2 environment
_jinja_env = None

def setup_jinja(template_dir: str = "templates") -> Optional[Any]:
    """
    Set up the Jinja2 environment.
    
    Args:
        template_dir: Directory containing templates
        
    Returns:
        Jinja2 Environment or None if Jinja2 is not available
    """
    global _jinja_env
    
    if not _has_jinja2:
        return None
    
    # Create absolute path if template_dir is relative
    if not os.path.isabs(template_dir):
        # Try to find the template directory relative to the calling module
        import inspect
        caller_frame = inspect.currentframe().f_back
        caller_file = caller_frame.f_globals.get('__file__')
        if caller_file:
            base_dir = os.path.dirname(os.path.abspath(caller_file))
            template_dir = os.path.join(base_dir, template_dir)
    
    # Create the template directory if it doesn't exist
    os.makedirs(template_dir, exist_ok=True)
    
    # Set up Jinja2 environment
    _jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Add custom filters
    _jinja_env.filters['json'] = lambda obj: jinja2.Markup(
        json.dumps(obj, ensure_ascii=False)
    )
    
    return _jinja_env

def render(template_name: str, **context) -> str:
    """
    Render a template with the given context.
    
    Args:
        template_name: Name of the template file
        **context: Variables to pass to the template
        
    Returns:
        Rendered template as a string
        
    Raises:
        ImportError: If Jinja2 is not installed
        jinja2.exceptions.TemplateError: If there's an error in the template
    """
    if not _has_jinja2:
        raise ImportError(
            "Jinja2 is required for template rendering. "
            "Install it with: pip install jinja2"
        )
    
    global _jinja_env
    
    # If Jinja environment is not set up, set it up with default settings
    if _jinja_env is None:
        setup_jinja()
    
    # Render the template
    template = _jinja_env.get_template(template_name)
    return template.render(**context)

# Simple template rendering fallback when Jinja2 is not available
def simple_render(template_str: str, **context) -> str:
    """
    Simple template rendering without Jinja2.
    
    Only supports basic variable substitution with {{ var }}.
    
    Args:
        template_str: Template string
        **context: Variables to substitute
        
    Returns:
        Rendered string
    """
    result = template_str
    for key, value in context.items():
        result = result.replace('{{' + key + '}}', str(value))
        result = result.replace('{{ ' + key + ' }}', str(value))
    
    return result
