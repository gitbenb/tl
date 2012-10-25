# tl/lib/eventhandler.py
#
#

""" event handler. use to dispatch function in main loop. """

## tl imports

from tl.utils.exception import handle_exception
from tl.utils.locking import lockdec
from .threads import start_new_thread
from .errors import TLStop
from .exit import globalshutdown

## basic imports

import queue
import _thread
import logging
import time

## locks

handlerlock = _thread.allocate_lock()
locked = lockdec(handlerlock)

## classes

class EventHandler(object):

    """
        events are handled in 11 queues with different priorities:
        queue0 is tried first queue10 last.

    """

    def __init__(self, ordered=False):
        self.sortedlist = []
        if ordered: self.queue = queue.PriorityQueue()
        else: self.queue = queue.Queue()
        self.stopped = False
        self.running = False
        self.nooutput = False

    def start(self):
        """ start the eventhandler thread. """
        self.stopped = False
        if not self.running:
            start_new_thread(self.handleloop, ())
            self.running = True

    def handle_one(self):
        try:
            speed, todo = self.queue.get_nowait()
            if self.stopped: raise KeyboardInterrupt
            self.dispatch(todo)
        except queue.Empty: pass

    def stop(self):
        """ stop the eventhandler thread. """
        self.running = False
        self.stopped = True
        self.put(None, None)

    def exitandclose(self):
        self.stop()
        globalshutdown()

    def put(self, speed, func, *args, **kwargs):
        """ put item on the queue. """
        self.queue.put_nowait((speed, (func, args, kwargs)))

    def handleloop(self):
        """ thread that polls the queues for items to dispatch. """
        logging.warn('starting - %s ' % str(self))
        while not self.stopped:
            try:
                (speed, todo) = self.queue.get()
                if speed == None or todo == None: break
                logging.warn("running at speed %s - %s" % (speed, str(todo)))
                self.dispatch(todo)
            except queue.Empty: time.sleep(0.1)
            except Exception as ex: handle_exception()
        logging.warn('stopping - %s' % str(self))

    runforever = handleloop

    def dispatch(self, todo):
        """ dispatch functions from provided queue. """
        try:
            (func, args, kwargs) = todo
            func(*args, **kwargs)
        except ValueError:
            try:
                (func, args) = todo
                func(*args)
            except ValueError:
                (func, ) = todo
                func()
        except: handle_exception()


## handler to use in main prog

mainhandler = EventHandler()
