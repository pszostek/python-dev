#!/usr/bin/env python

from contextlib import contextmanager
import sys
import functools
import inspect

def _retrieve_args(frame):
    """retrieves function arguments from given frame

    @param frame current stack frame
    @returns dictionary with argument names as keys
    """ 
    ret = {}
    arginfo = inspect.getargvalues(frame)
    try:
        for arg in arginfo.args:
            if arg in arginfo.locals.keys():
                ret[arg] = arginfo.locals[arg]
        return ret
    except AttributeError: #for some reason sometimes this error is raised
        return {}

def _call_printer(frame, event, arg, stream, disable_builtin,\
    print_args, short_fnames):
    """prints details about the caller and callee function for 'call' events

    @param frame required by sys.settrace()
    @param event required by sys.settrace()
    @param arg required by sys.settrace()
    @param stream an object offering 'write' method
    @param disable_builtin indicates if standard python functions
           should be printed
    @param print_args indicates whether print function arguments
    """
    if event != "call": #we are interested in function calls only
        return
    co = frame.f_code
    callee_name = co.co_name
    callee_filename = co.co_filename
    callee_line_no = frame.f_lineno
    caller = frame.f_back
    caller_line_no = caller.f_lineno
    caller_filename = caller.f_code.co_filename
    if short_fnames:
        callee_filename = callee_filename.split('/')[-1]
        caller_filename = caller_filename.split('/')[-1]
    if callee_name == "write": #omit self-recursion in prints
        return
    if disable_builtin and callee_name.startswith("__"): #omit magic functions
        return
    if (disable_builtin  and (callee_filename.startswith("/usr/lib") \
        #assume that builtins are in /usr/lib
        or caller_filename.startswith("/usr/lib"))): 
        return
    args = _retrieve_args(frame)
    if print_args:
        arg_str = ", ".join("%s=%s" % (k,v) for k,v in args.items())
    else:
        arg_str = ""
    print '%s(%s) -> %s(%s): %s(%s)' % \
        (caller_filename, caller_line_no, callee_filename,
            callee_line_no, callee_name, arg_str)
    return

@contextmanager
def log_calls(stream=None, disable_builtin=True, print_args=False, short_fnames=False):
    """ 
    Context manager for call tracing within its block
    @param stream an object offering 'write' method
    @param disable_builtin indicates if standard python functions
           should be printed
    @param print_args indicates whether function arguments should be printed
    @param short_fnames indicated whether to print whole file paths
           or just its names

    A very trivial usage example:
    >>> def a(n):
    ...     if n: b(n-1)
    >>> def b(n):
    ...     if n: a(n-1)
    >>> with log_calls():
    ...     a(10)
    ...
    <stdin>(2) -> <stdin>(1): a(n=10)
    <stdin>(2) -> <stdin>(1): b(n=9)
    <stdin>(2) -> <stdin>(1): a(n=8)
    <stdin>(2) -> <stdin>(1): b(n=7)
    <stdin>(2) -> <stdin>(1): a(n=6)
    <stdin>(2) -> <stdin>(1): b(n=5)
    <stdin>(2) -> <stdin>(1): a(n=4)
    <stdin>(2) -> <stdin>(1): b(n=3)
    <stdin>(2) -> <stdin>(1): a(n=2)
    <stdin>(2) -> <stdin>(1): b(n=1)
    <stdin>(2) -> <stdin>(1): a(n=0)
    """
    assert (stream is None) or hasattr(stream, "write")
    assert isinstance(disable_builtin, bool)
    assert isinstance(print_args, bool)
    assert isinstance(short_fnames, bool)
    if stream is None:
        stream = sys.stdout
    old_trace = sys.gettrace()
    new_trace = functools.partial(_call_printer, stream=stream,\
        disable_builtin=disable_builtin, print_args=print_args,\
        short_fnames=short_fnames)
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
