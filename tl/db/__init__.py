# tl/db/__init__.py
#
#

""" main db package """

## tl imports

from tl.utils.exception import handle_exception

## basic imports

import logging

## gotsqlite function

def gotsqlite():
    try: import sqlite3 ; return True
    except ImportError:
        try: import _sqlite3 ; return True
        except ImportError: return False

## getmaindb function

db = None

def getmaindb():
    try:
        from tl.lib.config import getmainconfig
        cfg = getmainconfig()
        if cfg.dbenable:
            if "sqlite" in cfg.dbtype and not gotsqlite():
                logging.error("sqlite is not found.")
                return
            global db
            if db: return db
            from .direct import Db
            return Db()
        else: raise Exception("db not enabled in %s" % cfg._cfile)
    except Exception as ex: handle_exception()
