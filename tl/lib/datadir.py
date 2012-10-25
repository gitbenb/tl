# tl/datadir.py
#
#

""" the data directory of the bot. """

## tl imports

from tl.utils.source import getsource

## basic imports

import re
import os
import shutil
import logging
import os.path
import getpass

## the global datadir

try: homedir = os.path.abspath(os.path.expanduser("~"))
except: homedir = os.getcwd()

datadir = homedir + os.sep + ".tl"

## helper functions

def touch(fname):
    """ touch a file. """
    fd = os.open(fname, os.O_WRONLY | os.O_CREAT)
    os.close(fd)

def doit(ddir, mod, target=None):
    source = getsource(mod)
    if not source: raise Exception("can't find %s package" % mod)
    shutil.copytree(source, ddir + os.sep + (target or mod.replace(".", os.sep)))


## makedir function

def makedirs(ddir=None):
    """ make subdirs in datadir. """
    global datadir
    datadir = ddir or getdatadir()
    logging.warn("datadir - set to %s" % datadir)
    if not os.path.isdir(ddir):
        try: os.mkdir(ddir)
        except:
             raise Exception("can't make %s dir" % ddir)
        logging.info("making dirs in %s" % ddir)
    try: os.chmod(ddir, 0o700)
    except: pass
    if ddir: setdatadir(ddir)
    last = datadir.split(os.sep)[-1]
    if not os.path.exists(ddir + os.sep + "__init__.py"):
        try: touch(ddir + os.sep + "__init__.py")
        except: pass
    try:
        os.mkdir(ddir + os.sep + "config")
        touch(ddir + os.sep + "config" + os.sep + "__init__.py")
    except: pass
    # examples
    try: doit(ddir, "tl.examples", "examples")
    except Exception as ex: pass
    # myplugs
    initsource = getsource("tl.plugs")
    if not initsource: raise Exception("can't find tl.plugs package")
    initsource = initsource + os.sep + "__init__.py"
    if not os.path.isdir(ddir + os.sep + 'myplugs'):
        os.mkdir(ddir + os.sep + 'myplugs')
        try: shutil.copy(initsource, ddir + os.sep + "myplugs" + os.sep + "__init__.py")
        except: pass
    # tl-myplugs
    if os.path.isdir('tl'):
        if not os.path.isdir('tl-myplugs'):
            os.mkdir('tl-myplugs')
            try: shutil.copy(initsource, "tl-myplugs" + os.sep + "__init__.py")
            except: pass
    if not os.path.isdir(ddir + '/timeline/'): os.mkdir(ddir + '/timeline/')
    if not os.path.isdir(ddir + '/run/'): os.mkdir(ddir + '/run/')
    if not os.path.isdir(ddir + '/twitter/'): os.mkdir(ddir + '/twitter/')
    if not os.path.isdir(ddir + '/users/'): os.mkdir(ddir + '/users/')
    if not os.path.isdir(ddir + '/channels/'): os.mkdir(ddir + '/channels/')
    if not os.path.isdir(ddir + '/fleet/'): os.mkdir(ddir + '/fleet/')
    if not os.path.isdir(ddir + '/pgp/'): os.mkdir(ddir + '/pgp/')
    if not os.path.isdir(ddir + '/plugs/'): os.mkdir(ddir + '/plugs/')
    if not os.path.isdir(ddir + '/old/'): os.mkdir(ddir + '/old/')
    if not os.path.isdir(ddir + '/containers/'): os.mkdir(ddir + '/containers/')
    if not os.path.isdir(ddir + '/chatlogs/'): os.mkdir(ddir + '/chatlogs/')
    if not os.path.isdir(ddir + '/botlogs/'): os.mkdir(ddir + '/botlogs/')
    if not os.path.isdir(ddir + '/spider/'): os.mkdir(ddir + '/spider/')
    if not os.path.isdir(ddir + '/spider/data/'): os.mkdir(ddir + '/spider/data')
    if os.path.isfile(ddir + '/globals'):
        try: os.rename(ddir + '/globals', ddir + '/globals.old')
        except: pass
    if not os.path.isdir(ddir + '/globals/'): os.mkdir(ddir + '/globals/')

## initdirs funcion

def makeplugs():
    from tl.lib.fleet import getfleet
    from tl.lib.plugins import plugs
    plugs.loadall(force=True)
    plugs.save()
    fleet = getfleet()
    fleet.loadall()
    fleet.save()   

## makeconfigs function

def makeconfigs():
    from tl.lib.config import makedefaultconfig
    fleet = getfleet()
    makedefaultconfig('irc', ddir)
    fleet.addnametype("default-irc", "irc")
    makedefaultconfig('sleek', ddir)
    fleet.addnametype("default-sleek", "sleek")

## getdatadir function

def getdatadir():
    global datadir
    return datadir

## getdatadirstr function

def getdatadirstr(stripname=False):
    result = getdatadir()
    if stripname:
        from tl.utils.name import stripname
        result = stripname(result)
    return result

## setdatadir function

def setdatadir(ddir):
    global datadir
    datadir = ddir
