# Deploying ProAPI Applications to Production

This guide explains how to deploy ProAPI applications to production environments.

## Production Configuration

When deploying to production, you should configure your application appropriately:

```python
from proapi import ProAPI

app = ProAPI(
    debug=False,                  # Disable debug mode
    env="production",             # Set environment to production
    workers=4,                    # Use multiple workers
    request_timeout=30,           # Set request timeout
    max_request_size=1024*1024,   # Limit request size
    trusted_hosts=["example.com", "*.example.com"],  # Restrict allowed hosts
    log_level="WARNING",          # Set appropriate log level
    log_file="logs/proapi.log"    # Log to file
)
```

## Server Options

ProAPI supports different server types for production:

### Multi-Worker Server

The multi-worker server uses multiple processes to handle requests, which improves performance and reliability:

```python
app.run(
    host="0.0.0.0",
    port=8000,
    server_type="multiworker",
    workers=4  # Number of worker processes
)
```

### Using Uvicorn

For better performance, you can use Uvicorn as the server:

```bash
pip install uvicorn
```

```python
app.run(
    host="0.0.0.0",
    port=8000,
    server_type="uvicorn",
    workers=4
)
```

## Security Considerations

### Trusted Hosts

In production, you should restrict which hosts can access your application:

```python
app.trusted_hosts = ["example.com", "api.example.com", "*.example.com"]
```

This helps prevent host header attacks.

### Request Limits

Set appropriate limits for requests:

```python
app.request_timeout = 30  # 30 seconds
app.max_request_size = 1024 * 1024  # 1MB
```

### CORS Configuration

Configure CORS headers appropriately:

```python
from proapi.middleware import cors_middleware

app.use(cors_middleware(
    allowed_origins=["https://example.com"],
    allowed_methods=["GET", "POST", "PUT", "DELETE"],
    allowed_headers=["Content-Type", "Authorization"]
))
```

### API Documentation

Consider disabling public API documentation in production:

```python
app = ProAPI(
    env="production",
    enable_docs=False  # Docs will be disabled in production by default
)
```

## Logging

Configure logging for production:

```python
app = ProAPI(
    log_level="WARNING",  # Only log warnings and errors
    log_file="logs/proapi.log"  # Log to file
)
```

In production, ProAPI automatically configures a log file if none is specified.

## Deployment Options

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "proapi", "run", "app.py", "--host=0.0.0.0"]
```

Build and run the Docker image:

```bash
docker build -t myapp .
docker run -p 8000:8000 myapp
```

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PROAPI_ENV=production
    volumes:
      - ./logs:/app/logs
```

Run with Docker Compose:

```bash
docker-compose up -d
```

### Nginx Reverse Proxy

For production deployments, it's recommended to use Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service

Create a systemd service file (`/etc/systemd/system/proapi-app.service`):

```ini
[Unit]
Description=ProAPI Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/app
ExecStart=/usr/bin/python -m proapi run app.py --host=0.0.0.0
Restart=always
Environment=PROAPI_ENV=production

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable proapi-app
sudo systemctl start proapi-app
```

## Performance Optimization

### Cython Compilation

Compile your application with Cython for improved performance:

```bash
python -m proapi run app.py --compile
```

This requires Cython to be installed:

```bash
pip install cython
```

### Response Compression

Enable response compression to reduce bandwidth usage:

```python
from proapi.middleware import compression_middleware

app.use(compression_middleware(
    min_size=1024,  # Minimum size for compression (bytes)
    level=6         # Compression level (1-9)
))
```

### Caching

Implement caching for frequently accessed data:

```python
# Simple in-memory cache
cache = {}

@app.get("/items/{item_id:int}")
def get_item(item_id):
    # Check cache
    cache_key = f"item:{item_id}"
    if cache_key in cache:
        return cache[cache_key]
    
    # Simulate database query
    item = {"id": item_id, "name": f"Item {item_id}"}
    
    # Store in cache
    cache[cache_key] = item
    
    return item
```

## Monitoring

### Health Check Endpoint

Add a health check endpoint to monitor your application:

```python
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": time.time()
    }
```

### Metrics Endpoint

Add a metrics endpoint to monitor application performance:

```python
import time
import os
import psutil

@app.get("/metrics")
def metrics():
    process = psutil.Process(os.getpid())
    
    return {
        "uptime": time.time() - process.create_time(),
        "memory_usage": process.memory_info().rss / 1024 / 1024,  # MB
        "cpu_percent": process.cpu_percent(),
        "thread_count": process.num_threads(),
        "open_files": len(process.open_files()),
        "connections": len(process.connections())
    }
```

## Deployment Checklist

- [ ] Set `debug=False` and `env="production"`
- [ ] Configure appropriate logging
- [ ] Set request limits
- [ ] Configure trusted hosts
- [ ] Use multiple workers
- [ ] Set up a reverse proxy
- [ ] Enable HTTPS
- [ ] Implement monitoring
- [ ] Set up backups
- [ ] Test thoroughly before deployment