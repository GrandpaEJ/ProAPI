"""
Complete example application for ProAPI.

This example demonstrates multiple features of the ProAPI framework:
- Routing with path parameters
- Template rendering
- Middleware
- JSON handling
- Static file serving
- Error handling
"""

import os
import sys
import time
import json
import asyncio

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, render

# Create directories for templates and static files
templates_dir = os.path.join(os.path.dirname(__file__), "complete_templates")
static_dir = os.path.join(os.path.dirname(__file__), "complete_static")
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

# Create a base template
with open(os.path.join(templates_dir, "base.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - ProAPI Example</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <h1>ProAPI Example</h1>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/api">API</a></li>
                <li><a href="/async">Async</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>ProAPI - A lightweight, beginner-friendly yet powerful Python web framework</p>
    </footer>
    
    <script src="/static/js/main.js"></script>
</body>
</html>""")

# Create a home page template
with open(os.path.join(templates_dir, "index.html"), "w") as f:
    f.write("""{% extends "base.html" %}

{% block content %}
    <h2>{{ title }}</h2>
    <p>{{ message }}</p>
    
    <h3>Features:</h3>
    <ul>
        {% for feature in features %}
            <li>{{ feature }}</li>
        {% endfor %}
    </ul>
{% endblock %}""")

# Create an about page template
with open(os.path.join(templates_dir, "about.html"), "w") as f:
    f.write("""{% extends "base.html" %}

{% block content %}
    <h2>{{ title }}</h2>
    <p>ProAPI is a lightweight, beginner-friendly yet powerful Python web framework.</p>
    <p>Version: {{ version }}</p>
    
    <h3>Key Features:</h3>
    <ul>
        <li>Decorator-based routing</li>
        <li>Template rendering with Jinja2</li>
        <li>Async support</li>
        <li>Middleware system</li>
        <li>Minimal dependencies</li>
        <li>Built-in JSON support</li>
        <li>Optional Cython compilation</li>
    </ul>
{% endblock %}""")

# Create an API page template
with open(os.path.join(templates_dir, "api.html"), "w") as f:
    f.write("""{% extends "base.html" %}

{% block content %}
    <h2>{{ title }}</h2>
    <p>This page demonstrates the API functionality of ProAPI.</p>
    
    <h3>API Endpoints:</h3>
    <ul>
        {% for endpoint in endpoints %}
            <li>
                <strong>{{ endpoint.method }} {{ endpoint.path }}</strong>
                <p>{{ endpoint.description }}</p>
            </li>
        {% endfor %}
    </ul>
    
    <h3>Try it out:</h3>
    <div class="api-test">
        <div class="form-group">
            <label for="name">Name:</label>
            <input type="text" id="name" value="world">
        </div>
        <button id="test-api">Test API</button>
        <div id="api-result"></div>
    </div>
{% endblock %}""")

# Create an async page template
with open(os.path.join(templates_dir, "async.html"), "w") as f:
    f.write("""{% extends "base.html" %}

{% block content %}
    <h2>{{ title }}</h2>
    <p>This page demonstrates the async functionality of ProAPI.</p>
    
    <h3>Async vs Sync:</h3>
    <div class="comparison">
        <div class="sync">
            <h4>Synchronous</h4>
            <p>Processing time: <span id="sync-time">-</span></p>
            <button id="test-sync">Test Sync</button>
            <div id="sync-result"></div>
        </div>
        <div class="async">
            <h4>Asynchronous</h4>
            <p>Processing time: <span id="async-time">-</span></p>
            <button id="test-async">Test Async</button>
            <div id="async-result"></div>
        </div>
    </div>
{% endblock %}""")

# Create a CSS file
with open(os.path.join(static_dir, "css", "style.css"), "w") as f:
    f.write("""/* Basic styles */
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

/* API test styles */
.api-test {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #f7fafc;
    border-radius: 4px;
}

.form-group {
    margin-bottom: 1rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
}

input {
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

#api-result, #sync-result, #async-result {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #edf2f7;
    border-radius: 4px;
    white-space: pre-wrap;
}

/* Comparison styles */
.comparison {
    display: flex;
    gap: 2rem;
}

.sync, .async {
    flex: 1;
    padding: 1rem;
    background-color: #f7fafc;
    border-radius: 4px;
}""")

# Create a JavaScript file
with open(os.path.join(static_dir, "js", "main.js"), "w") as f:
    f.write("""// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // API test
    const testApiButton = document.getElementById('test-api');
    if (testApiButton) {
        testApiButton.addEventListener('click', function() {
            const name = document.getElementById('name').value || 'world';
            const apiResult = document.getElementById('api-result');
            
            apiResult.textContent = 'Loading...';
            
            fetch(`/api/hello/${name}`)
                .then(response => response.json())
                .then(data => {
                    apiResult.textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    apiResult.textContent = `Error: ${error.message}`;
                });
        });
    }
    
    // Sync test
    const testSyncButton = document.getElementById('test-sync');
    if (testSyncButton) {
        testSyncButton.addEventListener('click', function() {
            const syncResult = document.getElementById('sync-result');
            const syncTime = document.getElementById('sync-time');
            
            syncResult.textContent = 'Loading...';
            
            const startTime = performance.now();
            
            fetch('/api/sync')
                .then(response => response.json())
                .then(data => {
                    const endTime = performance.now();
                    syncTime.textContent = `${((endTime - startTime) / 1000).toFixed(3)}s`;
                    syncResult.textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    syncResult.textContent = `Error: ${error.message}`;
                });
        });
    }
    
    // Async test
    const testAsyncButton = document.getElementById('test-async');
    if (testAsyncButton) {
        testAsyncButton.addEventListener('click', function() {
            const asyncResult = document.getElementById('async-result');
            const asyncTime = document.getElementById('async-time');
            
            asyncResult.textContent = 'Loading...';
            
            const startTime = performance.now();
            
            fetch('/api/async')
                .then(response => response.json())
                .then(data => {
                    const endTime = performance.now();
                    asyncTime.textContent = `${((endTime - startTime) / 1000).toFixed(3)}s`;
                    asyncResult.textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    asyncResult.textContent = `Error: ${error.message}`;
                });
        });
    }
});""")

# Create the application
app = ProAPI(debug=True, template_dir=templates_dir, static_dir=static_dir)

# Define middleware
@app.use
def logging_middleware(request):
    """Log request details."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.path}")
    request.start_time = time.time()
    return request

