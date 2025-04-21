"""
Example of template rendering with ProAPI.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, render

# Create templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)

# Create a simple template
with open(os.path.join(templates_dir, "index.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
        }
        .message {
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        ul {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <div class="message">{{ message }}</div>
    
    <h2>Features:</h2>
    <ul>
        {% for feature in features %}
            <li>{{ feature }}</li>
        {% endfor %}
    </ul>
</body>
</html>""")

# Create the application
app = ProAPI(debug=True, template_dir=templates_dir)

@app.get("/")
def index(request):
    """Render the index template."""
    return render("index.html", 
                 title="ProAPI Template Example",
                 message="Welcome to ProAPI template rendering!",
                 features=[
                     "Decorator-based routing",
                     "Template rendering with Jinja2",
                     "Async support",
                     "Middleware system",
                     "Minimal dependencies"
                 ])

if __name__ == "__main__":
    print(f"Template directory: {templates_dir}")
    app.run(host="127.0.0.1", port=8001)
