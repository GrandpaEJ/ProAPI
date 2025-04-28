from proapi import ProAPI

# Create a ProAPI application with debug mode enabled
app = ProAPI(debug=True)

@app.get("/")
def index(request):
    return {"message": "Hello from ProAPI!"}

@app.get("/hello/{name}")
def hello(name, request):
    return {"message": f"Hello, {name}!"}

@app.post("/echo")
def echo(request):
    return request.json

# API documentation is automatically available at /.docs

if __name__ == "__main__":
    app.run(port=8080)
