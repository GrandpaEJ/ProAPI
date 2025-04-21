"""
Template rendering example for ProAPI.
"""

import os
import sys

# Add parent directory to path to import proapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proapi import ProAPI, render

# Create templates directory if it doesn't exist
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)

# Create example templates
with open(os.path.join(templates_dir, "base.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - ProAPI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        nav {
            margin-bottom: 20px;
        }
        nav a {
            margin-right: 10px;
        }
        footer {
            margin-top: 40px;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>ProAPI Template Example</p>
    </footer>
</body>
</html>""")

with open(os.path.join(templates_dir, "index.html"), "w") as f:
    f.write("""{% extends "base.html" %}

{% block content %}
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
    
    <h2>Features:</h2>
    <ul>
        {% for feature in features %}
            <li>{{ feature }}</li>
        {% endfor %}
    </ul>
{% endblock %}""")

with open(os.path.join(templates_dir, "about.html"), "w") as f:
    f.write("""{% extends "base.html" %}

{% block content %}
    <h1>{{ title }}</h1>
    <p>ProAPI is a lightweight, beginner-friendly yet powerful Python web framework.</p>
    <p>Version: {{ version }}</p>
{% endblock %}""")

with open(os.path.join(templates_dir, "contact.html"), "w") as f:
    f.write("""{% extends "base.html" %}

{% block content %}
    <h1>{{ title }}</h1>
    
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
{% endblock %}""")

with open(os.path.join(templates_dir, "contact_success.html"), "w") as f:
    f.write("""{% extends "base.html" %}

{% block content %}
    <h1>{{ title }}</h1>
    <p>Thank you, {{ name }}! Your message has been received.</p>
    <p><a href="/">Return to home</a></p>
{% endblock %}""")

# Initialize the app
app = ProAPI(debug=True, template_dir=templates_dir)

@app.get("/")
def index():
    return render("index.html", 
                 title="Home",
                 message="Welcome to ProAPI!",
                 features=[
                     "Decorator-based routing",
                     "Template rendering",
                     "Async support",
                     "Middleware system",
                     "Minimal dependencies"
                 ])

@app.get("/about")
def about():
    return render("about.html", 
                 title="About",
                 version="0.1.0")

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
    # Run the application
    app.run(host="127.0.0.1", port=8000)
