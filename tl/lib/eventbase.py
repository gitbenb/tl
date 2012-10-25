# tl/lib/eventbase.py
#
#

""" base class of all events.  """

## tl imports

from .channelbase import ChannelBase
from tl.utils.lazydict import LazyDict
from tl.utils.generic import splittxt, stripped, waitforqueue
from .errors import NoSuchUser, NoSuchCommand, RequireError
from tl.utils.opts import makeeventopts
from tl.utils.trace import whichmodule, whichplugin
from tl.utils.exception import handle_exception
from tl.utils.locking import lockdec
from tl.lib.config import Config, getmainconfig
from tl.lib.users import getusers
from tl.lib.commands import cmnds
from tl.lib.floodcontrol import floodcontrol
from tl.drivers.sleek.namespace import attributes, subelements
from tl.id import get_uid

## basic imports

from collections import deque
from xml.sax.saxutils import unescape, escape
import copy
import logging
import queue
import types
import socket
import threading
import time
import _thread
import urllib.request, urllib.parse, urllib.error
import uuid

## defines

cpy = copy.deepcopy
lock = _thread.allocate_lock()
locked = lockdec(lock)

## classes

class EventBase(LazyDict):

    """ basic event class. """

    def __init__(self, input={}, bot=None, parsetxt=None):
        LazyDict.__init__(self)
        if bot: self.bot = bot 
        self.ctime = time.time()
        self.speed = 5
        self.nrout = 0
        self.nodispatch = True
        self.isready = threading.Event()
        self.dontbind = self.bot and self.bot.cfg and self.bot.cfg.strict or False
        if parsetxt: self.parse(parsetxt)
        if input: self.copyin(input)
        if not self.token: self.setup()

    def copyin(self, eventin):
        """ copy in an event. """
        self.update(eventin)
        return self

    def setup(self):
        self.token = self.token or str(uuid.uuid4().hex)
        self.finished = threading.Condition()
        self.busy = deque()
        self.inqueue = deque()
        self.outqueue = deque()
        self.resqueue = deque()
        self.ok = threading.Event()
        self.setupdone = True
        return self

    def __deepcopy__(self, a):
        """ deepcopy an event. """
        e = EventBase(self)
        return e

    def launched(self):
        logging.info(str(self))
        self.ok.set()

    def startout(self):
        if not self.nodispatch and not self.token in self.busy: self.busy.append(self.token)

    def ready(self, what=None, force=False):
        """ signal the event as ready - push None to all queues. """
        if self.threaded and self.untildone: return
        if self.nodispatch: return
        if not "TICK" in self.cbtype: logging.info(self.busy)
        try: self.busy.remove(self.token)
        except ValueError: pass
        if not self.busy or force: self.notify()
         
    def notify(self, p=None):
        self.finished.acquire()
        self.finished.notifyAll()
        self.isready.set()
        self.finished.release()
        if not "TICK" in self.cbtype: logging.info("notified %s" % str(self))

    def execwait(self, direct=False):
        from tl.lib.commands import cmnds
        e = self.bot.put(self)
        if e: return e.wait()
        else: logging.info("no response for %s" % self.txt) ; return
        logging.info("%s wont dispatch" % self.txt)

    def wait(self, nr=1000):
        nr = int(nr)
        result = []
        if not self.busy: self.startout()
        self.finished.acquire()
        if self.threaded and self.untildone:
            logging.info("waiting until done")
            while 1: self.finished.wait(0.1)
        else:
            while nr > 0 and (self.busy and not self.dostop): self.finished.wait(0.1) ; nr -= 100
        self.finished.release()
        if self.dowait and self.thread: logging.warn("joining thread %s" % self.thread) ; self.thread.join(nr/1000)
        if not "TICK" in self.cbtype: logging.info(self.busy)
        if not self.resqueue: res = waitforqueue(self.resqueue, nr)
        else: res = self.resqueue
        return list(res)

    join = wait

    def waitandout(self, nr=1000):
        res = self.wait(nr)
        if res: 
            for r in res: self.reply(r)

    def execute(self, direct=False, *args, **kwargs):
        """ dispatch event onto the cmnds object. this method needs both event.nodispatch = False amd event.iscommand = True set. """
        logging.debug("execute %s" % self.cbtype)
        from tl.lib.commands import cmnds
        res = self
        if not self.setupdone: self.setup()
        self.startout()
        self.bind(self.bot, force=True, dolog=True)
        if not self.pipelined and ' ! ' in self.txt: res = self.dopipe(direct, *args, **kwargs)
        else:
            try: res = cmnds.dispatch(self.bot, self, direct=direct, *args, **kwargs)
            except RequireError as ex: logging.error(str(ex))
            except NoSuchCommand as ex: logging.error("we don't have a %s command" % str(ex)) ; self.ready()
            except NoSuchUser as ex: logging.error("we don't have user for %s" % str(ex))
            except Exception as ex: handle_exception()
        return res

    def dopipe(self, direct=False, *args, **kwargs):
        """ split cmnds, create events for them, chain the queues and dispatch.  """
        direct = True
        logging.warn("starting pipeline")
        origout = self.outqueue
        events = []
        self.pipelined = True
        splitted = self.txt.split(" ! ")
        for i in range(len(splitted)):
            t = splitted[i].strip()
            if not t[0] in self.getcc(): t = ";" + t
            e = self.bot.make_event(self.userhost, self.channel, t)
            if self.sock: e.sock = self.sock
            e.outqueue = deque()
            e.busy = deque()
            e.prev = None
            e.pipelined = True
            e.dontbind = False
            if not e.woulddispatch(): raise NoSuchCommand(e.txt)
            events.append(e)
        prev = None
        for i in range(len(events)):
            if i > 0:
                events[i].inqueue = events[i-1].outqueue
                events[i].prev = events[i-1]
        events[-1].pipelined = False
        events[-1].dontclose = False
        for i in range(len(events)):
            if not direct: self.bot.put(events[i])
            else: events[i].execute(direct)
        self.ready()
        return events[-1]

    def prepare(self, bot=None):
        """ prepare the event for dispatch. """
        if bot: self.bot = bot or self.bot
        assert(self.bot)
        self.origin = self.channel
        self.bloh()
        self.makeargs()
        if not self.nolog: logging.debug("%s - prepared event - %s" % (self.auth, self.cbtype))
        return self

    def bind(self, bot=None, user=None, chan=None, force=False, dolog=None):
        """ bind event.bot event.user and event.chan to execute a command on it. """
        dolog = dolog or 'TICK' not in self.cbtype
        if dolog and not force and self.dontbind: logging.debug("dontbind is set on event . .not binding"); return
        if not force and self.bonded: logging.debug("already bonded") ; return
        dolog and logging.debug("starting bind on %s - %s" % (self.userhost, self.txt)) 
        target = self.auth or self.userhost
        bot = bot or self.bot
        if not self.chan:
            if chan: self.chan = chan
            elif self.channel: self.chan = ChannelBase(self.channel, bot.cfg.name)
            elif self.userhost: self.chan = ChannelBase(self.userhost, bot.cfg.name)
            if self.chan: dolog and logging.debug("channel bonded - %s" % self.chan.data.id)
        if not target: self.prepare(bot) ; self.bonded = True ; return
        if not self.user and target and not self.nodispatch:
            if user: u = user
            else: u = bot.users.getuser(target)
            if not u: 
                cfg = getmainconfig()
                if cfg.auto_register and self.iscommand:
                    u = bot.users.addguest(target, self.nick)
                    if u: logging.warn("auto_register applied")
                    else: logging.error("can't add %s to users database" % target)
            if u:
                msg = "!! %s -=- %s -=- %s -=- (%s) !!" % (u.data.name, self.usercmnd or "none", self.cbtype, self.bot.cfg.name)
                dolog and logging.warn(msg)
                self.user = u
                self.uid = get_uid(self.user.data.name)
            if self.user: dolog and logging.debug("user bonded from %s" % whichmodule())
        if not self.user and target: dolog and self.iscommand and logging.warn("no %s user found" % target) ; self.nodispatch = True
        self.prepare(bot)
        if self.bot: self.inchan = self.channel in self.bot.cfg.channels
        self.bonded = True
        return self

    def bloh(self, bot=None, *args, **kwargs):
        """ overload this. """
        self.bot = bot or self.bot
        self.usercmnd = self.iscmnd()
        if self.usercmnd:
            self.execstr = self.usercmnd
            self.usercmnd = self.usercmnd.split()[0]
            self.nodispatch = False
            self.iscommand = True
            
    def reply(self, txt, result=[], event=None, origin="", dot=", ", nr=375, extend=0, showall=False, *args, **kwargs):
        """ reply to this event """
        try: target = self.channel or self.arguments[1]
        except (IndexError, TypeError): target = self.channel or "nochannel"
        if self.silent:
            self.msg = True
            self.bot.say(self.nick, txt, result, self.userhost, extend=extend, event=self, dot=dot, nr=nr, showall=showall, *args, **kwargs)
        elif self.isdcc: self.bot.say(self.sock, txt, result, self.userhost, extend=extend, event=self, dot=dot, nr=nr, showall=showall, *args, **kwargs)
        else: self.bot.say(target, txt, result, self.userhost, extend=extend, event=self, dot=dot, nr=nr, showall=showall, *args, **kwargs)
        return self

    def missing(self, txt):
        """ display missing arguments. """
        if self.alias: l = len(self.alias.split()) - 1
        else: l = 0
        t = ' '.join(txt.split()[l:])
        self.reply("%s %s" % (self.aliased or self.usercmnd, t), event=self) 
        return self

    def done(self, silent=False):
        """ tell the user we are done. """
        if not silent: self.reply('<b>done</b> - %s' % (self.usercmnd or self.alias or self.txt), event=self)
        self.ready()
        return self

    def leave(self):
        """ lower the time to leave. """
        self.ttl -= 1
        if self.ttl <= 0 : self.status = "done"

    def makeoptions(self):
        """ check the given txt for options. """
        try: self.options = makeeventopts(self.txt)
        except: handle_exception() ; return 
        if not self.options: return
        if self.options.channel: self.target = self.options.channel
        logging.info("options - %s" % str(self.options))
        self.txt = ' '.join(self.options.args)
        self.makeargs()

    def makeargs(self):
        """ make arguments and rest attributes from self.txt. """
        if not self.execstr: self.args = [] ; self.rest = ""
        else:
            args = self.execstr.split()
            self.chantag = args[0]
            if len(args) > 1:
                self.args = args[1:]
                self.rest = ' '.join(self.args)
            else: self.args = [] ; self.rest = ""

    def makeresponse(self, txt, result, dot=", ", *args, **kwargs):
        """ create a response from a string and result list. """
        return self.bot.makeresponse(txt, result, dot, *args, **kwargs)

    def less(self, what, nr=365):
        """ split up in parts of <nr> chars overflowing on word boundaries. """
        return self.bot.less(what, nr)

    def isremote(self):
        """ check whether the event is off remote origin. """
        return self.txt.startswith('{"') or self.txt.startswith("{&")

    def iscmnd(self):
        """ check if event is a command. """
        if not self.txt: return ""
        if not self.bot: return ""
        if self.txt[0] in self.getcc(): return self.txt[1:]
        matchnick = str(self.bot.cfg.nick + ":")
        if self.txt.startswith(matchnick): return self.txt[len(matchnick):]
        matchnick = str(self.bot.cfg.nick + ",")
        if self.txt.startswith(matchnick): return self.txt[len(matchnick):]
        if self.iscommand and self.execstr: return self.execstr
        return ""

    hascc = stripcc = iscmnd

    def gotcc(self):
        if not self.txt: return False
        return self.txt[0] in self.getcc()

    def getcc(self):
        if self.chan: cc = self.chan.data.cc
        else: cc = ""
        if not cc:
            cfg = getmainconfig()
            if cfg.globalcc and not cfg.globalcc in cc: cc += cfg.globalcc
        if not cc: cc = "!;"
        if not ";" in cc: cc += ";"
        logging.debug("cc is %s" % cc)
        return cc

    def blocked(self):
        return floodcontrol.checkevent(self)

    def woulddispatch(self):
        cmnds.reloadcheck(self.bot, self)
        return cmnds.woulddispatch(self.bot, self)

    def wouldmatchre(self):
        return cmnds.wouldmatchre(self.bot, self)

    def tojabber(self):
        """ convert the dictionary to xml. """
        res = dict(self)
        if not res:
            raise Exception("%s .. toxml() can't convert empty dict" % self.name)
        elem = self['element']
        main = "<%s" % self['element']
        for attribute in attributes[elem]:
            if attribute in res:
                if res[attribute]: main += " %s='%s'" % (attribute, escape(res[attribute]))
                continue
        main += ">"
        if "xmlns" in res: main += "<x xmlns='%s'/>" % res["xmlns"] ; gotsub = True
        else: gotsub = False
        if 'html' in res:   
            if res['html']: 
                main += '<html xmlns="http://jabber.org/protocol/xhtml-im"><body xmlns="http://www.w3.org/1999/xhtml">%s</body></html>' % res['html']
                gotsub = True
        if 'txt' in res:
            if res['txt']:
                main += "<body>%s</body>" % escape(res['txt'])
                gotsub = True
        for subelement in subelements[elem]:
            if subelement == "body": continue
            if subelement == "thread": continue
            if subelement == "error": continue
            try: data = res[subelement]
            except KeyError: pass
            if data:
                try:
                    main += "<%s>%s</%s>" % (subelement, escape(data), subelement)
                    gotsub = True
                except AttributeError as ex: logging.warn("skipping %s" % subelement)
        if gotsub: main += "</%s>" % elem
        else: main = main[:-1] ; main += " />"   
        return main

    def finish(self):
        if self.handler: self.handler.finish()
