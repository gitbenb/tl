# tl/version.py
#
#

""" version related stuff. """

## tl imports

from tl.lib.config import getmainconfig

## basic imports

import os
import binascii

## defines

version = "0.4.2"
__version__ = version

## getversion function

def getversion(txt=""):
    """ return a version string. """
    if txt: return "VERSION %s %s" % (version, txt)
    else: return "VERSION %s" % version
