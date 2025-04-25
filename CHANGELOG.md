# Changelog

All notable changes to ProAPI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.3] - 2025-04-25

### Changed
- Updated WebSocket documentation with correct import paths
- Improved WebSocket examples to use built-in room management
- Enhanced WebSocket middleware documentation
- Updated reliability documentation to match current implementation
- Improved cross-referencing between documentation files

### Fixed
- Fixed import paths in WebSocket documentation
- Fixed WebSocket middleware registration examples
- Fixed reliability.md to accurately reflect available features
- Corrected examples in advanced.md for WebSocket usage
- Fixed documentation inconsistencies across multiple files

## [0.4.2] - 2025-04-25

### Added
- Added comprehensive documentation on HTML response handling
- Added examples for different HTML response methods
- Added notes about path-specific behavior for certain routes

### Changed
- Updated authentication documentation with best practices
- Improved examples for login and registration pages
- Enhanced custom response documentation

### Fixed
- Fixed HTML response handling for specific routes (e.g., "/register")
- Fixed documentation inconsistencies
- Improved error handling for HTML responses

## [0.4.1] - 2025-04-25

### Added
- Added modern packaging with pyproject.toml
- Added Cython build system integration
- Added mypy configuration

### Changed
- Updated package structure for better organization
- Moved example files to examples directory
- Moved utility scripts to utilities directory

### Fixed
- Fixed import paths for better package structure
- Fixed ASGI adapter for better compatibility with uvicorn reloader
- Fixed unexpected errors in the reloader

## [0.4.0] - 2025-04-25

### Added
- Added HTTP client functionality with httpx
- Added form data parsing with python-multipart
- Added support for Hypercorn as an alternative ASGI server
- Added Sphinx documentation support
- Added mypy for type checking in development
- Added HTTP Servers classifier
- Added Flask-like authentication system
- Added clean, organized logging system

### Changed
- Updated minimum Python version to 3.8
- Updated all dependencies to latest versions
- Improved logging system with cleaner output
- Enhanced login system with Flask-like protection
- Changed development status from Alpha to Beta
- Reorganized codebase for better maintainability

### Fixed
- Fixed ASGI compatibility issues
- Fixed event loop blocking issues
- Fixed WebSocket auto-handling
- Fixed duplicate logging issues

## [0.3.12] - 2025-04-22

### Added
- Comprehensive router testing with support for various response types
- Improved documentation for custom response handling
- Enhanced performance metrics and benchmarks

### Fixed
- Fixed JSON parsing in POST requests
- Fixed custom response handling for HTML, text, and other content types
- Improved error handling for different response types

## [0.3.11] - 2025-04-22

### Added
- Enhanced WebSocket support with improved error handling
- Fixed ASGI adapter for better WebSocket compatibility
- Comprehensive performance testing and benchmarking
- Performance documentation with RPS and response time metrics
- Loop protection system to detect and warn about event loop blocking
- Task offloading decorators: `@auto_task`, `@thread_task`, and `@process_task`

### Changed
- Improved error handling for WebSocket connections
- Enhanced multi-user request handling capabilities
- Updated documentation with performance benchmarks

### Fixed
- ASGI adapter issues with WebSocket connections
- Type conversion in route parameters
- WebSocket disconnection handling

## [0.3.0] - 2025-04-16

### Added
- Global request object for easier access to the current request
- Global session object for easier access to the current session
- Helper functions for common tasks:
  - `redirect()` for creating redirect responses
  - `jsonify()` for creating JSON responses
- Response hooks system for middleware to modify responses
- Example application demonstrating the new features

### Changed
- Updated session middleware to work with the global session object
- Improved request handling to support the global request object

## [0.2.0] - 2025-04-15

### Added
- Session management functionality
  - Memory and file-based session backends
  - Secure session cookies with configurable options
  - Session middleware for easy integration
- Enhanced cookie handling in Request and Response classes
- Comprehensive documentation for session functionality
- Example application demonstrating session usage
- Test suite for session functionality

### Changed
- Updated documentation to include session management
- Improved cookie handling in the Response class to support multiple cookies

## [0.1.2] - 2025-04-15

### Added
- WebSocket support with room management
- Fast mode with optimized request handling
- Response compression

### Fixed
- Auto-reloader issues with certain file structures
- Cookie handling in Response class

## [0.1.1] - 2025-04-14

### Added
- CLI commands for running applications
- Port forwarding support (ngrok, localtunnel, cloudflare)
- Automatic API documentation with Swagger UI

### Fixed
- Template rendering issues
- Static file handling

## [0.1.0] - 2025-04-13

### Added
- Initial release
- Decorator-based routing
- Template rendering with Jinja2
- Middleware system
- JSON support
- Logging with Loguru
