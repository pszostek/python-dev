#!/usr/bin/env python

from contextlib import contextmanager
import sys
import functools
import inspect

def _retrieve_args(frame):
    ret = {}
    arginfo = inspect.getargvalues(frame)
    try:
        for arg in arginfo.args:
            if arg in arginfo.locals.keys():
                ret[arg] = arginfo.locals[arg]
        return ret
    except AttributeError:
        return {}

def _call_printer(frame, event, arg, stream, disable_builtin):
    if event != "call":
        return
    co = frame.f_code
    func_name = co.co_name
    if func_name == "write":
        return
    if disable_builtin and func_name.startswith("__"):
        return
    func_filename = co.co_filename
    func_line_no = frame.f_lineno
    caller = frame.f_back
    caller_line_no = caller.f_lineno
    caller_filename = caller.f_code.co_filename
    if (disable_builtin  and (func_filename.startswith("/usr/lib") \
        or caller_filename.startswith("/usr/lib"))):
        return
    args = _retrieve_args(frame)
    #print "args", args
    arg_str = ", ".join("%s=%s" % (k,v) for k,v in args.items())
    print '%s(%s) -> %s(%s): %s(%s)' % \
        (caller_filename, caller_line_no, func_filename, func_line_no, func_name, arg_str)
    return

@contextmanager
def log_calls(stream=None, disable_builtin=True):
    """ 
    >>> def a(n):
    ...     pass
    >>> with log_calls():
    ...     a(2)
    <stdin>(2) -> <stdin>(1):a(n=2)
    """
    if stream is None:
        stream = sys.stdout
    old_trace = sys.gettrace()
    new_trace = functools.partial(_call_printer, stream=stream,\
        disable_builtin=disable_builtin)
    sys.settrace(new_trace)
    yield
    sys.settrace(old_trace)

def _test():
    def b(n, foo=None):
        if n == 1:
            return
        if n % 2 == 1:
            n = 3*n+1
        a(n)
            
    def a(n, bar=True):
        if n % 2 == 0:
            n = n/2
        b(n)

    with log_calls():
        a(100)
        #import re
        #p = re.compile("(a|b)?.*?[^0-9]")

if __name__ == "__main__":
    _test()
