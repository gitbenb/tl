# tl/utils/lockmanager.py
#
#

""" manages locks """

## basic imports

import _thread
import threading
import logging

## LockManager class

class LockManager(object):

    """ place to hold locks """

    def __init__(self):
        self.locks = {}

    def allocate(self, name):
        """ allocate a new lock """
        self.locks[name] = _thread.allocate_lock()
        logging.debug('lockmanager - allocated %s' % name)
        
    def get(self, name):
        """ get lock """
        if name not in self.locks: self.allocate(name)
        return self.locks[name]
        
    def delete(self, name):
        """ delete lock """
        if name in self.locks: del self.locks[name]

    def acquire(self, name):
        """ acquire lock """
        if name not in self.locks: self.allocate(name)
        logging.debug('lockmanager - *acquire* %s' % name)
        self.locks[name].acquire()

    def release(self, name):
        """ release lock """
        logging.debug('lockmanager - *releasing* %s' % name)
        try: self.locks[name].release()
        except RuntimeError: pass

## RLockManager class

class RLockManager(LockManager):

    def allocate(self, name):
        """ allocate a new lock """
        self.locks[name] = threading.RLock()
        logging.debug('lockmanager - allocated RLock %s' % name)

## global lockmanagers

lockmanager = LockManager()
rlockmanager = RLockManager()
