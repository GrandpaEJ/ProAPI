"""
Command-line interface for ProAPI framework.
"""

import argparse
import importlib.util
import os
import sys
from typing import Any, Optional

from .logging import app_logger

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="ProAPI command-line interface")

    # Add global options
    parser.add_argument("-c", "--compile", action="store_true", help="Compile with Cython before running")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a ProAPI application")
    run_parser.add_argument("app", help="Application module or file, optionally with app instance (module:app)")
    run_parser.add_argument("--host", default="127.0.0.1",
                          help="Host to bind to (use 'local' for 127.0.0.1 or 'all' for 0.0.0.0)")
    run_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    run_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    run_parser.add_argument("--reload", action="store_true", help="Enable auto-reload (requires uvicorn)")
    run_parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    run_parser.add_argument("--server", default="default", help="Server type (default, multiworker)")
    run_parser.add_argument("--forward", action="store_true", help="Enable port forwarding to expose the app to the internet")
    run_parser.add_argument("--forward-type", default="ngrok", choices=["ngrok", "cloudflare", "localtunnel"],
                          help="Port forwarding service to use (ngrok, cloudflare, or localtunnel)")
    run_parser.add_argument("--cf-token", help="Cloudflare Tunnel token (for authenticated tunnels)")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new ProAPI project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("--template", default="basic", help="Project template")

    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "run":
        run_command(args)
    elif args.command == "create":
        create_command(args)
    elif args.command == "version":
        version_command()
    else:
        parser.print_help()

def run_command(args):
    """Run a ProAPI application"""
    # Get the module path (without the app instance name)
    module_path = args.app.split(':')[0] if ':' in args.app else args.app

    # Compile with Cython if requested
    if hasattr(args, 'compile') and args.compile:
        try:
            app_logger.info(f"Compiling {module_path} before running...")
            compile_app(module_path)
            app_logger.success(f"Compilation complete.")
        except Exception as e:
            app_logger.error(f"Error compiling application: {e}")
            return

    # Process host parameter
    if args.host == 'local':
        host = '127.0.0.1'
    elif args.host == 'all' or args.host == '0.0.0.0':
        host = '0.0.0.0'
    else:
        host = args.host

    # Load the application
    app_instance = load_app(args.app)
    if not app_instance:
        app_logger.error(f"Could not load application from {args.app}")
        return

    # Set debug mode
    if hasattr(app_instance, 'debug'):
        app_instance.debug = args.debug

    # Set reloader option based on CLI argument
    if hasattr(app_instance, 'use_reloader'):
        app_instance.use_reloader = args.reload

    # Run the application
    try:
        app_logger.info(f"Starting server at http://{host}:{args.port}")
        app_logger.info(f"App: {args.app}")
        app_logger.info(f"Debug mode: {'ON' if args.debug else 'OFF'}")
        app_logger.info(f"Press Ctrl+C to stop the server")

        # Also print to console
        print(f"Starting server at http://{host}:{args.port}")
        print(f"App: {args.app}")
        print(f"Debug mode: {'ON' if args.debug else 'OFF'}")
        print(f"Press Ctrl+C to stop the server")

        # Prepare forwarding kwargs
        forward_kwargs = {}
        if args.forward_type == "cloudflare" and hasattr(args, 'cf_token') and args.cf_token:
            forward_kwargs['token'] = args.cf_token

        app_instance.run(
            host=host,
            port=args.port,
            server_type=args.server,
            workers=args.workers,
            forward=args.forward,
            forward_type=args.forward_type,
            forward_kwargs=forward_kwargs,
            use_reloader=args.reload
        )
    except KeyboardInterrupt:
        app_logger.info("Server stopped")
        print("\nServer stopped")
    finally:
        pass  # No need to clean up the reloader here, it's handled by the ProAPI class

def create_command(args):
    """Create a new ProAPI project"""
    project_name = args.name
    template = args.template

    # Create project directory
    if os.path.exists(project_name):
        app_logger.error(f"Directory {project_name} already exists")
        print(f"Error: Directory {project_name} already exists")
        return

    os.makedirs(project_name)

    # Create project files based on template
    if template == "basic":
        create_basic_template(project_name)
    elif template == "api":
        create_api_template(project_name)
    elif template == "web":
        create_web_template(project_name)
    else:
        app_logger.error(f"Unknown template {template}")
        print(f"Error: Unknown template {template}")
        return

    app_logger.success(f"Project {project_name} created successfully")
    app_logger.info(f"To run the project: cd {project_name} && python -m proapi run app.py")

    print(f"Project {project_name} created successfully")
    print(f"To run the project: cd {project_name} && python -m proapi run app.py")

def version_command():
    """Show version information"""
    from . import __version__
    app_logger.info(f"ProAPI version {__version__}")
    app_logger.info(f"Python version: {sys.version}")

    print(f"ProAPI version {__version__}")
    print("Python version:", sys.version)

