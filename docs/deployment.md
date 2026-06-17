# Deployment

## Workers

```python
app.run(cores=4)       # 4 worker processes
app.run(cores=0)       # all available CPUs
app.run()              # 1 worker (default)
```

Each worker runs its own event loop and accepts connections independently.

## Production config

```python
app.config = {
    'max_body_size': 1024 * 1024,        # 1MB
    'keepalive_timeout': 30,             # seconds
    'session_secret': 'change-me',
}
```

## Behind nginx

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Performance tips

- Set CPU governor to `performance` for benchmarks
- Use `wrk -t4 -c64` for realistic load testing
- Pipelining gives 10-50× throughput boost
- The GIL becomes the bottleneck above ~150k req/s on this hardware — more workers help with connection concurrency, not raw throughput
