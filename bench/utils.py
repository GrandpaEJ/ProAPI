
import timeit

setup = u"""
import proapi, cgi
x = 406785442332432
x64 = proapi.to64(x)
txt = u"This is going to be escaped <yay> 你们好"
"""

print ("  ",(min(timeit.Timer('proapi.to64(x)', setup=setup).repeat(100000, 3))))
print ("  ",(min(timeit.Timer('proapi.from64(x64)', setup=setup).repeat(100000, 3))))
print ("  ",(min(timeit.Timer('proapi.escape(txt)', setup=setup).repeat(100000, 3))))
print ("  ",(min(timeit.Timer('cgi.escape(txt)', setup=setup).repeat(100000, 3))))

