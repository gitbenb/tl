# tl/channelbase.py
#
#

""" provide a base class for channels. """

## tl imports

from tl.utils.name import stripname
from tl.utils.lazydict import LazyDict
from tl.lib.persist import Persist
from tl.lib.datadir import getdatadir
from tl.utils.trace import whichmodule
from tl.lib.errors import NoChannelProvided, NoChannelSet

## basic imports

import time
import os
import logging

## classes

class ChannelBase(Persist):

    """ Base class for all channel objects. """

    def __init__(self, id, botname=None, type="notset"):
        if not id: raise NoChannelSet()
        if not botname: Persist.__init__(self, getdatadir() + os.sep + 'channels' + os.sep + stripname(id))
        else: Persist.__init__(self, getdatadir() + os.sep + 'fleet' + os.sep + stripname(botname) + os.sep + 'channels' + os.sep + stripname(id))
        self.id = id
        self.type = type
        self.lastmodified = time.time()
        self.data.id = id
        self.data.enable = self.data.enable or False
        self.data.ops = self.data.ops or []
        self.data.silentcommands = self.data.silentcommands or []
        self.data.allowcommands = self.data.allowcommands or []
        self.data.feeds = self.data.feeds or []
        self.data.forwards = self.data.forwards or []
        self.data.allowwatch = self.data.allowwatch or []
        self.data.watched = self.data.watched or []
        self.data.passwords = self.data.passwords or {}
        self.data.cc = self.data.cc or "!"
        self.data.nick = self.data.nick or "tl"
        self.data.key = self.data.key or ""
        self.data.denyplug = self.data.denyplug or []
        self.data.createdfrom = whichmodule()
        self.data.cacheindex = 0
        self.data.tokens = self.data.tokens or []
        self.data.webchannels = self.data.webchannels or []

    def setpass(self, type, key):
        """ set channel password based on type. """
        self.data.passwords[type] = key
        self.save()

    def getpass(self, type='IRC'):
        """ get password based of type. """
        try:
            return self.data.passwords[type]
        except KeyError: return

    def delpass(self, type='IRC'):
        """ delete password. """
        try:
            del self.data.passwords[type]
            self.save()
            return True
        except KeyError: return

