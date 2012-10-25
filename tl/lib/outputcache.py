# tl/outputcache.py
#
#

## tl imports

from .persist import Persist
from tl.utils.name import stripname
from .datadir import getdatadir
from tl.utils.timeutils import hourmin

## basic imports

import os
import logging
import time

## clear function

def clear(target):
    """ clear target's outputcache. """
    cache = Persist(getdatadir() + os.sep + 'run' + os.sep + 'outputcache' + os.sep + stripname(target))
    try:
        cache.data['msg'] = []
        cache.save()
    except KeyError: pass
    return []

## add function

def add(target, txtlist):
    """ add list of txt to target entry. """
    logging.warn("outputcache - adding %s lines" % len(txtlist))
    t = []
    for item in txtlist:
        t.append("[%s] %s" % (hourmin(time.time()), item))
    cache = Persist(getdatadir() + os.sep + 'run' + os.sep + 'outputcache' + os.sep + stripname(target))
    d = cache.data
    if 'msg' not in d: d['msg'] = []
    d['msg'].extend(t)
    while len(d['msg']) > 10: d['msg'].pop(0)
    cache.save()

## set function

def set(target, txtlist):
    """ set target entry to list. """
    cache = Persist(getdatadir() + os.sep + 'run' + os.sep + 'outputcache' + os.sep + stripname(target))
    if 'msg' not in cache.data: cache.data['msg'] = []
    cache.data['msg'] = txtlist
    cache.save()

## get function

def get(target):
    """ get output for target. """
    logging.warn("get target is %s" % target)
    cache = Persist(getdatadir() + os.sep + 'run' + os.sep + 'outputcache' + os.sep + stripname(target))
    try:
        result = cache.data['msg']
        if result: return result
    except KeyError: pass
    return []
