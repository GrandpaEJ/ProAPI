# Request

The request object `r` is passed to every handler.

## Body

```python
@app.route('/data', methods=['POST'])
def data(r):
    text = r.text          # raw body as str
    body = r.body          # raw body as bytes
    return text
```

## JSON

```python
@app.route('/api', methods=['POST'])
def api(r):
    data = r.json          # parsed dict/list
    return {'received': data}
```

## Form

```python
@app.route('/form', methods=['POST'])
def form(r):
    name = r.form['name']  # dict of form fields
    return f'Hello {name}'
```

## Headers

```python
@app.route('/headers')
def headers(r):
    ua = r.headers.get('User-Agent')
    ct = r.headers.get('Content-Type')
    return f'UA: {ua}'
```

## Cookies

```python
@app.route('/cookies')
def cookies(r):
    session = r.cookies.get('session')
    return f'session: {session}'
```

## File uploads

```python
@app.route('/upload', methods=['POST'])
def upload(r):
    f = r.file             # single file
    # or
    files = r.files        # dict of files
    return f'Got {f.name} ({f.type})'
```

## Other

```python
r.method       # GET, POST, ...
r.path         # /hello/world
r.query_string # ?foo=bar
r.ip           # client IP
r.mime_type    # content-type header
r.encoding     # charset
```
