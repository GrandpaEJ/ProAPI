# Quickstart

```python
import proapi

app = proapi.Application()

@app.route('/')
def hello(r):
    return 'Hello World!'

app.run(cores=2)
```

```bash
$ curl http://localhost:8080
Hello World!
```

## Routes

```python
@app.route('/text', _type='text')
def text(r):
    return 'plain text'

@app.route('/json', _type='json')
def json(r):
    return {'key': 'value'}
```

Run with `app.run()`. Default port is 8080. Pass `cores` for multiprocessing.
