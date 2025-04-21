"""
Example of Python version compatibility check.
"""

import sys
import platform

def main():
    """Check Python version compatibility."""
    print(f"Python version: {platform.python_version()}")
    print(f"Python implementation: {platform.python_implementation()}")
    print(f"System: {platform.system()} {platform.release()}")
    print()
    
    # Check if Python version is compatible
    if sys.version_info < (3, 7):
        print("ProAPI requires Python 3.7 or higher.")
        print("Your Python version is not compatible.")
        return
    
    print("Your Python version is compatible with ProAPI.")
    print()
    
    # Check for optimal features
    if sys.version_info >= (3, 8):
        print("Python 3.8+ features available:")
        print("- Assignment expressions (walrus operator)")
        print("- Positional-only parameters")
        print("- f-strings with = specifier (Python 3.8+)")
    
    if sys.version_info >= (3, 9):
        print("\nPython 3.9+ features available:")
        print("- Dictionary union operators")
        print("- Type hinting generics in standard collections")
    
    if sys.version_info >= (3, 10):
        print("\nPython 3.10+ features available:")
        print("- Structural pattern matching")
        print("- Parenthesized context managers")
    
    if sys.version_info >= (3, 11):
        print("\nPython 3.11+ features available:")
        print("- Exception groups")
        print("- Improved error messages")
        print("- Performance improvements")
    
    if sys.version_info >= (3, 12):
        print("\nPython 3.12+ features available:")
        print("- Type parameter syntax")
        print("- f-string parsing improvements")
    
    if sys.version_info >= (3, 13):
        print("\nPython 3.13+ features available:")
        print("- Latest Python features")
        print("- Performance improvements")

if __name__ == "__main__":
    main()
