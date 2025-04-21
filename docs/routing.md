# Routing in ProAPI

ProAPI provides a simple and intuitive routing system using decorators. This guide explains how to define routes, use path parameters, and handle different HTTP methods.

## Basic Routing

Define routes using decorators that correspond to HTTP methods:

```python
from proapi import ProAPI

app = ProAPI()

@app.get("/")
def index():
    return {"message": "This is a GET request"}

@app.post("/items")
def create_item(request):
    return {"message": "This is a POST request", "data": request.json}

@app.put("/items/{item_id}")
def update_item(item_id, request):
    return {"message": "This is a PUT request", "item_id": item_id, "data": request.json}

@app.delete("/items/{item_id}")
def delete_item(item_id):
    return {"message": "This is a DELETE request", "item_id": item_id}

@app.patch("/items/{item_id}")
def patch_item(item_id, request):
    return {"message": "This is a PATCH request", "item_id": item_id, "data": request.json}
```

## Path Parameters

You can define path parameters in your routes using curly braces:

```python
@app.get("/users/{user_id}")
def get_user(user_id):
    return {"user_id": user_id}
```

### Typed Path Parameters

ProAPI supports typed path parameters:

```python
# Integer parameter
@app.get("/users/{user_id:int}")
def get_user(user_id):
    # user_id will be converted to an integer
    return {"user_id": user_id, "type": type(user_id).__name__}

# Float parameter
@app.get("/items/{price:float}")
def get_item_by_price(price):
    # price will be converted to a float
    return {"price": price, "type": type(price).__name__}

# UUID parameter
@app.get("/resources/{resource_id:uuid}")
def get_resource(resource_id):
    return {"resource_id": resource_id}
```

### Optional Parameters

You can make path parameters optional by adding a question mark:

```python
@app.get("/users/{user_id?}")
def get_user(user_id=None):
    if user_id is None:
        return {"message": "List of all users"}
    return {"user_id": user_id}
```

### Wildcard Parameters

You can use wildcard parameters to match any path:

```python
@app.get("/files/{*path}")
def get_file(path):
    return {"path": path}
```

## Query Parameters

Access query parameters from the request object:

```python
@app.get("/search")
def search(request):
    query = request.get_query_param("q")
    limit = request.get_query_param("limit", 10)  # Default value
    return {"query": query, "limit": limit}
```

## Route Naming and Options

You can provide additional options to routes:

```python
@app.get("/users", name="list_users")
def get_users():
    return {"users": []}

@app.post("/users", name="create_user", description="Create a new user")
def create_user(request):
    return {"user": request.json}
```

## Route Groups and Prefixes

You can create route groups with a common prefix:

```python
# Create a sub-application
api = ProAPI()

# Define routes on the sub-application
@api.get("/users")
def get_users():
    return {"users": []}

@api.get("/items")
def get_items():
    return {"items": []}

# Mount the sub-application with a prefix
app.use(api)  # Routes will be available at /users and /items

# Or mount with a specific prefix
app.use(api, prefix="/api/v1")  # Routes will be available at /api/v1/users and /api/v1/items
```

## Route Matching Order

Routes are matched in the order they are defined. If multiple routes match a request, the first one defined will be used.

## Error Handling

You can handle errors by raising exceptions or returning appropriate responses:

```python
@app.get("/users/{user_id:int}")
def get_user(user_id):
    if user_id <= 0:
        from proapi.server import Response
        return Response(
            status=400,
            body={"error": "Invalid user ID"},
            content_type="application/json"
        )
    
    # Simulate user not found
    if user_id > 100:
        return Response(
            status=404,
            body={"error": "User not found"},
            content_type="application/json"
        )
    
    return {"user_id": user_id, "name": f"User {user_id}"}
```