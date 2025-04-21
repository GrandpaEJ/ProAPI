# ProAPI Examples

This directory contains example applications that demonstrate various features of the ProAPI framework.

## Basic Example

A simple example that demonstrates the basic functionality of ProAPI.

```bash
python examples/basic_app.py
```

## Async Example

An example that demonstrates the async functionality of ProAPI.

```bash
python examples/async_example.py
```

## Template Example

An example that demonstrates template rendering with ProAPI.

```bash
python examples/template_example.py
```

## Middleware Example

An example that demonstrates middleware functionality with ProAPI.

```bash
python examples/middleware_example.py
```

## CLI Example

An example that demonstrates how to use the ProAPI CLI.

```bash
python -m proapi run examples/cli_example.py
```

## Multi-App Example

An example that demonstrates how to run specific app instances with the CLI.

```bash
# Run the main app (default)
python -m proapi run examples/multi_app.py

# Run a specific app
python -m proapi run examples/multi_app.py:app1 --port 8010

# Run with host options
python -m proapi run examples/multi_app.py --host local
python -m proapi run examples/multi_app.py --host all

# Compile and run
python -m proapi -c run examples/multi_app.py
```

## CLI Test Example

A simple example for testing various CLI commands.

```bash
# Run with default settings
python -m proapi run examples/main.py

# Run with specific app instance
python -m proapi run examples/main.py:app

# Run with specific port
python -m proapi run examples/main.py --port 5500

# Run with specific host
python -m proapi run examples/main.py --host 0.0.0.0
python -m proapi run examples/main.py --host all

# Compile and run
python -m proapi -c run examples/main.py
```

## Documentation Example

An example that demonstrates the automatic API documentation feature.

```bash
python examples/docs_example.py
```

Then visit http://127.0.0.1:8006/docs in your browser.

## Swagger UI Documentation Example

An example that demonstrates the Swagger UI API documentation feature.

```bash
python examples/swagger_docs_example.py
```

Then visit http://127.0.0.1:8005/docs in your browser to see the interactive Swagger UI documentation.

## Default Documentation Example

An example that demonstrates the default documentation endpoint at /.docs.

```bash
python examples/default_docs_example.py
```

Then visit http://127.0.0.1:8010/.docs in your browser to see the default Swagger UI documentation.

## Complete Example

A complete example that demonstrates multiple features of ProAPI.

```bash
python examples/complete_example.py
```

## Port Forwarding Example

An example that demonstrates the port forwarding feature to expose your app to the internet.

```bash
# Run with default settings (forwarding enabled)
python examples/forwarding_example.py

# Run with CLI and explicit forwarding
python -m proapi run examples/forwarding_example.py --forward

# Run with CLI and localtunnel
python -m proapi run examples/forwarding_example.py --forward --forward-type localtunnel
```

## Cloudflare Tunnel Example

An example that demonstrates using Cloudflare Tunnel to expose your app to the internet.

```bash
# Run with default settings (Cloudflare Tunnel)
python examples/cloudflare_example.py

# Run with CLI and explicit Cloudflare Tunnel
python -m proapi run examples/cloudflare_example.py --forward --forward-type cloudflare

# Run with authenticated tunnel (requires Cloudflare account)
python -m proapi run examples/cloudflare_example.py --forward --forward-type cloudflare --cf-token YOUR_TOKEN
```
