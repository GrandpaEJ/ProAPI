# MRQ (Message Request Queue)

MRQ is a job queue system that moves request processing off the main thread. Requests are forwarded to a worker pool, freeing the HTTP handler instantly.

## Setup

```python
app.config['mrq'] = [('127.0.0.1', 5555)]
```

## Usage

```python
@app.route('/process', mrq=True)
def process(r):
    # This runs on the MRQ worker, not the HTTP thread
    return do_heavy_computation(r.body)
```

## Two queues

```python
app.config['mrq'] = [('127.0.0.1', 5555)]   # primary
app.config['mrq2'] = [('127.0.0.2', 5555)]  # secondary
```

Use `mrq=True` or `mrq2=True` on a route to pick the queue. Useful for priority separation.
