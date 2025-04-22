# Fast Mode

ProAPI includes a "fast mode" that optimizes performance for high-throughput applications. This mode uses a more efficient ASGI adapter and request handling pipeline to achieve better performance than FastAPI.

## Using Fast Mode

To enable fast mode, simply pass `fast=True` to the `run()` method:

```python
from proapi import ProAPI

app = ProAPI()

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run(fast=True)
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

Fast mode has a few limitations:

- It requires uvicorn to be installed
- It may not work with all middleware (though most should work fine)
- It doesn't support some advanced features like WebSockets (yet)

## Example

Here's a complete example of using fast mode:

```python
from proapi import ProAPI

app = ProAPI(debug=True)  # Debug can still be enabled in fast mode

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
    # Run with fast mode enabled
    app.run(
        host="0.0.0.0",
        port=8000,
        fast=True,
        workers=4  # Multiple workers for even better performance
    )
```
