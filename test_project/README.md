# ProAPI Test Project

A simple blog application built with ProAPI, a lightweight Python web framework.

## Features

- Home page with a list of posts
- Individual post pages
- API endpoints for posts
- Authentication for creating/editing posts
- Template rendering with Jinja2
- Automatic API documentation
- Port forwarding to expose the app to the internet

## Running the Application

```bash
# Run locally
python test_project/app.py

# Run with CLI
python -m proapi run test_project/app.py

# Run with port forwarding (expose to the internet)
python -m proapi run test_project/app.py --forward
```

## Accessing the Application

- Web Interface: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/api/docs

## Admin Access

- Username: admin
- Password: password
- API Key: test-api-key

## API Endpoints

- `GET /api/posts` - Get all posts
- `GET /api/posts/{post_id}` - Get a specific post
- `POST /api/admin/posts` - Create a new post (requires API key)
- `PUT /api/admin/posts/{post_id}` - Update a post (requires API key)
- `DELETE /api/admin/posts/{post_id}` - Delete a post (requires API key)
- `GET /api/info` - Get server information

## Project Structure

```
test_project/
├── app.py              # Main application file
├── README.md           # This file
├── static/             # Static files
│   ├── css/
│   │   └── style.css   # CSS styles
│   └── js/
│       └── main.js     # JavaScript functionality
└── templates/          # HTML templates
    ├── about.html      # About page
    ├── admin.html      # Admin panel
    ├── base.html       # Base template
    ├── error.html      # Error page
    ├── index.html      # Home page
    ├── login.html      # Login page
    ├── login_success.html  # Login success page
    ├── new_post.html   # New post page
    └── post.html       # Individual post page
```
