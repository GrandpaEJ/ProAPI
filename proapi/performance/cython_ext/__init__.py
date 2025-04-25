"""
Cython extensions for ProAPI framework.
"""

import os
import sys
from typing import Any, Dict, List, Optional, Union

# Flag to track if Cython is available
_has_cython = False

try:
    import Cython
    _has_cython = True
except ImportError:
    pass

def is_cython_available():
    """
    Check if Cython is available.
    
    Returns:
        True if Cython is available, False otherwise
    """
    return _has_cython

def compile_module(module_path):
    """
    Compile a module with Cython.
    
    Args:
        module_path: Path to the module
        
    Returns:
        True if compilation was successful, False otherwise
    """
    if not _has_cython:
        return False
    
    try:
        from Cython.Build import cythonize
        from setuptools import setup, Extension
        
        # Compile the module
        ext_modules = cythonize([module_path])
        setup(
            ext_modules=ext_modules,
            script_args=['build_ext', '--inplace']
        )
        
        return True
    except Exception:
        return False