@app.use
def timing_middleware(request):
    """Add timing information to the response."""
    def add_timing_header(response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response.headers['X-Response-Time'] = f"{duration:.6f}s"
        return response
    
    request.add_timing_header = add_timing_header
    return request

# Simulate a database
db = {
    "users": [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
    ],
    "products": [
        {"id": 1, "name": "Product 1", "price": 9.99},
        {"id": 2, "name": "Product 2", "price": 19.99}
    ]
}

# Simulate async operations
async def fetch_data(delay=1):
    await asyncio.sleep(delay)
    return {
        "timestamp": time.time(),
        "data": "Async data fetched successfully"
    }

# Define routes

# Web routes
@app.get("/")
def index(request):
    """Home page."""
    return render("index.html", 
                 title="Home",
                 message="Welcome to the ProAPI complete example!",
                 features=[
                     "Routing with path parameters",
                     "Template rendering",
                     "Middleware",
                     "JSON handling",
                     "Static file serving",
                     "Error handling"
                 ])

@app.get("/about")
def about(request):
    """About page."""
    return render("about.html", 
                 title="About",
                 version="0.1.0")

@app.get("/api")
def api_page(request):
    """API documentation page."""
    return render("api.html", 
                 title="API",
                 endpoints=[
                     {"method": "GET", "path": "/api/hello/{name}", "description": "Get a greeting"},
                     {"method": "GET", "path": "/api/users", "description": "Get all users"},
                     {"method": "GET", "path": "/api/users/{id}", "description": "Get a user by ID"},
                     {"method": "GET", "path": "/api/products", "description": "Get all products"},
                     {"method": "GET", "path": "/api/products/{id}", "description": "Get a product by ID"},
                     {"method": "GET", "path": "/api/sync", "description": "Synchronous operation"},
                     {"method": "GET", "path": "/api/async", "description": "Asynchronous operation"}
                 ])

@app.get("/async")
def async_page(request):
    """Async demonstration page."""
    return render("async.html", 
                 title="Async Demo")

# API routes
@app.get("/api/hello/{name}")
def api_hello(name, request):
    """API hello endpoint."""
    return {
        "message": f"Hello, {name}!",
        "timestamp": time.time()
    }

@app.get("/api/users")
def api_users(request):
    """Get all users."""
    return {"users": db["users"]}

@app.get("/api/users/{id:int}")
def api_user(id, request):
    """Get a user by ID."""
    for user in db["users"]:
        if user["id"] == id:
            return user
    
    return {"error": "User not found"}, 404

@app.get("/api/products")
def api_products(request):
    """Get all products."""
    return {"products": db["products"]}

@app.get("/api/products/{id:int}")
def api_product(id, request):
    """Get a product by ID."""
    for product in db["products"]:
        if product["id"] == id:
            return product
    
    return {"error": "Product not found"}, 404

@app.get("/api/sync")
def api_sync(request):
    """Synchronous operation."""
    # Simulate a blocking operation
    start_time = time.time()
    time.sleep(1)
    end_time = time.time()
    
    return {
        "message": "Synchronous operation completed",
        "duration": end_time - start_time,
        "timestamp": time.time()
    }

@app.get("/api/async")
async def api_async(request):
    """Asynchronous operation."""
    start_time = time.time()
    data = await fetch_data()
    end_time = time.time()
    
    return {
        "message": "Asynchronous operation completed",
        "duration": end_time - start_time,
        "result": data
    }

# Error handling
@app.get("/error")
def error(request):
    """Trigger an error."""
    # This will raise a ZeroDivisionError
    return 1 / 0

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8005)
