
from setuptools import setup, Extension, find_packages

m1 = Extension(
    'proapi.internals',
     sources = [ 
      './src/proapi/internals/module.c',
      './src/proapi/internals/utils.c',
      './src/proapi/internals/app.c',
      './src/proapi/internals/protocol.c',
      './src/proapi/internals/mrqprotocol.c',
      './src/proapi/internals/mrqclient.c',
      './src/proapi/internals/memcachedclient.c',
      './src/proapi/internals/memprotocol.c',
      './src/proapi/internals/mrcacheclient.c',
      './src/proapi/internals/mrcacheprotocol.c',
      './src/proapi/internals/parser.c',
      './src/proapi/internals/request.c',
      './src/proapi/internals/response.c',
      './src/proapi/internals/router.c',
      './src/proapi/internals/proapiparser.c',
      #'./src/proapi/cpp/cpptest.cpp'
      './src/proapi/internals/hash/city.c',
      './src/proapi/internals/hash/assoc.c',
      './src/proapi/utils/unpack.c',
     ],
     include_dirs = ['./src/proapi/internals','./src/proapi/utils'],
     extra_compile_args = ['-O3', '-march=native', '-msse4.2', '-mavx2', '-mbmi2', '-Wunused-variable','-std=gnu99','-Wno-discarded-qualifiers', '-Wno-unused-variable','-Wno-unused-function'],
     extra_link_args = [],
     #extra_link_args = ['-lasan'],
     define_macros = []
)

setup(
  name="proapi", 
  version="0.13",
  license='MIT',
  description='A python web framework written in C',
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  ext_modules = [m1],
  package_dir={'':'src'},
  packages=find_packages('src'),# + ['prof'],
  #package_data={'prof': ['prof.so']},
  install_requires=[
    #'uvloop<0.9.0',
    'uvloop>0.9.0',
  ],
  platforms='x86_64 Linux and MacOS X',
  url='http://github.com/MarkReedZ/proapi/',
  author='Mark Reed',
  author_email='markreed99@gmail.com',
  keywords=['web', 'asyncio'],
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Environment :: Web Environment',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: C',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Internet :: WWW/HTTP'
   ]
)

