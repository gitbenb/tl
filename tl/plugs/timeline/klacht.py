# tl/plugs/timeline/klacht.py
#
#

""" het timeline klachten command. """

## tl imports

from tl.utils.name import stripname
from tl.lib.datadir import getdatadir
from tl.lib.persist import TimedPersist, PersistCollection
from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.id import get_uid, get_bid

## basic imports

import logging
import time
import os

## getklachtdir function

def getklachtdir(username):
    return os.path.join(getdatadir(), "timeline", stripname(username), "klacht")

## Klacht class

class Klacht(TimedPersist):

   def __init__(self, username, klacht, default={}, ddir=None, origin=None, *args, **kwargs):
       TimedPersist.__init__(self, username, default=default, ddir=getklachtdir(username), *args, **kwargs)
       self.data.klacht = self.data.klacht or klacht or "geen text gegeven"
       self.data.username = self.data.username or username or "anon"
       self.data.uid = self.data.uid or get_uid(username)
       self.data.origin = self.data.origin or origin or get_bid()

class Klachten(PersistCollection): pass

## complaint command

def handle_klacht(bot, event):
    if not event.rest: event.reply("waar wil je over klagen?") ; return
    k = Klacht(event.user.data.name, event.rest)
    k.save()
    event.reply("klacht is genoteerd op %s" % time.ctime(k.data.created))

cmnds.add("klacht", handle_klacht, ["OPER", "USER", "GUEST"])
examples.add(
             "klacht",
             "met het klacht commando kan je laten registeren wat je intiept, een overzicht kan je krijgen door het klachten commando te geven",
             "klacht die GGZ NHN is maar een rukkerig zooitje proviteurs die betaalt krijgen om nee te zeggen"
            )

def handle_klachten(bot, event):
    klachten = Klachten(getklachtdir(event.user.data.name))
    result = []
    for k in klachten.dosort(): result.append("%s - %s" % (k.data.klacht, time.ctime(k.data.created)))
    if result: event.reply("klachten van %s: " % event.user.data.name, result, dot="indent", nosort=True)
    else: event.reply("ik kan nog geen klachten vinden voor %s" % event.uid)

cmnds.add("klachten", handle_klachten, ["OPER", "USER", "GUEST"])
examples.add("klachten", "laat alle klachten zien", "klachten")
