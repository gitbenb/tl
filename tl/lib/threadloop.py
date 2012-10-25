# tl/lib/threadloop.py
#
#

""" class to implement start/stoppable threads. """

## lib imports

from tl.utils.exception import handle_exception
from tl.utils.trace import whichmodule
from tl.utils.lazydict import LazyDict
from .threads import start_new_thread, getname, Thr
from .job import Job
from .errors import URLNotEnabled, TLStop

## basic imports

import queue
import time
import logging
from collections import deque

## ThreadLoop class

class ThreadLoop(Thr):

    """ implement startable/stoppable threads. """

    def __init__(self, name="", q=None, ordered=False, *args, **kwargs):
        Thr.__init__(self, type(self), self._loop, name, args, kwargs)
        self.type = getname(str(type(self)))
        self.name = "%s/%s" % (self.type, name)
        self.fromplug = ""
        self.stopped = False
        self.running = False
        self.outs = []
        self.working = False
        self.curjob = None
        self.curevent = None
        if ordered: self.queue = q or queue.PriorityQueue()
        else: self.queue = q or queue.Queue()
        self.nowrunning = "none"

    def status(self, filter=None):
        todo = ["fromplug", "stopped" , "running", "outs", "working", "queue"]
        res = LazyDict()
        for item  in todo:
            if filter and filter not in item: continue
            value = getattr(self, item)
            if value == None: continue
            if item in ["outs", ]: res[item] = len(value)
            elif item in ["queue", ]: res[item] = value.qsize()
            else: res[item] = str(value)
        return res

    def _loop(self):
        """ the threadloops loop. """
        logging.debug('starting %s' % getname(self))
        self.running = True
        nrempty = 0
        while not self.stopped:
            job = self.queue.get() 
            if job.stop: break
            if self.stopped: break
            try: self.handle(job)
            except TLStop: break
            except Exception as ex: handle_exception()
        self.running = False
        logging.debug('stopping %s' % getname(self))
        
    def put(self, *args, **kwargs):
        """ put data on task queue. """
        job = Job()
        job.args = args
        job.kwargs = kwargs
        self.queue.put(job)
        return job

    def start(self):
        """ start the thread. """
        if not self.running and not self.stopped: Thr.start(self) ; return self
 
    def stop(self):
        """ stop the thread. """
        self.stopped = True
        self.running = False
        logging.debug("stopping %s" % self.name)  
        job = Job()
        job.stop = True
        self.put(job)

    def handle(self, *args, **kwargs):
        """ overload this. """
        pass

## RunnerLoop class

class RunnerLoop(ThreadLoop):

    """ dedicated threadloop for bot commands/callbacks. """

    def _loop(self):
        """ runner loop. """
        logging.debug('starting %s' % self.name)
        self.running = True
        logstr = ""
        fromplug = ""
        while not self.stopped:
            try:
                job = self.queue.get()
                self.curjob = job
                if job.stop: logging.debug("break %s" % self.nowrunning) ; break
                if self.stopped: break
                try:
                    self.curevent = job.event = job.args[4]
                    if job.event.createdfrom: job.fromplug = job.event.createdfrom
                except IndexError: job.fromplug = job.args[1] 
                if not fromplug: job.fromplug = job.args[1]
                self.nowrunning = getname(job.args[2])
                self.working = True
                self.starttime = job.starttime = time.time()
                result = self.handle(job)
                self.finished = job.finished = time.time()
                self.elapsed = job.elapsed = self.finished - self.starttime
                self.working = job.working = False
                logstr = "finished %s %s - %s" % (self.nowrunning, "(%.3f)" % self.elapsed, job.fromplug)
            except TLStop: break
            except URLNotEnabled as ex: logging.warn("url fetching is not enabled - %s" % str(ex)) ; continue
            except IndexError: time.sleep(0.01) ; logging.warn("can't parse data for %s" % str(job)) ; continue
            except Exception as ex:
                handle_exception(self.curevent)
                logging.error("%s - %s" % (self.nowrunning, str(ex)))
                continue
            logging.warn(logstr)
        self.running = False
        self.fromplug = ""
        logging.debug('%s - stopping' % self.name)

class TimedLoop(ThreadLoop):

    """ threadloop that sleeps x seconds before executing. """

    def __init__(self, name, sleepsec=300, *args, **kwargs):
        ThreadLoop.__init__(self, name, *args, **kwargs)
        self.sleepsec = sleepsec

    def _loop(self):
        """ timed loop. sleep a while. """
        logging.warn('%s - starting timedloop (%s seconds)' % (self.name, self.sleepsec))
        self.stopped = False
        self.running = True
        while not self.stopped:
            time.sleep(self.sleepsec)
            if self.stopped: break
            try: self.handle()
            except TLStop: break
            except Exception as ex: handle_exception()
        self.running = False
        logging.warn('stopping %s' % self.name)