def load_app(app_path):
    """
    Load a ProAPI application from a module or file.

    Args:
        app_path: Path to the application module or file, optionally with app instance (module:app)

    Returns:
        ProAPI application instance or None if not found
    """
    from .core import ProAPI

    # Check if app_path includes a specific app instance
    module_path = app_path
    app_instance_name = None

    if ':' in app_path:
        module_path, app_instance_name = app_path.split(':', 1)

    # Check if the path is a file
    if os.path.isfile(module_path):
        # Load the module from the file
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        # Try to import the module
        try:
            module = importlib.import_module(module_path)
        except ImportError:
            return None

    # If a specific app instance was specified, try to get it
    if app_instance_name:
        if hasattr(module, app_instance_name):
            attr = getattr(module, app_instance_name)
            if isinstance(attr, ProAPI):
                return attr
            else:
                print(f"Error: {app_instance_name} is not a ProAPI instance")
                return None
        else:
            print(f"Error: Could not find {app_instance_name} in {module_path}")
            return None

    # Otherwise, find the first ProAPI instance
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, ProAPI):
            return attr

    return None

def compile_app(app_path):
    """
    Compile a ProAPI application with Cython.

    Args:
        app_path: Path to the application module or file

    Raises:
        ImportError: If Cython is not installed
        Exception: If compilation fails
    """
    try:
        import Cython.Build
        from Cython.Compiler import Options
        from setuptools import setup, Extension
    except ImportError:
        raise ImportError("Cython is required for compilation. Install with: pip install cython")

    # Set Cython compiler options
    Options.annotate = True

    # Check if the file exists
    if not os.path.exists(app_path):
        raise FileNotFoundError(f"File not found: {app_path}")

    # Create a temporary setup.py file
    setup_py = """
from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize([
        "{app_path}"
    ], compiler_directives={{
        'language_level': 3,
        'boundscheck': False,
        'wraparound': False,
        'initializedcheck': False
    }})
)
""".format(app_path=app_path)

    with open("setup_temp.py", "w") as f:
        f.write(setup_py)

    # Run the setup.py file
    try:
        # Save original argv
        original_argv = sys.argv.copy()

        # Set new argv for setup
        sys.argv = ["setup_temp.py", "build_ext", "--inplace"]

        # Execute setup
        exec(setup_py, globals(), locals())
        print(f"Successfully compiled {app_path}")

        # Restore original argv
        sys.argv = original_argv
    except Exception as e:
        print(f"Compilation error: {e}")
        raise
    finally:
        # Clean up
        if os.path.exists("setup_temp.py"):
            os.remove("setup_temp.py")

def create_basic_template(project_name):
    """
    Create a basic project template.

    Args:
        project_name: Project name
    """
    # Create app.py
    app_py = """from proapi import ProAPI

app = ProAPI(debug=True)

@app.get("/")
def index():
    return {"message": "Hello, World!"}

@app.get("/hello/{name}")
def hello(name):
    return {"message": f"Hello, {name}!"}

@app.post("/echo")
def echo(request):
    return request.json

if __name__ == "__main__":
    app.run()
"""

    with open(os.path.join(project_name, "app.py"), "w") as f:
        f.write(app_py)

    # Create README.md
    readme_md = f"""# {project_name}

A ProAPI project.

## Running the application

```bash
python -m proapi run app.py
```

Or:

```bash
python app.py
```

## API Endpoints

- GET / - Returns a greeting message
- GET /hello/{{name}} - Returns a personalized greeting
- POST /echo - Echoes the JSON request body
"""

    with open(os.path.join(project_name, "README.md"), "w") as f:
        f.write(readme_md)

def create_api_template(project_name):
    """
    Create an API project template.

    Args:
        project_name: Project name
    """
    # Create directories
    os.makedirs(os.path.join(project_name, "routes"))
    os.makedirs(os.path.join(project_name, "models"))

    # Create app.py
    app_py = """from proapi import ProAPI

app = ProAPI(debug=True)

# Import routes
from routes import users, items

# Register routes
app.use(users.router)
app.use(items.router)

@app.get("/")
def index():
    return {"message": "API is running"}

if __name__ == "__main__":
    app.run()
"""

    with open(os.path.join(project_name, "app.py"), "w") as f:
        f.write(app_py)

    # Create routes/users.py
    users_py = """from proapi import ProAPI

router = ProAPI()

@router.get("/users")
def get_users():
    return {"users": [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Smith"}
    ]}

@router.get("/users/{user_id:int}")
def get_user(user_id):
    return {"id": user_id, "name": f"User {user_id}"}

@router.post("/users")
def create_user(request):
    user_data = request.json
    return {"id": 3, **user_data}
"""

    with open(os.path.join(project_name, "routes", "users.py"), "w") as f:
        f.write(users_py)

    # Create routes/items.py
    items_py = """from proapi import ProAPI

router = ProAPI()

@router.get("/items")
def get_items():
    return {"items": [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"}
    ]}

@router.get("/items/{item_id:int}")
def get_item(item_id):
    return {"id": item_id, "name": f"Item {item_id}"}

@router.post("/items")
def create_item(request):
    item_data = request.json
    return {"id": 3, **item_data}
"""

    with open(os.path.join(project_name, "routes", "items.py"), "w") as f:
        f.write(items_py)

    # Create routes/__init__.py
    with open(os.path.join(project_name, "routes", "__init__.py"), "w") as f:
        f.write("")

    # Create models/__init__.py
    with open(os.path.join(project_name, "models", "__init__.py"), "w") as f:
        f.write("")

    # Create README.md
    readme_md = f"""# {project_name}

A ProAPI API project.

## Running the application

```bash
python -m proapi run app.py
```

## API Endpoints

- GET / - API status
- GET /users - List users
- GET /users/{id} - Get user by ID
- POST /users - Create a new user
- GET /items - List items
- GET /items/{id} - Get item by ID
- POST /items - Create a new item
"""

    with open(os.path.join(project_name, "README.md"), "w") as f:
        f.write(readme_md)

