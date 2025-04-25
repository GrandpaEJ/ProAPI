from setuptools import setup, find_packages
from setuptools.extension import Extension

# Check if Cython is available
try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

# Get version
with open("proapi/__init__.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break

# Get long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Define extensions
ext_modules = []
if USE_CYTHON:
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

setup(
    name="proapi",
    version=version,
    description="A lightweight, beginner-friendly yet powerful Python web framework - simpler than Flask, faster than FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ProAPI Team",
    author_email="",
    url="https://github.com/GrandpaEJ/ProAPI",
    packages=find_packages(),
    package_data={
        "proapi": ["templates/*", "static/*"],
        "proapi.templates": ["templates/*"],
    },
    ext_modules=ext_modules,
    install_requires=[
        "loguru>=0.7.2",
        "uvicorn>=0.27.0",
        "jinja2>=3.1.3",
        "watchdog>=3.0.0",
        "pydantic>=2.6.0",
        "psutil>=5.9.8",  # Required for worker monitoring and resource usage tracking
        "httpx>=0.26.0",  # For HTTP client functionality
        "python-multipart>=0.0.7"  # For form data parsing
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "isort>=5.13.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0"
        ],
        "prod": [
            "gunicorn>=21.2.0",
            "python-dotenv>=1.0.0",
            "hypercorn>=0.15.0"  # Alternative ASGI server
        ],
        "cloudflare": [
            "cloudflared>=0.1.0"
        ],
        "cython": [
            "cython>=3.0.6"
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.25.2"
        ],
        "full": [
            "gunicorn>=21.2.0",
            "python-dotenv>=1.0.0",
            "cloudflared>=0.1.0",
            "cython>=3.0.6",
            "hypercorn>=0.15.0",
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "proapi=proapi.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False
)
