# Template Rendering in ProAPI

ProAPI provides template rendering using Jinja2. This guide explains how to set up and use templates in your application.

## Setting Up Templates

When creating your ProAPI application, specify the template directory:

```python
from proapi import ProAPI

app = ProAPI(template_dir="templates")
```

By default, ProAPI looks for templates in a directory named "templates" in the current working directory. You can specify a different directory if needed.

## Creating Templates

Templates are HTML files with Jinja2 syntax. Here's a simple example:

```html
<!DOCTYPE html>
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
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
    
    <h2>Items:</h2>
    <ul>
        {% for item in items %}
            <li>{{ item }}</li>
        {% endfor %}
    </ul>
</body>
</html>
```

Save this file as `index.html` in your templates directory.

## Rendering Templates

Use the `render` function to render templates:

```python
from proapi import ProAPI, render

app = ProAPI(template_dir="templates")

@app.get("/")
def index():
    return render("index.html", 
                 title="ProAPI Template Example",
                 message="Welcome to ProAPI template rendering!",
                 items=["Item 1", "Item 2", "Item 3"])
```

The `render` function takes the template name as the first argument, followed by any variables you want to pass to the template.

## Template Variables

You can pass any Python object to your templates:

```python
@app.get("/user/{user_id:int}")
def user_profile(user_id):
    # Simulate fetching user data
    user = {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "joined": "2023-01-01"
    }
    
    return render("user.html", user=user, title=f"User {user_id}")
```

## Template Inheritance

Jinja2 supports template inheritance, which allows you to create a base template and extend it in other templates:

Base template (`base.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}ProAPI{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    {% block head %}{% endblock %}
</head>
<body>
    <header>
        <h1>ProAPI Example</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2023 ProAPI Example</p>
    </footer>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

Child template (`page.html`):

```html
{% extends "base.html" %}

{% block title %}{{ title }} - ProAPI{% endblock %}

{% block content %}
    <h1>{{ title }}</h1>
    <p>{{ content }}</p>
{% endblock %}

{% block scripts %}
    <script src="/static/js/app.js"></script>
{% endblock %}
```

## Template Filters

Jinja2 provides filters to modify variables in templates:

```html
<p>{{ name|upper }}</p>
<p>{{ description|truncate(100) }}</p>
<p>{{ date|date('%Y-%m-%d') }}</p>
```

ProAPI adds a `json` filter for formatting JSON data:

```html
<script>
    const data = {{ data|json }};
    console.log(data);
</script>
```

## Template Conditionals

Use conditionals in your templates:

```html
{% if user %}
    <p>Welcome, {{ user.name }}!</p>
{% else %}
    <p>Please log in.</p>
{% endif %}
```

## Template Loops

Loop through collections:

```html
<ul>
    {% for item in items %}
        <li>{{ item.name }} - ${{ item.price }}</li>
    {% endfor %}
</ul>

{% if items|length == 0 %}
    <p>No items found.</p>
{% endif %}
```

## Including Other Templates

Include other templates:

```html
{% include "partials/header.html" %}

<main>
    <h1>{{ title }}</h1>
    <p>{{ content }}</p>
</main>

{% include "partials/footer.html" %}
```

## Error Handling

If Jinja2 is not installed, ProAPI will raise an ImportError. Make sure to install Jinja2:

```bash
pip install jinja2
```

## Fallback Rendering

ProAPI includes a simple template rendering fallback when Jinja2 is not available:

```python
from proapi.templating import simple_render

# Only supports basic variable substitution with {{ var }}
html = simple_render(
    "<h1>{{ title }}</h1><p>{{ message }}</p>",
    title="Hello",
    message="World"
)
```