"""
Test Cython compilation of ProAPI.
"""

import os
import sys
import time

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi.cython_ext import is_cython_available, compile_module

def main():
    """Test Cython compilation."""
    print("Testing Cython compilation...")
    
    # Check if Cython is available
    if not is_cython_available():
        print("Cython is not available. Please install it with: pip install cython")
        return
    
    print("Cython is available.")
    
    # Get the path to the core_cy.pyx file
    core_cy_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'proapi', 
        'cython_ext', 
        'core_cy.pyx'
    ))
    
    print(f"Compiling {core_cy_path}...")
    
    # Compile the module
    start_time = time.time()
    success = compile_module(core_cy_path)
    end_time = time.time()
    
    if success:
        print(f"Compilation successful! Time: {end_time - start_time:.2f}s")
    else:
        print("Compilation failed.")

if __name__ == "__main__":
    main()
