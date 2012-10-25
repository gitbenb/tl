# tl/lib/tasks.py
#
#

## tl imports 

from tl.utils.trace import calledfrom
from tl.lib.plugins import plugs
from tl.lib.runner import apirunner
from tl.api.hooks import get_hooks

## basic imports

import logging
import sys

## TaskManager class

class TaskManager(object):

    def __init__(self):
        self.handlers = {}
        self.plugins = {}

    def size(self): return len(self.handlers)

    def add(self, taskname, func):
        """ add a task. """
        logging.debug("tasks - added task %s - %s" % (taskname, func))
        self.handlers[taskname] = func
        plugin = self.plugins[taskname] = calledfrom(sys._getframe())
        plugs.load_mod(plugin)
        return True

    def unload(self, taskname):
        """ unload a task. """
        logging.debug("tasks - unloading task %s" % taskname)
        try:
            del self.handlers[taskname]
            del self.plugins[taskname]
            return True
        except KeyError: return False

    def dispatch(self, taskname, *args, **kwargs):
        """ dispatch a task. """
        try: plugin = self.plugins[taskname]
        except KeyError:
            logging.debug('tasks - no plugin for %s found' % taskname)
            return
        logging.debug('loading %s for taskmanager' % plugin)
        #plugs.load(plugin)
        try: handler = self.handlers[taskname]
        except KeyError:
            logging.debug('tasks - no handler for %s found' % taskname)
            return
        logging.warn("dispatching task %s - %s" % (taskname, str(handler)))
        return handler(*args, **kwargs)

## global task manager

taskmanager = TaskManager()

def handle_task(bot, event):
    try:
        """ this is where the task gets dispatched. """
        path = self.request.path
        if path.endswith('/'): path = path[:-1]
        taskname = path.split('/')[-1].strip()
        logging.warn("using taskname: %s" % taskname)
        inputdict = {}
        for name, value in self.request.environ.iteritems():
            if not 'wsgi' in name:
                inputdict[name] = value
        apirunner.put(5, taskname, taskmanager.dispatch, taskname, inputdict, self.request, self.response)

    except Exception as ex: 
        handle_exception()
        self.response.set_status(500)

get_hooks.register("task", handle_task)
