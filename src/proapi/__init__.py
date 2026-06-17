# ProAPI — based on mrhttp by Mark Reed (https://github.com/MarkReedZ/mrhttp)
# All credit for the original C engine and design to Mark Reed.
# mrpacker serialization merged from https://github.com/MarkReedZ/mrpacker by Mark Reed.
# mrjson JSON encoder/decoder from https://github.com/MarkReedZ/mrjson by Mark Reed.

from .internals import Protocol
from .internals import Request as CRequest
from .internals import Response
from .internals import Router as CRouter
from .internals import ProAPIApp as CApp
from .httputil import HTTPError, HTTPRedirect

from .internals import MemcachedProtocol
from .internals import MemcachedClient as CMemcachedClient
from .memcachedclient import MemcachedClient

from .internals import MrqProtocol
from .internals import MrqClient as CMrqClient
from .mrqclient import MrqClient 

from .internals import MrcacheProtocol
from .internals import MrcacheClient as CMrcacheClient
from .mrcacheclient import MrcacheClient 

from .app import *
from .internals import randint, escape, to64, from64, timesince, pack, unpack

# mrjson JSON — bundled as proapi._mrjson
from . import _mrjson
dumps = _mrjson.dumps
dumpb = _mrjson.dumpb
dump  = _mrjson.dump
loads = _mrjson.loads
loadb = _mrjson.loadb
load  = _mrjson.load

__version__="1.0.0"

