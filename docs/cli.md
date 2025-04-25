# Command-Line Interface (CLI) in ProAPI

ProAPI includes a powerful command-line interface (CLI) for common tasks like running applications and initializing new projects. This guide explains how to use the CLI.

## Basic Usage

The CLI is available through the `proapi` command or the `proapi` module:

```bash
# Using the command directly
proapi [command] [options]

# Using the Python module
python -m proapi [command] [options]
```

## Getting Help

To see all available commands and options:

```bash
proapi --help
```

To get help for a specific command:

```bash
proapi run --help
proapi init --help
```

## Available Commands

### Run Command

Run a ProAPI application:

```bash
proapi run app.py
```

#### Options

- `--host`: Host to bind to (default: 127.0.0.1)
  - Use `--host=local` for 127.0.0.1
  - Use `--host=all` or `--host=0.0.0.0` for all interfaces
- `--port`: Port to bind to (default: 8000)
- `--debug`: Enable debug mode for detailed error messages
- `--reload`: Enable auto-reload when code changes
- `--workers`: Number of worker processes (default: 1, production: 2+)
- `--fast`: Enable fast mode with optimized request handling for better performance
- `--forward`: Enable Cloudflare port forwarding to expose the app to the internet
- `--cf-token`: Cloudflare Tunnel token for authenticated tunnels

#### Examples

Run an application in debug mode:

```bash
proapi run app.py --debug
```

Run an application with auto-reload:

```bash
proapi run app.py --reload
```

Run an application on a specific host and port:

```bash
proapi run app.py --host=0.0.0.0 --port=5000
```

Run an application with multiple workers:

```bash
proapi run app.py --workers=4
```

Run an application with fast mode for better performance:

```bash
proapi run app.py --fast
```

Run an application with Cloudflare port forwarding:

```bash
proapi run app.py --forward
```

Run a specific app instance from a module:

```bash
proapi run mymodule:app
```

### Init Command

Initialize a new ProAPI project:

```bash
# Initialize in a new directory
proapi init myproject

# Initialize in the current directory
proapi init .
```

#### Options

- `--template`: Project template to use (default: basic)
  - `basic`: Simple app with basic routes
  - `api`: REST API with modular structure and example endpoints
  - `web`: Web application with Jinja2 templates and static files

#### Examples

Initialize a basic project in a new directory:

```bash
proapi init myproject
```

Initialize a project in the current directory:

```bash
proapi init .
```

Initialize an API project:

```bash
proapi init myapi --template api
```

Initialize a web project:

```bash
proapi init myweb --template web
```

### Version Command

Show version information and check dependencies:

```bash
# Using the version command
proapi version

# Using the shorthand flag
proapi -v
```

This will display:
- ProAPI version
- Python version
- Platform information
- Status of optional dependencies (Cython, Cloudflared, Uvicorn, Jinja2, Loguru)

## Global Options

- `-c`, `--compile`: Compile with Cython before running (requires proapi[cython])
- `-v`, `--version`: Show version information and exit

## Specifying the Application Instance

By default, the CLI looks for the first ProAPI instance in the specified module. You can specify a particular instance using the `module:instance` syntax:

```bash
python -m proapi run app:api
```

This will run the `api` instance from the `app` module.

## Project Templates

ProAPI provides three project templates to help you get started quickly.

### Basic Template

A simple application with basic routes. Ideal for small projects or learning ProAPI.

The basic template includes:

- `app.py`: Simple application with example routes
  - GET / - Returns a greeting message
  - GET /hello/{name} - Returns a personalized greeting
  - POST /echo - Echoes the JSON request body
- `README.md`: Basic documentation with usage instructions

### API Template

A REST API with modular structure and example endpoints. Ideal for building APIs.

The API template includes:

- `app.py`: Main application file with fast mode enabled
- `routes/`: Directory for route modules
  - `users.py`: User routes (GET, POST, etc.)
  - `items.py`: Item routes (GET, POST, etc.)
- `models/`: Directory for data models
- `README.md`: API documentation with endpoint descriptions

### Web Template

A web application with Jinja2 templates and static files. Ideal for building websites.

The web template includes:

- `app.py`: Main application file
- `templates/`: Directory for HTML templates
  - `base.html`: Base template with common layout
  - `index.html`: Home page template
  - `about.html`: About page template
  - `contact.html`: Contact form template
  - `contact_success.html`: Contact form success page
- `static/`: Directory for static files
  - `css/`: CSS files with basic styling
  - `js/`: JavaScript files with basic functionality
- `README.md`: Web application documentation

## Compiling with Cython

You can compile your application with Cython for improved performance:

```bash
# Using the -c flag
proapi -c run app.py

# Or with the full option
proapi --compile run app.py
```

This requires the Cython extra to be installed:

```bash
pip install proapi[cython]
```

Or you can install Cython directly:

```bash
pip install cython
```

> **Note:** Cython compilation requires a C compiler and development tools to be installed on your system. On Windows, you'll need Visual Studio with C++ development tools. On Linux, you'll need gcc and Python development headers.

## Environment Variables

The CLI respects the following environment variables:

- `PROAPI_HOST`: Default host to bind to
- `PROAPI_PORT`: Default port to bind to
- `PROAPI_DEBUG`: Enable debug mode (1 or 0)
- `PROAPI_ENV`: Environment (development, production, or testing)

## Exit Codes

The CLI uses the following exit codes:

- 0: Success
- 1: General error
- 2: Invalid arguments
- 3: Application error