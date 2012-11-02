# tl/lib/errors.py
#
#

""" tl exceptions. """

## tl imports

from tl.utils.trace import calledfrom

## basic imports

import sys

## exceptions


class TLError(Exception):
    pass

class LazyDictNeeded(TLError): pass

class DictNeeded(TLError): pass

class DatadirNotSet(TLError): pass

class CannotBindBot(TLError): pass

class NoUsers(TLError): pass

class TLStop(TLError): pass

class NoOptsSet(TLError): pass

class NoDbConnection(TLError): pass

class NoDbResult(TLError): pass

class CantLogon(TLError): pass

class URLNotEnabled(TLError): pass

class JSONParseError(TLError): pass

class StreamError(TLError): pass

class RequireError(TLError): pass

class CannotAuth(TLError): pass

class NotConnected(TLError): pass

class FeedAlreadyExists(TLError): pass

class MemcachedCounterError(TLError): pass

class NoSuchFile(TLError): pass

class BotNotEnabled(TLError): pass

class NoProperDigest(TLError): pass

class NoChannelProvided(TLError): pass

class NoInput(TLError): pass

class PropertyIgnored(TLError): pass

class BotNotSetInEvent(TLError): pass

class FeedProviderError(TLError): pass

class CantSaveConfig(TLError): pass

class NoOwnerSet(TLError): pass

class NameNotSet(TLError): pass

class NoSuchUser(TLError): pass

class NoUserProvided(TLError): pass

class NoSuchBotType(TLError): pass

class NoChannelSet(TLError): pass

class NoSuchWave(TLError): pass

class NoSuchCommand(TLError): pass

class NoSuchPlugin(TLError): pass

class NoOwnerSet(TLError): pass

class PlugsNotConnected(TLError): pass

class NoEventProvided(TLError): pass

class WrongType(TLError): pass

