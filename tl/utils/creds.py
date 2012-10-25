# tl/utils/creds.py
#
#

""" credentials helper funcions. """

# tl feedback

from tl.lib.tlimport import import_byfile
from tl.lib.datadir import getdatadir
from tl.lib.errors import RequireError

## basic imports

import os
import logging

## getcredsfile function

def getcredsmod(datadir=None, doraise=False):
    """ returnd credendtials.py as a module. """
    if not datadir: datadir = getdatadir()
    try:
        mod = import_byfile("credentials", datadir + os.sep + "config" + os.sep + "credentials.py")
        global go
        go = True
    except (IOError, ImportError):
        if doraise: raise RequireError("credentials.py is needed in %s/config dir. see %s/examples" % (datadir, datadir))
        else: logging.warn("credentials.py is needed in %s/config dir. see %s/examples" % (datadir, datadir)) 
        return
    logging.info("found %s credentials" % str(mod))
    return mod
