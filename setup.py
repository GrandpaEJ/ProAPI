from setuptools import setup, find_packages
from setuptools.extension import Extension

# Check if Cython is available
try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

# Get version
with open("proapi/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break

# Get long description
with open("README.md", "r") as f:
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
    ext_modules=ext_modules,
    install_requires=[
        "loguru>=0.7.0",
        "uvicorn>=0.23.0",
        "jinja2>=3.0.0",
        "watchdog>=3.0.0",
        "pydantic>=2.0.0",
        "psutil>=5.9.0"  # Required for worker monitoring and resource usage tracking
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0"
        ],
        "prod": [
            "gunicorn>=21.0.0",
            "python-dotenv>=1.0.0"
        ],
        "cloudflare": [
            "cloudflared>=0.1.0"
        ],
        "cython": [
            "cython>=0.29.0"
        ],
        "full": [
            "gunicorn>=21.0.0",
            "python-dotenv>=1.0.0",
            "cloudflared>=0.1.0",
            "cython>=0.29.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "proapi=proapi.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False
)
