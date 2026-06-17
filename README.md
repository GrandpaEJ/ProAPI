<div align="center">
  <h1>⚡ ProAPI</h1>
  <p><b>Async Python web server — C core, SIMD-accelerated</b></p>
  <p>
    <a href="#-benchmarks">Benchmarks</a> •
    <a href="#-quickstart">Quickstart</a> •
    <a href="#-installation">Install</a> •
    <a href="#-api">API</a> •
    <a href="#-examples">Examples</a> •
    <a href="#-legacy">Legacy</a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/python-3.13%20|%203.14-blue?logo=python&logoColor=white">
    <img src="https://img.shields.io/badge/C-99-555555?logo=c&logoColor=white">
    <img src="https://img.shields.io/badge/license-MIT-green">
    <img src="https://img.shields.io/badge/platform-linux%20|%20macos-lightgrey">
    <img src="https://img.shields.io/github/v/release/GrandpaEJ/ProAPI?include_prereleases&label=release&logo=github">
    <img src="https://img.shields.io/github/repo-size/GrandpaEJ/ProAPI?label=size&logo=github">
    <img src="https://img.shields.io/github/last-commit/GrandpaEJ/ProAPI?label=updated&logo=github">
    <img src="https://img.shields.io/github/stars/GrandpaEJ/ProAPI?style=social">
  </p>
  <p>
    <img src="https://img.shields.io/badge/ASGI-uvloop-24a0ed?logo=uv">
    <img src="https://img.shields.io/badge/SIMD-AVX2%20|%20SSE4.2%20|%20BMI2-orange">
    <img src="https://img.shields.io/badge/serializer-mrpacker_(built--in)-purple">
  </p>
  <br>
</div>

Most Python web servers hit a wall when you need real throughput — pure-Python event loops just can't keep up. ProAPI takes the hot path out of Python and into C, using SIMD instructions (the same kind that power video encoding and scientific computing) to parse HTTP at memory bandwidth speeds.

The result? ~150k req/s on a laptop CPU, and over 8 million with pipelining. No FFI tricks, no Cython — just a C extension that talks directly to Python's runtime.

Based on [mrhttp](https://github.com/MarkReedZ/mrhttp) by Mark Reed. Python 3.13+ only.

---

## Features

- **C extension core** — routing, parsing, response building all in compiled C, not Python
- **SIMD HTTP parser** — parses headers 16–32 bytes at a time using SSE4.2/AVX2/BMI2
- **uvloop event loop** — libuv backend replaces asyncio's default, cuts overhead significantly
- **Built-in binary serializer** — mrpacker compiled directly into the extension, no extra pip dependencies beyond uvloop
- **Trie-based router** — O(path length) matching with zero memory alloc per request
- **Async and sync handlers** — write either, ProAPI handles the scheduling
- **Session backends** — memcached, redis, mrwork, or mrcache out of the box
- **Pipelining** — handles multiple requests per TCP connection without head-of-line blocking

---

## 🚀 Quickstart

```python
import proapi

app = proapi.Application()

@app.route('/')
def hello(r):
    return 'Hello World!'

@app.route('/json', _type='json')
def json_route(r):
    return {'message': 'Hello World!'}

app.run(cores=2)
```

```bash
$ curl http://localhost:8080/json
{"message": "Hello World!"}
```

---

## 📦 Installation

```bash
pip install proapi
```

### From source

```bash
git clone https://github.com/GrandpaEJ/ProAPI
cd ProAPI
pip install -e .
# or: zig build
```

Requires Python 3.13+, a C99 compiler, and Python dev headers (`python3-dev` on Debian).

---

## 📊 Benchmarks

ProAPI is roughly **5–30× faster** than pure-Python async servers depending on the workload. Tests below ran on an Intel i5-8365U laptop (4C/8T, 1.6 GHz base). On server hardware (Xeon, Ryzen, EPYC) you'll see much higher numbers.

| Route | Concurrency | Requests/s | Latency (avg) |
|-------|-------------|-----------|---------------|
| `/` (plaintext) | t4-c64 | **132,806** | 890µs |
| `/json` | t4-c64 | **105,811** | 825µs |
| `/` (plaintext) | t8-c256 | **149,779** | 2.3ms |
| `/` (plaintext) | t8-c512 | **149,500** | 4.1ms |

The server plateaus at ~150k on this laptop because the CPU is only 30% busy — bottleneck is the Python GIL, not the C code. Multi-process or the async worker pool bypasses this.

<details>
<summary>Original benchmark data (from mrhttp, on faster hardware)</summary>

```
Pipelined
  Hello (cached)    8,534,332 req/s
  Hello             6,834,994 req/s
  More hdrs         6,193,307 req/s
  Sessions          4,396,364 req/s
  File Upload       3,510,289 req/s
  mrpacker          2,052,674 req/s
  Form              1,182,228 req/s

One by one
  Hello               707,667 req/s
  Hello hdrs          728,639 req/s
  Cookies             588,212 req/s
  many args           691,910 req/s
  404 natural         763,643 req/s
  404                 580,424 req/s
  Form parsing        338,553 req/s
  mrpacker            533,242 req/s
  Sessions            325,354 req/s
  File Upload         292,331 req/s
  get ip              503,454 req/s
```

For comparison, Sanic (pure Python):

```
Hello World          22,366 req/s
Cookies              20,867 req/s
404                   8,256 req/s
forms                11,104 req/s
sessions              4,053 req/s
File upload           1,457 req/s
```

</details>

---

## 🔧 API

### Routing

```python
from proapi import HTTPError, HTTPRedirect

@app.route('/hello/{name}')
def greet(r, name):
    return f'Hello {name}!'

@app.route('/post', methods=['POST'])
def create(r):
    data = r.json
    form = r.form
    return {'ok': True}

@app.route('/error')
def err(r):
    raise HTTPError(404, 'Not found')

@app.route('/old')
def old(r):
    raise HTTPRedirect('/new')
```

### Async handlers

```python
@app.route('/db')
async def db_query(r):
    async with app.pg_pool.acquire() as conn:
        val = await conn.fetchval('SELECT 1')
    return {'result': val}
```

### Events

```python
@app.on('at_start')
async def startup():
    app.db = await create_pool()

@app.on('at_end')
async def shutdown():
    await app.db.close()
```

### Pack / Unpack (built-in serializer)

```python
import proapi

data = proapi.pack({'hello': 'world', 'nums': [1, 2, 3]})
obj = proapi.unpack(data)
```

No external serializer — mrpacker is compiled directly into the C extension. Faster and one less dependency.

---

## 🧪 Examples

| File | What it shows |
|------|---------------|
| `examples/1_hello.py` | Basic routing |
| `examples/2_async.py` | Async handlers |
| `examples/3_request.py` | Request object (json, form, headers) |
| `examples/4_response.py` | Custom responses |
| `examples/5_router.py` | URL parameters |
| `examples/6_exceptions.py` | Error handling |
| `examples/7_session.py` | Session middleware |
| `examples/8_template.py` | Template rendering |
| `examples/9_mrworkserver.py` | MRQ job queue |
| `examples/14_upload.py` | File uploads |

```bash
python examples/1_hello.py
```

---

---

## 🏛️ Legacy

ProAPI is a fork of [mrhttp](https://github.com/MarkReedZ/mrhttp) by Mark Reed. The C core, SIMD parsers, router design, protocol implementations, and [mrpacker](https://github.com/MarkReedZ/mrpacker) serialization are his work. All credit for the foundation goes to him.

---

<div align="center">
  <sub><b><a href="LICENSE">MIT License</a></b></sub>
</div>