def create_web_template(project_name):
    """
    Create a web project template.

    Args:
        project_name: Project name
    """
    # Create directories
    os.makedirs(os.path.join(project_name, "templates"))
    os.makedirs(os.path.join(project_name, "static", "css"))
    os.makedirs(os.path.join(project_name, "static", "js"))

    # Create app.py
    app_py = """from proapi import ProAPI, render

app = ProAPI(debug=True)

@app.get("/")
def index():
    return render("index.html", title="Home", message="Welcome to ProAPI!")

@app.get("/about")
def about():
    return render("about.html", title="About")

@app.get("/contact")
def contact():
    return render("contact.html", title="Contact")

@app.post("/contact")
def submit_contact(request):
    form_data = request.form
    return render("contact_success.html",
                  title="Thank You",
                  name=form_data.get("name", ""))

if __name__ == "__main__":
    app.run()
"""

    with open(os.path.join(project_name, "app.py"), "w") as f:
        f.write(app_py)

    # Create templates/base.html
    base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - My ProAPI Website</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>&copy; 2023 My ProAPI Website</p>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>
"""

    with open(os.path.join(project_name, "templates", "base.html"), "w") as f:
        f.write(base_html)

    # Create templates/index.html
    index_html = """{% extends "base.html" %}

{% block content %}
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
    <p>This is a simple website built with ProAPI.</p>
{% endblock %}
"""

    with open(os.path.join(project_name, "templates", "index.html"), "w") as f:
        f.write(index_html)

    # Create templates/about.html
    about_html = """{% extends "base.html" %}

{% block content %}
    <h1>{{ title }}</h1>
    <p>This is the about page.</p>
    <p>ProAPI is a lightweight, beginner-friendly yet powerful Python web framework.</p>
{% endblock %}
"""

    with open(os.path.join(project_name, "templates", "about.html"), "w") as f:
        f.write(about_html)

    # Create templates/contact.html
    contact_html = """{% extends "base.html" %}

{% block content %}
    <h1>{{ title }}</h1>
    <p>Get in touch with us!</p>

    <form action="/contact" method="post">
        <div>
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>
        </div>
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="message">Message:</label>
            <textarea id="message" name="message" rows="5" required></textarea>
        </div>
        <div>
            <button type="submit">Send</button>
        </div>
    </form>
{% endblock %}
"""

    with open(os.path.join(project_name, "templates", "contact.html"), "w") as f:
        f.write(contact_html)

    # Create templates/contact_success.html
    contact_success_html = """{% extends "base.html" %}

{% block content %}
    <h1>{{ title }}</h1>
    <p>Thank you, {{ name }}! Your message has been received.</p>
    <p><a href="/">Return to home</a></p>
{% endblock %}
"""

    with open(os.path.join(project_name, "templates", "contact_success.html"), "w") as f:
        f.write(contact_success_html)

    # Create static/css/style.css
    style_css = """/* Basic styles */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    color: #333;
}

header {
    background-color: #4a5568;
    color: white;
    padding: 1rem;
}

nav ul {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
}

nav li {
    margin-right: 1rem;
}

nav a {
    color: white;
    text-decoration: none;
}

nav a:hover {
    text-decoration: underline;
}

main {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

footer {
    background-color: #f7fafc;
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}

/* Form styles */
form div {
    margin-bottom: 1rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
}

input, textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
}

button {
    background-color: #4a5568;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #2d3748;
}
"""

    with open(os.path.join(project_name, "static", "css", "style.css"), "w") as f:
        f.write(style_css)

    # Create static/js/main.js
    main_js = """// Main JavaScript file
console.log('ProAPI web template loaded');

// Add event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
});
"""

    with open(os.path.join(project_name, "static", "js", "main.js"), "w") as f:
        f.write(main_js)

    # Create README.md
    readme_md = f"""# {project_name}

A ProAPI web project.

## Running the application

```bash
python -m proapi run app.py
```

## Pages

- Home (/)
- About (/about)
- Contact (/contact)
"""

    with open(os.path.join(project_name, "README.md"), "w") as f:
        f.write(readme_md)

if __name__ == "__main__":
    main()
