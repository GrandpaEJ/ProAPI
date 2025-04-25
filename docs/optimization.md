# Performance Optimization in ProAPI

ProAPI includes several performance optimizations to make your applications faster and more efficient. These optimizations are enabled when running in fast mode.

## Fast Mode

To enable fast mode, use the `fast=True` parameter when running your application:

```python
from proapi import ProAPI

app = ProAPI()

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run(fast=True)  # Enable fast mode
```

## Optimization Features

When fast mode is enabled, ProAPI uses several optimizations:

### Route Caching

ProAPI caches route lookups to avoid regex compilation and matching on each request:

- Routes are cached based on the HTTP method and path
- The cache has a maximum size to prevent memory leaks
- Cache statistics are available for monitoring

### Object Pooling

ProAPI uses object pooling to reduce object creation and garbage collection:

- Request objects are reused from a pool
- Response objects are reused from a pool
- This reduces memory allocations and improves performance

### Optimized JSON Processing

ProAPI uses optimized JSON serialization and deserialization:

- Faster JSON serialization for common data types
- Optimized content type handling
- Reduced memory allocations

### Response Compression

ProAPI automatically compresses responses when appropriate:

- Responses larger than a threshold are compressed
- Compression is only used when it actually reduces size
- Appropriate headers are added automatically

## Monitoring Optimization Performance

You can monitor the performance of the optimization features:

```python
from proapi import ProAPI
from proapi.optimized import get_cache_stats

app = ProAPI()

@app.get("/stats")
def stats(request):
    return get_cache_stats()

if __name__ == "__main__":
    app.run(fast=True)
```

This will return statistics like:

```json
{
    "route_cache_size": 42,
    "route_cache_hits": 1024,
    "route_cache_misses": 50,
    "route_cache_hit_ratio": 0.9534,
    "request_pool_size": 10,
    "response_pool_size": 8
}
```

## Benchmarking

To benchmark your application, you can use tools like `wrk` or `ab`:

```bash
# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/

# Using Apache Bench
ab -n 10000 -c 100 http://localhost:8000/
```

## Optimization Tips

Here are some tips for optimizing your ProAPI applications:

### Use Fast Mode in Production

Always use fast mode in production for better performance:

```python
if __name__ == "__main__":
    app.run(fast=True, env="production")
```

### Use Multiple Workers

For better performance, use multiple workers:

```python
if __name__ == "__main__":
    app.run(fast=True, workers=4)  # Use 4 worker processes
```

### Optimize Your Handlers

Write efficient request handlers:

- Return JSON directly instead of strings when possible
- Use async handlers for I/O-bound operations
- Avoid unnecessary database queries
- Use caching for expensive operations

### Use WebSocket Optimizations

When using WebSockets, consider these optimizations:

- Use the rate limiting middleware to prevent abuse
- Close unused connections to free up resources
- Use room management for efficient broadcasting

### Monitor Performance

Regularly monitor the performance of your application:

- Check cache statistics
- Monitor memory usage
- Track response times
- Identify bottlenecks

## Advanced Optimization

For even more performance, consider these advanced techniques:

### Custom JSON Encoder

You can provide a custom JSON encoder for better performance:

```python
import json

class FastJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Add optimized serialization for your custom types
        if isinstance(obj, YourCustomType):
            return obj.to_dict()
        return super().default(obj)

app = ProAPI(json_encoder=FastJSONEncoder)
```

### Response Streaming

For large responses, consider using streaming:

```python
@app.get("/large-file")
def large_file(request):
    def generate():
        with open("large-file.txt", "r") as f:
            for line in f:
                yield line
    
    from proapi.server import StreamingResponse
    return StreamingResponse(generate(), content_type="text/plain")
```

### Cython Compilation

ProAPI supports Cython compilation for even better performance:

```bash
# Install Cython
pip install cython

# Compile your application
python setup.py build_ext --inplace
```

## Comparison with Other Frameworks

ProAPI's fast mode provides performance comparable to or better than other popular frameworks:

| Framework | Requests/sec | Latency (ms) |
|-----------|--------------|--------------|
| ProAPI (fast mode) | 15,000 | 2.5 |
| FastAPI | 12,000 | 3.2 |
| Flask | 8,000 | 5.1 |
| Django | 5,000 | 8.3 |

*Note: These are example numbers. Actual performance depends on many factors.*

## Conclusion

ProAPI's optimization features make it a high-performance framework suitable for production applications. By enabling fast mode and following the optimization tips, you can build applications that are both easy to develop and highly performant.
