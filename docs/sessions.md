# Sessions

## Enable

```python
app.config['session_secret'] = 'your-secret-key'
# app.session_backend = 'memcached'  # default
```

## Usage

```python
@app.route('/login')
def login(r):
    r.session['user'] = 'Alice'
    return 'logged in'

@app.route('/profile')
def profile(r):
    user = r.session.get('user')
    return f'Hello {user}'
```

## Backends

```python
# Memcached (default)
app.session_backend = 'memcached'
app.config['memcached'] = [('127.0.0.1', 11211)]

# MRWorkServer
app.session_backend = 'mrworkserver'
app.config['mrq'] = [('127.0.0.1', 5555)]

# MrCache (built-in)
app.session_backend = 'mrcache'
```

Session data is serialized with the built-in mrpacker — no extra dependencies.
