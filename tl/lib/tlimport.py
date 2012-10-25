# tl/lib/tlimport.py
#
#

""" use the imp module to import modules. """

## basic imports

import time
import sys
import imp
import os
import _thread
import logging

## _import function

def _import(name):
    """ do a import (full). """
    if not name: raise Exception(name)
    logging.info("importing %s" % name)
    res = __import__(name)
    return sys.modules[name]


def silent_import(name):
    from tl.utils.exception import exceptionmsg
    try: return _import(name)
    except Exception as ex: logging.error(exceptionmsg())

## force_import function

def force_import(name):
    """ force import of module <name> by replacing it in sys.modules. """
    try: del sys.modules[name]
    except KeyError: pass
    plug = _import(name)
    return plug

def import_byfile(modname, filename):
    logging.info("importing %s" % filename)
    try: return imp.load_source(modname, filename)
    except NotImplementedError: return _import(filename[:-3].replace(os.sep, "."))

