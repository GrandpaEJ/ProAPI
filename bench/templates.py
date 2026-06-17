import multiprocessing
from proapi import Application
from proapi import Request
import proapi
import mrjson as json

import tenjin
tenjin.set_template_encoding('utf-8')
from tenjin.helpers import *
engine = tenjin.Engine(path=['templates'])

app = Application()

@app.route('/')
def t2(r):
  context = { "world":"all you python fanatics out there!" }
  return engine.render('example.ten', context)
   
app.run(cores=4)
