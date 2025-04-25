#!/usr/bin/env python
"""
Script to upload the Gpgram package to PyPI using an API token.

Usage:
    python upload_to_pypi.py [--test] [--token TOKEN]

Options:
    --test      Upload to TestPyPI instead of PyPI
    --token     Specify the PyPI API token (if not provided, will look for environment variable)
"""

import os
import sys
import subprocess
import argparse
import shutil

def run_command(command):
    """Run a shell command and print its output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=True)
    print(f"Command completed with exit code {result.returncode}")
    return result

def clean_build_dirs():
    """Clean build directories."""
    print("Cleaning build directories...")
    dirs_to_clean = ["build", "dist", "proapi.egg-info"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}...")
            shutil.rmtree(dir_name)

def build_package():
    """Build the package."""
    print("Building package...")
    run_command("python -m build")

def check_package():
    """Check the package with twine."""
    print("Checking package...")
    run_command("python -m twine check dist/*")

def upload_to_pypi(token, test=False):
    """
    Upload the package to PyPI or TestPyPI using an API token.
    
    Args:
        token: PyPI API token
        test: Whether to upload to TestPyPI
    """
    repository = "--repository testpypi" if test else ""
    
    # Set the token as an environment variable
    os.environ["TWINE_USERNAME"] = "__token__"
    os.environ["TWINE_PASSWORD"] = token
    
    print(f"Uploading to {'TestPyPI' if test else 'PyPI'}...")
    run_command(f"python -m twine upload {repository} dist/*")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Upload Gpgram package to PyPI")
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--token", help="PyPI API token")
    args = parser.parse_args()
    
    # Determine if we're uploading to TestPyPI
    test = args.test
    
    # Get the API token
    token = args.token
    if not token:
        # Try to get the token from environment variables
        if test:
            token = os.environ.get("TEST_PYPI_API_TOKEN")
        else:
            token = os.environ.get("PYPI_API_TOKEN")
    
    if not token:
        print("Error: No API token provided. Please provide a token using --token or set the environment variable.")
        print("For PyPI: PYPI_API_TOKEN")
        print("For TestPyPI: TEST_PYPI_API_TOKEN")
        sys.exit(1)
    
    try:
        # Clean build directories
        clean_build_dirs()
        
        # Build the package
        build_package()
        
        # Check the package
        check_package()
        
        # Upload to PyPI
        upload_to_pypi(token, test=test)
        
        print("Package uploaded successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
