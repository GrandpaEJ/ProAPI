# Response

## Plain text

```python
@app.route('/')
def index(r):
    return 'Hello World'
```

## JSON

```python
@app.route('/data')
def data(r):
    return {'key': 'value', 'nums': [1, 2, 3]}
```

The route must have `_type='json'` or return a dict.

## Custom status / headers

```python
from proapi import Response

@app.route('/custom')
def custom(r):
    resp = Response()
    resp.status = 201
    resp.set_header('X-Custom', 'yes')
    resp.text = 'Created'
    return resp
```

## Binary

```python
@app.route('/file')
def file(r):
    resp = Response()
    resp.body = b'\x00\x01\x02'
    resp.set_header('Content-Type', 'application/octet-stream')
    return resp
```

## Streaming

```python
@app.route('/stream')
async def stream(r):
    resp = Response()
    resp.stream = True
    return resp
```

## Errors

```python
from proapi import HTTPError

@app.route('/404')
def not_found(r):
    raise HTTPError(404, 'Not found')

@app.route('/403')
def forbidden(r):
    raise HTTPError(403, 'Forbidden')
```

Custom error pages:

```python
app.config['err404'] = b'<h1>Missing</h1>'
app.config['err500'] = b'<h1>Oops</h1>'
```
