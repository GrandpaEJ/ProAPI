from proapi import Application
from proapi import Request
import proapi
import socket

app = Application()

@app.route('/foo')
def foo():
  return 'foo\n'

#@app.route('/',options=['session'])
@app.route('/')
def hello():
  raise proapi.HTTPRedirect("/foo")
  return 'Hello World!'

app.run(debug=True, cores=1)
