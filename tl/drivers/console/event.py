# tl/console/event.py
#
#

""" a console event. """

## tl imports

from tl.lib.eventbase import EventBase
from tl.lib.channelbase import ChannelBase
from tl.lib.errors import NoInput
from tl.id import get_uid, get_id

## basic imports

import getpass
import logging
import re

## ConsoleEvent class

class ConsoleEvent(EventBase):

    def parse(self, bot, input, console, *args, **kwargs):
        """ overload this. """
        if not input: raise NoInput()
        self.bot = bot
        self.console = console
        self.userhost = get_id()
        self.origin = self.userhost
        self.txt = input
        self.channel = self.userhost
        self.cbtype = self.cmnd = "CONSOLE"
        self.showall = True
        self.prepare()
        return self

        