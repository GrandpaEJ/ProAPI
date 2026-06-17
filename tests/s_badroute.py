from proapi import Application
from proapi import Request
import proapi
import socket

app = Application()

@app.route('/foo/{}/{}')
def foo2(r, foo, bar, baz):
  return 'Hello World!'

app.run(cores=1)

