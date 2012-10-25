# tl/imports.py
#
#

""" provide a import wrappers for the contrib packages. """

## lib imports

from tl.lib.tlimport import _import

## basic imports

import logging

## getjson function

def getjson():
    mod = _import("json")
    logging.debug("json module is %s" % str(mod))
    return mod

## getfeedparser function

def getfeedparser():
    try: mod = _import("feedparser")
    except: mod = _import("tl.contrib.feedparser")
    logging.debug("feedparser module is %s" % str(mod))
    return mod

def getoauth():
    try: mod = _import("oauth")
    except:
        mod = _import("tl.contrib.oauth")
    logging.debug("oauth module is %s" % str(mod))
    return mod

def getrequests():
    try: mod = _import("requests")
    except: mod = None
    logging.debug("requests module is %s" % str(mod))
    return mod

def gettornado():
    try:
        mod = _import("tornado")
        if not "site-packages" in str(mod): mod = _import("tl.contrib.tornado")
    except: mod = _import("tl.contrib.tornado")
    logging.debug("tornado module is %s" % str(mod))
    return mod

def getBeautifulSoup():
    try: mod = _import("BeautifulSoup")
    except: mod = _import("tl.contrib.bs4")
    logging.debug("BeautifulSoup module is %s" % str(mod))
    return mod

def getsleek():
    try: mod = _import("sleekxmpp")
    except: mod = _import("tl.contrib.sleekxmpp")
    logging.debug("sleek module is %s" % str(mod))
    return mod

def gettweepy():
    try: mod = _import("tweepy")
    except: mod = _import("tl.contrib.tweepy")
    logging.info("tweepy module is %s" % str(mod))
    return mod
