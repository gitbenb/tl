# tl/persist.py
#
#

"""
    allow data to be written to disk or BigTable in JSON format. creating 
    the persisted object restores data. 

"""

## tl imports

from tl.utils.trace import whichmodule, calledfrom, callstack, where
from tl.utils.lazydict import LazyDict
from tl.utils.exception import handle_exception
from tl.utils.name import stripname, reversename, stripdatadir
from tl.utils.locking import lockdec
from tl.utils.timeutils import elapsedstring
from tl.lib.callbacks import callbacks
from tl.lib.errors import MemcachedCounterError, JSONParseError
from tl.id import get_pid
from .datadir import getdatadir

## simplejson imports

from tl.imports import getjson
json = getjson()

## basic imports

from errno import ENOENT, EAGAIN, EEXIST
from collections import deque
import _thread
import logging
import os
import os.path
import types
import copy
import sys
import time

## defines

cpy = copy.deepcopy

## locks


persistlock = _thread.allocate_lock()
persistlocked = lockdec(persistlock)

## global list to keeptrack of what persist objects need to be saved

needsaving = deque()

def cleanup(bot=None, event=None):
    global needsaving
    #todo = cpy(needsaving)
    r = []
    for p in needsaving:
        try: p.dosave() ; r.append(p) ; logging.warn("saved on retry - %s" % p.fn)
        except (OSError, IOError) as ex: logging.error("failed to save %s - %s" % (p, str(ex)))
    for p in r:
        try: needsaving.remove(p)
        except ValueError: pass
    return needsaving


got = False
#from tl.memcached import getmc
#mc = getmc()
#if mc:
#    status = mc.get_stats()
#    if status:
#        logging.warn("memcached uptime is %s" % elapsedstring(status[0][1]['uptime']))
#        got = True
#else: logging.debug("no memcached found - using own cache")
from .cache import get, set, delete

import fcntl

## classes

class Persist(object):

    """ persist data attribute to JSON file. """
        
    def __init__(self, filename, default=None, init=True, postfix=None):
        """ Persist constructor """
        filename = filename.replace("//", "/")
        self.origname = filename
        if postfix: self.fn = str(filename.strip()) + str("-%s" % postfix)
        else: self.fn = str(filename.strip())
        self.lock = _thread.allocate_lock() # lock used when saving
        self.data = LazyDict(default=default) # attribute to hold the data
        self.logname = reversename(stripdatadir(self.origname))
        self.pid = get_pid(self)
        self.countername = self.fn + "_" + "counter"
        if got:
            count = mc.get(self.countername)
            try: self.mcounter = self.counter = int(count)
            except (ValueError, TypeError): self.mcounter = self.counter = mc.set(self.countername, "1") or 0
        else: self.mcounter = self.counter = 0
        self.ssize = 0
        self.jsontxt = ""
        self.dontsave = False
        if init:
            self.init(default)
            if default == None: default = LazyDict()

    def size(self):
        return "%s (%s)" % (len(self.data), len(self.jsontxt))

    def init(self, default={}, filename=None):
        """ initialize the data. """
        gotcache = False
        cachetype = "cache"
        try:
            #logging.debug("using name %s" % self.fn)
            a = get(self.fn)
            if a: self.data = a
            else: self.data = None
            if self.data != None:
                logging.debug("got data from local cache")
                return self
            if got: self.jsontxt = mc.get(self.fn) ; cachetype = "cache"
            if not self.jsontxt:
               datafile = open(self.fn, 'r')
               self.jsontxt = datafile.read()
               datafile.close()
               self.ssize = len(self.jsontxt)
               cachetype = "file"
               if got: mc.set(self.fn, self.jsontxt)
        except IOError as ex:
                if not ex.errno == ENOENT:
                    logging.error('failed to read %s: %s' % (self.fn, str(ex)))
                    raise
                else:
                    logging.debug("%s is new - setting to %s" % (self.fn, default))
                    self.jsontxt = json.dumps(default)
        try:
            if self.jsontxt:
                #logging.debug("loading: %s" % type(self.jsontxt))
                try: self.data = json.loads(str(self.jsontxt))
                except Exception as ex: logging.error("ERROR: %s - couldn't parse %s" % (str(ex), self.jsontxt)) ; self.data = None ; self.dontsave = True
            if not self.data: self.data = LazyDict()
            elif type(self.data) == dict:
                logging.debug("converting dict to LazyDict")
                d = LazyDict()
                d.update(self.data)
                self.data = d
            set(self.fn, self.data)
            logging.info("loaded %s - %s" % (self.logname, cachetype))
        except Exception as ex:
            logging.error('ERROR: %s' % self.fn)
            raise

    def upgrade(self, filename):
        self.init(self.data, filename=filename)
        self.save(filename)

    def get(self):
        #logging.debug("getting %s from local cache" % self.fn)
        a = get(self.fn)
        #logging.debug("got %s from local cache" % type(a))
        return a

    def sync(self):
        logging.debug("syncing %s" % self.fn)
        if got: mc.set(self.fn, json.dumps(self.data))
        set(self.fn, self.data)
        return self

    def save(self):
        cleanup()
        global needsaving
        try: self.dosave()
        except (IOError, OSError):
            self.sync()
            if self not in needsaving: needsaving.append(self)

    @persistlocked
    def dosave(self):
        """ persist data attribute. """
        #logging.debug("trying to save %s" % self.fn)
        try:
            if self.dontsave: logging.error("dontsave is set on  %s - not saving" % self.fn) ; return
            fn = self.fn
            if got: self.mcounter = int(mc.incr(self.countername))
            if got and (self.mcounter - self.counter) > 1:
                tmp = json.loads(mc.get(fn))
                if tmp:
                    try: tmp.update(self.data) ; self.data = LazyDict(tmp) ; logging.warn("updated %s" % fn)
                    except AttributeError: pass
                self.counter = self.mcounter
            d = []
            if fn.startswith(os.sep): d = [os.sep,]
            for p in fn.split(os.sep)[:-1]:
                if not p: continue
                d.append(p)
                pp = os.sep.join(d)
                if not os.path.isdir(pp):
                    logging.warn("creating %s dir" % pp)
                    os.mkdir(pp)
            tmp = fn + '.tmp' # tmp file to save to
            datafile = open(tmp, 'w')
            fcntl.flock(datafile, fcntl.LOCK_EX | fcntl.LOCK_NB)
            json.dump(self.data, datafile, indent=True)
            fcntl.flock(datafile, fcntl.LOCK_UN)
            datafile.close()
            try: os.rename(tmp, fn)
            except (IOError, OSError):
                os.remove(fn)
                os.rename(tmp, fn)
            jsontxt = json.dumps(self.data)
            #logging.debug("setting cache %s - %s" % (fn, jsontxt))
            self.jsontxt = jsontxt
            set(fn, self.data)
            if got: mc.set(fn, jsontxt)
            logging.warn('%s saved' % self.logname)
        except IOError as ex: logging.error("not saving %s: %s" % (self.fn, str(ex))) ; raise
        except: raise
        finally: pass

