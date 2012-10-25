# tl/lib/runner.py 
#
#

""" threads management to run jobs. """

## tl imports

from tl.lib.threads import getname, start_new_thread, start_bot_command
from tl.utils.exception import handle_exception
from tl.utils.locking import locked, lockdec
from tl.utils.lockmanager import rlockmanager, lockmanager
from tl.utils.generic import waitevents
from tl.utils.trace import callstack, whichmodule
from tl.utils.statdict import StatDict
from tl.lib.threadloop import RunnerLoop
from tl.lib.callbacks import callbacks
from tl.lib.errors import URLNotEnabled
from .threads import getmod
from tl.utils.lazydict import LazyDict

## basic imports

import queue
import time
import _thread
import random
import logging
import sys

## defines

stats = StatDict()

## Runner class

class Runner(RunnerLoop):

    """
        a runner is a thread with a queue on which jobs can be pushed. 
        jobs scheduled should not take too long since only one job can 
        be executed in a Runner at the same time.

    """

    def __init__(self, name="runner", doready=True):
        RunnerLoop.__init__(self, name)
        self.starttime = time.time()
        self.elapsed = self.starttime
        self.finished = time.time()  
        self.doready = doready
        self.longrunning = [] 
        self.shortrunning = []

    def handle(self, job):
        """ schedule a job. """
        kwargs = job.kwargs
        try: speed, descr, func, *args = job.args
        except ValueError:
            try:
                speed, descr, func = job.args
                args = []
                kwargs = {}
            except ValueError:
                speed, func = jobs.args
                descr = "none"
                args = ()
                kwargs = {}
        res = func(*args, **kwargs)
        elapsed = time.time() - self.starttime
        if elapsed > 5:
            logging.debug('ALERT %s %s job taking too long: %s seconds' % (descr, str(func), elapsed))
        stats.upitem(self.nowrunning)
        stats.upitem(self.type)
        return res

    def done(self, event):
        try: int(event.cbtype)
        except ValueError:
            if event.cbtype not in ['TICK', 'TICK10', 'PING', 'NOTICE', 'TICK60']: logging.warn("done %s" % str(event.cbtype))

## BotEventRunner class

class BotEventRunner(Runner):

    def handle(self, job):
        """ schedule a bot command. """
        speed, descr, func, bot, ievent = job.args
        self.starttime = time.time()
        self.finished = 0
        self.elapsed = 0
        if not ievent.nolog: logging.debug("event handler is %s" % str(func))
        if self.nowrunning in self.longrunning: 
            logging.warn("putting %s on longrunner" % self.nowrunning)
            longrunner.put(job)
            return
        res = func(bot, job.event)
        self.finished = time.time()
        self.elapsed = self.finished - self.starttime
        if self.elapsed > 5:
            if self.nowrunning not in self.longrunning: self.longrunning.append(self.nowrunning)
            if not ievent.nolog: logging.debug('ALERT %s %s job taking too long: %s seconds' % (descr, str(func), self.elapsed))
        return res

class LongRunner(Runner):

    def handle(self, job):
        """ schedule a bot command. """
        speed, descr, func, bot, ievent = job.args
        self.starttime = time.time()
        if not ievent.nolog: logging.debug("long event handler is %s" % str(func))
        res = func(bot, ievent)
        self.elapsed = time.time() - self.starttime
        if self.elapsed < 1 and self.nowrunning not in self.shortrunning: self.shortrunning.append(self.nowrunning)
        return res

## Runners class

class Runners(object):

    """ runners is a collection of runner objects. """

    def __init__(self, name, max=100, runnertype=Runner, doready=True):
        self.name = name
        self.max = max
        self.runners = []
        self.runnertype = runnertype
        self.doready = doready

    def status(self, filter=None):
        res = LazyDict()
        for runner in self.runners: res[runner.name] = runner.status(filter)
        return res.tojson()

    def names(self):
        return [getname(runner.name) for runner in self.runners]

    def size(self):
        qsize = [runner.queue.qsize() for runner in self.runners]
        return "%s/%s" % (qsize, len(self.runners))

    def runnersizes(self):
        """ return sizes of runner objects. """
        result = []
        for runner in self.runners: result.append("%s/%s" % (runner.name, runner.queue.qsize()))
        return result

    def stop(self, name=None, dojoin=False):
        """ stop runners. """
        for runner in self.runners:
            if name and not name in runner.name: continue
            runner.stop()
            if dojoin: runner.join(3.0)

    def start(self):
        """ overload this if needed. """
        pass
 
    def put(self, *data, **kwargs):
        """ put a job on a free runner. """
        for runner in self.runners:
            if runner.queue.empty() and not runner.working:
                return runner.put(*data, **kwargs)
        runner = self.makenew()
        return runner.put(*data, **kwargs)

              
    def running(self):
        """ return list of running jobs. """
        result = []
        for runner in self.runners:
            if runner.running: result.append(runner.nowrunning)
        return result

    def makenew(self):
        """ create a new runner. """
        runner = None
        if len(self.runners) < self.max:
            runner = self.runnertype(self.name + "-" + str(len(self.runners)))
            runner.start()
            self.runners.append(runner)
        else:
            logging.error("%s runner is at max, choosing random runner" % self.name)
            runner = random.choice(self.runners)
        return runner

    def cleanup(self, dojoin=False):
        """ clean up idle runners. """
        r = []
        for runner in self.runners:
            if not runner.running or runner.queue.empty() or not runner.working: r.append(runner)
        if not r: return
        for runner in r:
            if dojoin: runners.stop(runner)
            else: runner.stop()
        for runner in r:
            try: self.runners.remove(runner)
            except ValueError: pass
        logging.debug("%s - cleaned %s" %  (self.name, [item.name for item in r]))
        logging.debug("%s - now running: %s" % (self.name, self.size()))
        return self.size()
        
## global runners

cmndrunner = defaultrunner = Runners("cmnd", 75, BotEventRunner) 
longrunner = Runners("long", 50, LongRunner)
callbackrunner = Runners("callback", 20, BotEventRunner)
waitrunner = Runners("wait", 20, BotEventRunner)
apirunner = Runners("api", 10, BotEventRunner)
threadrunner = Runners("thread", 50, Runner)
urlrunner = Runners("url", 50, Runner)

allrunners = [cmndrunner, longrunner, callbackrunner, waitrunner, apirunner, threadrunner, urlrunner]

## cleanup 

def runnercleanup(bot, event):
    cmndrunner.cleanup()
    longrunner.cleanup()
    callbackrunner.cleanup()
    waitrunner.cleanup()
    apirunner.cleanup()
    threadrunner.cleanup()
    urlrunner.cleanup()

callbacks.add("TICK10", runnercleanup)

def size():
    return "cmnd: %s - callback: %s - wait: %s - long: %s - api: %s - thread: %s" % (cmndrunner.size(), callbackrunner.size(), waitrunner.size(), longrunner.size(), apirunner.size(), threadrunner.size())
