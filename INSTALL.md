# Installing ProAPI

This guide explains how to install ProAPI from source.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- setuptools and wheel (`pip install setuptools wheel`)

## Installation Methods

### Method 1: Using pip (Recommended)

The easiest way to install ProAPI is directly from GitHub:

```bash
pip install git+https://github.com/GrandpaEJ/ProAPI.git
```

To install a specific version:

```bash
pip install git+https://github.com/GrandpaEJ/ProAPI.git@v0.2.0
```

### Method 2: From Source

1. Clone the repository:

```bash
git clone https://github.com/GrandpaEJ/ProAPI.git
cd ProAPI
```

2. Install the package:

```bash
pip install .
```

For development installation (editable mode):

```bash
pip install -e .
```

### Method 3: Using the Build Script

We provide a build script that handles building and installing the package:

```bash
python build_and_install.py
```

## Verifying Installation

To verify that ProAPI is installed correctly, run:

```bash
python -c "import proapi; print(proapi.__version__)"
```

This should print the version number of ProAPI.

## Installing Optional Dependencies

ProAPI has several optional dependency groups:

- Development tools: `pip install proapi[dev]`
- Production extras: `pip install proapi[prod]`
- Cloudflare Tunnel support: `pip install proapi[cloudflare]`

To install all extras:

```bash
pip install proapi[dev,prod,cloudflare]
```

## Troubleshooting

If you encounter issues during installation:

1. Make sure you have the latest pip, setuptools, and wheel:

```bash
pip install --upgrade pip setuptools wheel
```

2. If you're having issues with Cython compilation, you can install without it:

```bash
pip install --no-binary :all: proapi
```

3. For Windows users, you may need Visual C++ build tools for Cython compilation:
   - Install Visual Studio with "Desktop development with C++" workload
   - Or use the pre-built wheels when available

## Uninstalling

To uninstall ProAPI:

```bash
pip uninstall proapi
```
