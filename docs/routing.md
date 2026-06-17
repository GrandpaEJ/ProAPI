# Routing

## Basic

```python
@app.route('/hello')
def handler(r):
    return 'Hello'
```

## URL Parameters

```python
@app.route('/user/{id}')
def user(r, id):
    return f'User {id}'

@app.route('/post/{year}/{slug}')
def post(r, year, slug):
    return f'{year}: {slug}'
```

## Methods

```python
@app.route('/submit', methods=['POST'])
def submit(r):
    return r.form
```

## HTTP Errors

```python
from proapi import HTTPError

@app.route('/secret')
def secret(r):
    raise HTTPError(403, 'Nope')
```

## Redirects

```python
from proapi import HTTPRedirect

@app.route('/old')
def old(r):
    raise HTTPRedirect('/new')
```

## Dynamic type matching

```python
@app.route('/items/{id}', _type='json')
def items(r, id):
    return {'id': id}
```
