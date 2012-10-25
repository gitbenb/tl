# tl/exit.py
#
#

""" tl's finaliser """

## tl imports

from tl.utils.locking import globallocked
from tl.utils.exception import handle_exception
from tl.utils.trace import whichmodule
from tl.memcached import killmcdaemon
from tl.lib.persist import cleanup
from .runner import defaultrunner, cmndrunner, callbackrunner, waitrunner

## basic imports

import atexit
import os
import time
import sys
import logging

## functions

@globallocked
def globalshutdown(exit=True):
    """ shutdown the bot. """
    try:
        try: sys.stdout.write("\n")
        except: pass
        txt = "SHUTTING DOWN (%s)" % whichmodule(2)
        logging.error(txt)
        from .fleet import getfleet
        fleet = getfleet()
        if fleet:
            logging.warn('shutting down fleet')
            fleet.exit()
        logging.warn('shutting down plugins')
        from tl.lib.plugins import plugs
        plugs.exit()
        logging.warn("shutting down runners")
        cmndrunner.stop()
        callbackrunner.stop()
        waitrunner.stop()
        logging.warn("cleaning up any open files")
        while cleanup(): time.sleep(1)
        try: os.remove('tl.pid')
        except: pass
        #killmcdaemon()
        logging.warn('done')
        from tl.utils.url import stats
        nr = stats.get("urlnotenabled")
        if nr: logging.error("%s UrlNotEnabled catched" % nr)
        print("")
        if exit: os._exit(0)
        sys.stdout.flush()
    except Exception as ex:
        print("error in exit function: %s" % str(ex))
        if exit: os._exit(1)
