# tl/utils/path.py
#
#

""" path manipulation funcions. """

## basic import

import os

## homedir function

def homedir():
    """ try to locate the homedir .. otherwise return current working directory. """
    try: homedir = os.path.abspath(os.path.expanduser("~"))
    except: homedir = os.getcwd()
    return homedir

## absdir function

def absdir(d):
    """ return a normalized directory. """
    return os.path.abspath(d)

## normdir function

def normdir(d):
    """ return a normalized directory. """
    return os.path.normpath(d)

## reldir function

def reldir(d, to=None):
    """ return directory relative to the homedir (or provided directory). """
    return os.path.relpath(normdatadir, to or homedir)
    