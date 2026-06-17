
import proapi
import json
import asyncio

app = proapi.Application()

@app.route('/json', _type="json")
def j(r):
  #await asyncio.sleep(0.1) 
  return json.dumps({'message': 'Hello, world!'})

@app.route('/', _type="text")
def p(r):
  return "Hello, world!"


app.run('0.0.0.0', 8080)

