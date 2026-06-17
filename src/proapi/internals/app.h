#pragma once

#include <Python.h>
#include <stdbool.h>

typedef struct Protocol Protocol;
typedef struct Request Request;

typedef struct {
  Protocol *protocol;
  Request  *request;
} SessionCallbackData;

typedef void (*tSessionCallback)(void*, char*, int);
typedef int (*tSessionClientGet)(void*, char*, void*, void*);

#include "memcachedclient.h"

typedef struct {
  PyObject_HEAD
  
  // Idle timeouts
  PyObject *connections;
  PyObject* call_later;
  PyObject* check_idle;
  PyObject* check_idle_handle;
  PyObject* check_interval;
  PyObject* loop;

  // Custom error pages
  PyObject* err404;
  PyObject* err400;

  // Request pool
  PyObject *func_expand_requests;
  PyObject *requests;
  //Request **requests;
  int numRequests, nextRequest,freeRequests; 
  //int numGets, numReleases;

  // Clients
  PyObject *py_mc;
  PyObject *py_mrq;
  PyObject *py_mrq2;
  PyObject *py_mrc;
  PyObject *py_redis;
  PyObject *py_session_backend_type; // int 1,2,3 ( memcached, mrworkserver, mrcache )
  PyObject *py_session; // points to mc, mrq, or mrcache

  tSessionClientGet session_get;

} ProAPIApp;

PyObject *ProAPIApp_new    (PyTypeObject* self, PyObject *args, PyObject *kwargs);
int       ProAPIApp_init   (ProAPIApp* self,    PyObject *args, PyObject *kwargs);
void      ProAPIApp_dealloc(ProAPIApp* self);

PyObject *ProAPIApp_cinit(ProAPIApp* self);

void ProAPIApp_release_request(ProAPIApp* self, Request *r);
PyObject *ProAPIApp_get_request(ProAPIApp* self);

PyObject *ProAPIApp_updateDate(ProAPIApp *self, PyObject *date);
PyObject *ProAPIApp_check_idle(ProAPIApp *self);
PyObject *ProAPIApp_test_fut(ProAPIApp *self);

void ProAPIApp_setup_error_pages(ProAPIApp* self);
