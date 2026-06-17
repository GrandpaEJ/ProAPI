
from proapi import app

@app.route('/tst', type="text")
def tst(r):
  return "tst"


