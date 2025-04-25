"""
This setup.py file is maintained for backward compatibility.
The actual package configuration is in pyproject.toml.
"""

import sys
from setuptools import setup
from setuptools.extension import Extension

# Check if Cython is available
try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

# Define extensions
ext_modules = []
# Only try to build Cython extensions if explicitly requested
if USE_CYTHON and 'build_ext' in sys.argv:
    try:
        ext_modules = cythonize([
            Extension(
                "proapi.cython_ext.core_cy",
                ["proapi/cython_ext/core_cy.pyx"],
                language="c",
                extra_compile_args=["-O3"]
            )
        ], compiler_directives={
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'initializedcheck': False
        })
    except Exception as e:
        print(f"Warning: Cython compilation failed: {e}")
        print("Falling back to pure Python implementation")

# Setup with minimal configuration, deferring to pyproject.toml
setup(
    ext_modules=ext_modules,
)
