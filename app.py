from proapi import ProAPI

app = ProAPI(debug=True)

@app.get("/")
def index(request):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    import os 
    os.system("proapi run app.py")
