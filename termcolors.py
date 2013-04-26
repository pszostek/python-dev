#!/usr/bin/env python

def red(text):
    return ''.join(['\033[91m', text, '\033[0m'])

def blue(text):
    return ''.join(['\033[94m', text, '\033[0m'])

def green(text):
    return ''.join(['\033[92m', text, '\033[0m'])

def yellow(text):
    return ''.join(['\033[93m', text, '\033[0m'])