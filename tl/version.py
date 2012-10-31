# tl/version.py
#
#

""" version related stuff. """

## tl imports


## basic imports

import os
import binascii

## defines

version = "0.4.4"
__version__ = version

## getversion function

def getversion(txt=""):
    """ return a version string. """
    if txt: return "VERSION %s %s" % (version, txt)
    else: return "VERSION %s" % version

def getfullversion(txt="", repo=False):
    v = str(version)
    from tl.lib.config import getmainconfig
    cfg = getmainconfig()
    if cfg.dbenable: v += " -=- " + cfg.dbtype.upper()
    tip = None
    if repo:
        try:
            from mercurial import context, hg, node, repo, ui
            repository = hg.repository(ui.ui(), '.')
            ctx = context.changectx(repository)
            tip = str(ctx.rev())
        except: tip = None
    if tip: version2 = v + " -=- HG " + tip
    else: version2 = v
    return "T I M E L I N E -=- %s -=- %s" % (txt, version2)
