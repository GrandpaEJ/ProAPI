# Command-Line Interface (CLI) in ProAPI

ProAPI includes a command-line interface (CLI) for common tasks like running applications and creating new projects. This guide explains how to use the CLI.

## Basic Usage

The CLI is available through the `proapi` module:

```bash
python -m proapi [command] [options]
```

## Available Commands

### Run Command

Run a ProAPI application:

```bash
python -m proapi run app.py
```

#### Options

- `--host`: Host to bind to (default: 127.0.0.1)
  - Use `--host=local` for 127.0.0.1
  - Use `--host=all` or `--host=0.0.0.0` for all interfaces
- `--port`: Port to bind to (default: 8000)
- `--debug`: Enable debug mode
- `--reload`: Enable auto-reload (requires uvicorn)
- `--workers`: Number of worker processes (default: 1)
- `--server`: Server type (default, multiworker)
- `--forward`: Enable port forwarding to expose the app to the internet
- `--forward-type`: Port forwarding service to use (ngrok, cloudflare, or localtunnel)
- `--cf-token`: Cloudflare Tunnel token (for authenticated tunnels)

#### Examples

Run an application in debug mode:

```bash
python -m proapi run app.py --debug
```

Run an application with auto-reload:

```bash
python -m proapi run app.py --reload
```

Run an application on a specific host and port:

```bash
python -m proapi run app.py --host=0.0.0.0 --port=5000
```

Run an application with multiple workers:

```bash
python -m proapi run app.py --workers=4
```

Run an application with port forwarding:

```bash
python -m proapi run app.py --forward
```

### Create Command

Create a new ProAPI project:

```bash
python -m proapi create myproject
```

#### Options

- `--template`: Project template (default: basic)
  - `basic`: Simple application with a few routes
  - `api`: API-focused application with route modules
  - `web`: Web application with templates and static files

#### Examples

Create a basic project:

```bash
python -m proapi create myproject
```

Create an API project:

```bash
python -m proapi create myapi --template=api
```

Create a web project:

```bash
python -m proapi create myweb --template=web
```

### Version Command

Show version information:

```bash
python -m proapi version
```

## Global Options

- `-c`, `--compile`: Compile with Cython before running

## Specifying the Application Instance

By default, the CLI looks for the first ProAPI instance in the specified module. You can specify a particular instance using the `module:instance` syntax:

```bash
python -m proapi run app:api
```

This will run the `api` instance from the `app` module.

## Project Templates

### Basic Template

The basic template includes:

- `app.py`: Simple application with a few routes
- `README.md`: Basic documentation

### API Template

The API template includes:

- `app.py`: Main application file
- `routes/`: Directory for route modules
  - `users.py`: User routes
  - `items.py`: Item routes
- `models/`: Directory for data models
- `README.md`: API documentation

### Web Template

The web template includes:

- `app.py`: Main application file
- `routes/`: Directory for route modules
- `templates/`: Directory for HTML templates
- `static/`: Directory for static files
  - `css/`: CSS files
  - `js/`: JavaScript files
  - `img/`: Image files
- `README.md`: Web application documentation

## Compiling with Cython

You can compile your application with Cython for improved performance:

```bash
python -m proapi run app.py --compile
```

This requires Cython to be installed:

```bash
pip install cython
```

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