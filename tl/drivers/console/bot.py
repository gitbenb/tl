# tl/console/bot.py
#
#

""" console bot. """

## tl imports

from tl.version import getversion
from tl.lib.datadir import getdatadir
from tl.utils.generic import waitforqueue
from tl.lib.errors import NoSuchCommand, NoInput, TLStop
from tl.lib.botbase import BotBase
from tl.lib.exit import globalshutdown
from tl.utils.generic import strippedtxt, waitevents
from tl.utils.exception import handle_exception
from tl.lib.eventhandler import mainhandler
from .event import ConsoleEvent

## basic imports

import time
import queue
import logging
import sys
import code
import os
import readline
import atexit
import getpass
import re
import copy

## defines

cpy = copy.deepcopy
histfilepath = os.path.expanduser(getdatadir() + os.sep + "run" + os.sep + "console-history")

## HistoryConsole class

class HistoryConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>", histfile=histfilepath):
        self.fname = histfile
        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try: readline.read_history_file(histfile)
            except IOError: pass

    def save_history(self, histfile=None):
        readline.write_history_file(histfile or self.fname)

## the console

console = HistoryConsole()

## ConsoleBot

class ConsoleBot(BotBase):

    ERASE_LINE = '\033[2K'
    BOLD='\033[1m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ENDC = '\033[0m'
    COMMON = '\003[9'

    def __init__(self, cfg=None, users=None, plugs=None, botname=None, *args, **kwargs):
        BotBase.__init__(self, cfg, users, plugs, botname, *args, **kwargs)
        self.type = "console"

    def startshell(self, connect=True):
        """ start the console bot. """
        self.start(False)
        print(getversion("CONSOLE"))
        while not self.stopped: 
            try: 
                mainhandler.handle_one()
                input = console.raw_input("\n> ")
                if self.stopped: return
                event = ConsoleEvent()
                event.parse(self, input, console)
                event.nooutput = True
                event.nodispatch = False
                e = self.put(event)
                res = e.wait()
                if res:
                    sys.stdout.write("\n")
                    txt = self.makeresponse(res, dot="<br>")
                    self.out(e.userhost, txt)
                sys.stdout.flush()
            except TLStop: break
            except IOError: break
            except NoInput: continue
            except (KeyboardInterrupt, EOFError): break
            except Exception as ex: handle_exception() ; break
        console.save_history()
        
    def outnocb(self, printto, txt, *args, **kwargs):
        assert txt
        if not self.cfg.userid in printto: logging.error("%s is not the owner of this shell . not printing." % printto) ; return
        txt = self.normalize(txt)
        self._raw(txt)

    def _raw(self, txt):
        """ do raw output to the console. """
        logging.info("%s - out - %s" % (self.cfg.name, txt))             
        sys.stdout.write(txt)
        sys.stdout.write('\n')

    def action(self, channel, txt, event=None):
        txt = self.normalize(txt)
        self._raw(txt)

    def notice(self, channel, txt):
        txt = self.normalize(txt)
        self._raw(txt)

    def exit(self, *args, **kwargs):
        """ called on exit. """
        console.save_history()
        self.stopped = True
        
    def normalize(self, what):
        what = strippedtxt(what)
        what = what.replace("<b>", self.BLUE)
        what = what.replace("</b>", self.ENDC)
        what = what.replace("<i>", self.YELLOW)
        what = what.replace("</i>", self.ENDC)
        what = what.replace("<h2>", self.GREEN)
        what = what.replace("</h2>", self.ENDC)
        what = what.replace("<h3>", self.GREEN)
        what = what.replace("</h3>", self.ENDC)
        what = what.replace("&lt;b&gt;", self.BOLD)
        what = what.replace("&lt;/b&gt;", self.ENDC)
        what = what.replace("<br>", "\n")
        what = what.replace("<li>", "* ")
        what = what.replace("</li>", "\n")
        if what.count(self.ENDC) % 2: what = "%s%s" %  (self.ENDC, what)
        return what
