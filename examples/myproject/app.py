from proapi import ProAPI

# Create a ProAPI application with debug mode and fast mode enabled
app = ProAPI(debug=True, fast_mode=True)

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

@app.get("/hello/{name}")
def hello(name, request):
    return {"message": f"Hello, {name}!"}

@app.post("/echo")
def echo(request):
    return request.json

# API documentation is automatically available at /.docs

if __name__ == "__main__":
    app.run()
