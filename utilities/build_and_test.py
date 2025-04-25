#!/usr/bin/env python
"""
Build, install, and test script for ProAPI.

This script builds, installs, and tests the ProAPI package.
"""

import os
import sys
import subprocess
import shutil
import tempfile

def run_command(command, cwd=None):
    """Run a command and print output."""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        cwd=cwd
    )
    stdout, stderr = process.communicate()
    
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)
    
    return process.returncode

def clean_build_files():
    """Clean build files."""
    print("Cleaning build files...")
    
    # Remove build directories
    dirs_to_remove = [
        "build",
        "dist",
        "proapi.egg-info"
    ]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}...")
            shutil.rmtree(dir_name)

def build_package():
    """Build the package."""
    print("Building package...")
    
    # Build the package
    return run_command("python setup.py sdist bdist_wheel")

def install_package(full=False):
    """Install the package."""
    print("Installing package...")
    
    # Install the package
    if full:
        print("Installing with all features (full)...")
        return run_command("pip install --force-reinstall dist/*.whl[full]")
    else:
        return run_command("pip install --force-reinstall dist/*.whl")

def test_cli():
    """Test the CLI commands."""
    print("\nTesting CLI commands...")
    
    # Test version command
    print("\nTesting 'proapi version'...")
    run_command("proapi version")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test init command with new directory
        print(f"\nTesting 'proapi init' in {temp_dir}...")
        test_project = os.path.join(temp_dir, "test_project")
        run_command(f"proapi init {test_project}")
        
        # Check if files were created
        if os.path.exists(os.path.join(test_project, "app.py")):
            print("✓ Project initialization successful")
        else:
            print("✗ Project initialization failed")
            return False
        
        # Test init command with current directory
        print(f"\nTesting 'proapi init .' in a new directory...")
        current_test_dir = os.path.join(temp_dir, "current_test")
        os.makedirs(current_test_dir)
        run_command("proapi init .", cwd=current_test_dir)
        
        # Check if files were created
        if os.path.exists(os.path.join(current_test_dir, "app.py")):
            print("✓ Project initialization in current directory successful")
        else:
            print("✗ Project initialization in current directory failed")
            return False
    
    return True

def main():
    """Main function."""
    # Parse arguments
    full_install = "--full" in sys.argv
    skip_tests = "--skip-tests" in sys.argv
    
    # Clean build files
    clean_build_files()
    
    # Build the package
    if build_package() != 0:
        print("Error building package")
        return 1
    
    # Install the package
    if install_package(full=full_install) != 0:
        print("Error installing package")
        return 1
    
    print("\nProAPI has been successfully built and installed!")
    if full_install:
        print("Installed with all features (full)")
    
    # Run tests if not skipped
    if not skip_tests:
        if not test_cli():
            print("CLI tests failed")
            return 1
        print("\nAll tests passed!")
    
    print("\nYou can now import it in your Python code:")
    print("from proapi import ProAPI")
    print("\nExample usage:")
    print("app = ProAPI(debug=True, fast_mode=True)")
    print("app.run(port=8000)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
