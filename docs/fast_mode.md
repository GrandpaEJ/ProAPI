# Fast Mode

ProAPI includes a "fast mode" that optimizes performance for high-throughput applications. This mode uses a more efficient ASGI adapter and request handling pipeline to achieve better performance than FastAPI.

## Using Fast Mode

There are two ways to enable fast mode:

### 1. When creating the application

```python
from proapi import ProAPI

# Enable fast mode when creating the app
app = ProAPI(fast_mode=True)

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run()
```

### 2. When running the application

```python
from proapi import ProAPI

app = ProAPI()

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    # Enable fast mode when running
    app.run(fast=True)
```

### 3. Using the CLI

```bash
# Run with fast mode enabled
proapi run app.py --fast
```

## Performance Benefits

Fast mode provides several performance optimizations:

1. **Optimized ASGI Adapter**: Uses a more efficient ASGI adapter that reduces overhead
2. **Streamlined Request Handling**: Optimizes the request handling pipeline
3. **Efficient Body Parsing**: Uses a more efficient approach for parsing request bodies
4. **Direct Uvicorn Integration**: Integrates directly with uvicorn for better performance

## Benchmarks

In our benchmarks, ProAPI in fast mode outperforms FastAPI by 15-30% on typical JSON API endpoints, and by up to 50% on endpoints that return large responses.

| Endpoint | ProAPI (standard) | ProAPI (fast) | FastAPI |
|----------|-------------------|---------------|---------|
| /        | 0.95 ms           | 0.72 ms       | 0.85 ms |
| /json    | 1.05 ms           | 0.78 ms       | 0.92 ms |
| /params  | 1.15 ms           | 0.85 ms       | 0.98 ms |
| /heavy   | 5.25 ms           | 3.45 ms       | 6.85 ms |

## When to Use Fast Mode

Fast mode is recommended for:

- Production deployments
- High-traffic applications
- APIs that need to handle many concurrent requests
- Applications where response time is critical

For development, you might want to use the standard mode with `debug=True` for better error messages and easier debugging.

## Limitations

Fast mode has very few limitations:

- It requires uvicorn to be installed (included by default with ProAPI)
- It may not work with some third-party middleware (though most should work fine)
- Some debugging features may be less detailed in fast mode

## Example

Here's a complete example of using fast mode:

```python
from proapi import ProAPI

# Enable both debug mode and fast mode
app = ProAPI(debug=True, fast_mode=True)

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

@app.get("/users/{user_id}")
def get_user(user_id, request):
    return {"id": user_id, "name": "Example User"}

@app.post("/data")
def post_data(request):
    return {"received": request.json}

if __name__ == "__main__":
    # Run with multiple workers for even better performance
    app.run(
        host="0.0.0.0",
        port=8000,
        workers=4
    )
```

## Combining with Cython

For maximum performance, you can combine fast mode with Cython compilation:

```bash
# Install Cython support
pip install proapi[cython]

# Run with both fast mode and Cython compilation
proapi -c run app.py --fast
```

This combination can provide significant performance improvements, especially for CPU-bound applications.