## findfilenames function 

def findfilenames(target, filter=[], skip=[]):
    res = []
    if not os.path.isdir(target): return res
    for f in os.listdir(target):
        if f in skip: continue
        fname = target + os.sep + f
        if os.path.isdir(fname): res.extend(findfilenames(fname, skip))
        go = True
        for fil in filter:
            if fil.lower() in fname.lower(): go = False ; break
        if not go: continue
        res.append(fname)
    return res

def findnames(target, filter=[], skip=[]):
    res = []
    for f in findfilenames(target, filter, skip):
        res.append(f.split(os.sep)[-1])
    return res


class PlugPersist(Persist):

    """ persist plug related data. data is stored in jsondata/plugs/{plugname}/{filename}. """

    def __init__(self, filename, default={}, *args, **kwargs):
        plugname = calledfrom(sys._getframe())
        Persist.__init__(self, getdatadir() + os.sep + 'plugs' + os.sep + stripname(plugname) + os.sep + stripname(filename), default=default, *args, **kwargs)

class TimedPersist(Persist):

    """ persist that incorporates the create time in the filename. """

    def __init__(self, filename, default={}, ddir=None, *args, **kwargs):
        ddir = ddir or getdatadir()
        timed = time.time()
        timedstr = time.ctime(timed)
        Persist.__init__(self, ddir + os.sep + "%s-%s" % (timedstr, stripname(filename)), default=default, *args, **kwargs)
        self.data.created = timed
        self.data.createdstr = timedstr
 
class GlobalPersist(Persist):

    """ persist plug related data. data is stored in jsondata/plugs/{plugname}/{filename}. """

    def __init__(self, filename, default={}, *args, **kwargs):
        if not filename: raise Exception("filename not set in GlobalPersist")
        #logging.warn("filename is %s" % filename)
        Persist.__init__(self, getdatadir() + os.sep + 'globals' + os.sep + stripname(filename), default=default, *args, **kwargs)

## PersistCollection class

class PersistCollection(object):

    """ maintain a collection of Persist objects. """

    def __init__(self, path, *args, **kwargs):
        assert path
        path = path.replace("//", "/")
        self.path = path
        if not self.path.startswith(os.sep): d = [os.sep, ]
        else: d = []
        for p in path.split(os.sep):
            if not p: continue
            d.append(p)
            pp = os.sep.join(d)
            try: os.mkdir(pp)
            except OSError as ex:
                if ex.errno in [EAGAIN, ENOENT, EEXIST]: continue
                logging.warn("can't make %s - %s" % (pp,str(ex))) ; continue
            logging.warn("created %s dir" % pp)

    def __iter__(self):
        return iter(self.objects().values())
                
    def filenames(self, filter=[], path=None, skip=[], result=[]):
        target = path or self.path
        res = findfilenames(target, filter, skip)
        logging.info("filenames are %s" % str(res))
        return res

    def names(self, filter=[], path=None, skip=[], result=[]):
        target = path or self.path
        res = findnames(target, filter, skip)
        return res

    def search(self, field, target):
        res = []
        for obj in list(self.objects().values()):
            try: item = getattr(obj.data, field)
            except AttributeError: handle_exception() ; continue
            if not item: continue
            if target in item: res.append(obj)
        return res
            
    def objects(self, filter=[], path=None, sorton=""):
        if type(filter) != list: filter = [filter, ] 
        res = {}
        target = path or self.path
        for f in self.filenames(filter, target):
             res[f] = Persist(f)
        return res

    def dosort(self):
        result = list(self.objects().values())
        result.sort(key=lambda i: i.data.created)
        return iter(result)

## PlugPersistCollection class

class PlugPersistCollection(PersistCollection):

    def __init__(self):
        plugname = calledfrom(sys._getframe())
        self.path =  getdatadir() + os.sep + 'plugs' + os.sep + stripname(plugname) + os.sep
        PersistCollection.__init__(self, self.path)

## TimedPersistCollection class

class TimedPersistCollection(PersistCollection):

    def __init__(self, ddir):
        plugname = calledfrom(sys._getframe())
        PersistCollection.__init__(self, ddir)

## GlobalPersistCollection class

class GlobalPersistCollection(PersistCollection):

    def __init__(self):
        self.path =  getdatadir() + os.sep + 'globals'
        GlobalCollection(self, self.path)

callbacks.add("TICK60", cleanup)
