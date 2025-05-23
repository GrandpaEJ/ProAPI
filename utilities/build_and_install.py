#!/usr/bin/env python
"""
Build and install script for ProAPI.

This script builds and installs ProAPI using pip.
"""

import os
import sys
import subprocess
import shutil

def run_command(command):
    """Run a command and print output."""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
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

def main():
    """Main function."""
    # Parse arguments
    full_install = "--full" in sys.argv

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
    print("You can now import it in your Python code:")
    print("from proapi import ProAPI")
    print("\nExample usage:")
    print("app = ProAPI(debug=True, fast_mode=True)")
    print("app.run(port=8000)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
