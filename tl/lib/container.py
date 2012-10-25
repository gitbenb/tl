# tl/container.py
#
#

""" container for bot to bot communication. """

__version__ = "1"

## tl imports

from tl.lib.persist import Persist
from tl.utils.name import stripname
from tl.lib.eventbase import EventBase
from tl.imports import getjson

## basic imports

import hmac
import uuid
import time
import hashlib

## defines

idattributes = ['createtime', 'origin', 'type', 'idtime', 'payload']

## functions

def getid(container):
    name = ""
    for attr in idattributes:
        try: name += str(container[attr])
        except KeyError: pass
    return uuid.uuid3(uuid.NAMESPACE_URL, name).hex

## classes

class Container(EventBase):

    """ Container for bot to bot communication. Provides a hmac id that can be checked. """

    def __init__(self, origin=None, payload=None, type="event", key=None, how="direct"):
        EventBase.__init__(self)
        self.createtime = time.time()
        self.origin = origin
        self.type = type
        self.hashkey = key
        if payload:
            self.payload = payload
            self.makeid()
            if key: self.makehmac(key)
            else:
                self.hashkey = self.id
                self.makehmac(self.id)

    def makeid(self):
        self.idtime = time.time()
        self.id = getid(self)

    def makehmac(self, key):
        self.hash = "sha512"
        self.hashkey = key
        self.digest = hmac.new(bytes(self.hashkey, "utf-8"), bytes(self.payload, "utf-8"), hashlib.sha512).hexdigest()

    def save(self, attributes=[]):
        target = {}
        if attributes:
            for key in attributes: target[key] = self[key]
        else: target = cpy(self)
        targetfile = getdatadir() + os.sep + "containers" + os.sep + str(self.createtime) + "_" + stripname(self.origin)
        p = Persist(targetfile)
        p.data = getjson().dumps(target)
        p.save()
