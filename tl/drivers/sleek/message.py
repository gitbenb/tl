# tl/drivers/sleek/message.py
#
#

""" jabber message definition .. types can be normal, chat, groupchat, 
    headline or  error
"""

## tl imports

from tl.utils.exception import handle_exception
from tl.utils.trace import whichmodule
from tl.utils.generic import toenc, fromenc, jabberstrip
from tl.utils.locking import lockdec
from tl.lib.eventbase import EventBase
from tl.lib.errors import BotNotSetInEvent

## basic imports

import types
import time
import _thread
import logging
import re

## locks

replylock = _thread.allocate_lock()
replylocked = lockdec(replylock)

## classes

class Message(EventBase):

    """ jabber message object. """

    def __init__(self, nodedict={}):
        self.element = "message"
        self.jabber = True
        self.cmnd = "MESSAGE"
        self.cbtype = "MESSAGE"
        self.bottype = "xmpp"
        self.type = "normal"
        self.speed = 8
        EventBase.__init__(self, nodedict)
  
    def __copy__(self):
        return Message(self)

    def __deepcopy__(self, bla):
        m = Message()
        m.copyin(self)
        return m

    def parse(self, data, bot):
        """ set ircevent compat attributes. """
        logging.info("starting parse on %s" % str(data))
        self.bot = bot
        self.createdfrom = bot.cfg.name
        self.jidchange = False
        self.jid = str(data['from'])
        self.type = data['type']
        try: self.error = data['error']
        except KeyError: pass
        if not self.jid: logging.error("can't detect origin - %s" % data) ; return
        try: self.resource = self.jid.split('/')[1]
        except IndexError: pass
        self.channel = self.jid.split('/')[0]
        self.origchannel = self.channel
        self.nick = self.resource
        self.ruserhost = self.jid
        self.userhost = self.jid
        self.stripped = self.jid.split('/')[0]
        self.printto = self.channel
        try: self.txt = str(data['body']) ; self.nodispatch = False
        except AttributeError: self.txt = "" ; self.nodispatch = True
        self.time = time.time()
        logging.warn("message type is %s" % self.type)
        if self.type == "error": logging.error("%s (%s)" % (self.error, self.bot.cfg.name))
        if self.type == 'groupchat':
            self.groupchat = True
            self.auth = self.userhost
        else:
            self.showall = True
            self.groupchat = False
            self.auth = self.stripped
            self.nick = self.jid.split("@")[0]
        self.msg = not self.groupchat
        self.fromm = self.jid
        self.makeargs()
        self.bind(self.bot)
        return self

    def errorHandler(self):
        """ dispatch errors to their handlers. """
        try:
            code = self.get('error').code
        except Exception as ex:
            handle_exception()
        try:
            method = getattr(self, "handle_%s" % code)
            if method:
                logging.error('dispatching error to handler %s' % str(method))
                method(self)
        except AttributeError as ex: logging.error('unhandled error %s' % code)
        except: handle_exception()

    def normalize(self, what):
        return self.bot.normalize(what)
