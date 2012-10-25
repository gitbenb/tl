# tl/drivers/sleek/presence.py
#
#

""" SleekXMPP Presence. """

# tl imports

from tl.lib.eventbase import EventBase
from tl.utils.exception import handle_exception
from tl.utils.trace import whichmodule

## basic imports

import time
import logging 

## classes

class Presence(EventBase):

    def __init__(self, nodedict={}):
        EventBase.__init__(self, nodedict)
        self.element = "presence"
        self.jabber = True
        self.cmnd = "PRESENCE"
        self.cbtype = "PRESENCE"
        self.bottype = "xmpp"

    def parse(self, data, bot=None):
        """ set ircevent compatible attributes """
        try:
            self.bot = bot or self.bot
            self.cmnd = 'PRESENCE'
            self.fromm = str(data['from'])        
            try: self.nick = self.fromm.split('/')[1]
            except (AttributeError, IndexError): self.nick = ""
            self.jid = str(self.jid) or self.fromm
            self.ruserhost = self.jid
            self.userhost = self.jid
            self.resource = self.nick
            self.stripped = self.jid.split('/')[0]
            self.auth = self.stripped
            self.channel = self.fromm.split('/')[0]
            self.printto = self.channel
            self.origtxt = self.txt
            self.time = time.time()
            if self.type == 'groupchat': self.groupchat = True
            else: self.groupchat = False
        except Excpetion as ex: handle_exception()
