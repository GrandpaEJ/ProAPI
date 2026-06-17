# Async

## Async handlers

```python
@app.route('/db')
async def db(r):
    async with app.pg_pool.acquire() as conn:
        val = await conn.fetchval('SELECT 1')
    return {'result': val}
```

## Startup / shutdown

```python
@app.on('at_start')
async def startup():
    app.db = await create_pool()
    print('ready')

@app.on('at_end')
async def shutdown():
    await app.db.close()
    print('bye')
```

## Background tasks

```python
async def bg_worker():
    while True:
        await asyncio.sleep(60)
        print('tick')

@app.on('at_start')
async def start_bg():
    app.loop.create_task(bg_worker())
```

## Event loop

ProAPI uses uvloop by default — libuv backend, significantly faster than the default asyncio event loop.

```python
# uvloop is automatic, no config needed
app.run()
```
