# tl/lib/job.py
#
#

""" provide a Job class, used to follow exec of an command. """

## tl imports

from tl.utils.lazydict import LazyDict

## basic imports

import threading
import logging

## Job class

class Job(LazyDict):

    def __init__(self, *args, **kwargs):
        LazyDict.__init__(self, *args, **kwargs)
        self.__wait = threading.Event()

    def join(self, nrsec=1.0):
        if self.event: return self.event.isready.wait(nrsec)
        self.__wait.wait(nrsec)
        return self.__wait.isSet()

    def done(self): self.__wait.set()
