# tl/lib/errors.py
#
#

""" tl exceptions. """

## tl imports

from tl.utils.trace import calledfrom

## basic imports

import sys

## exceptions


class TLBotError(Exception):
    pass

class CannotBindBot(TLBotError): pass

class NoUsers(TLBotError): pass

class TLStop(TLBotError): pass

class NoOptsSet(TLBotError): pass

class NoDbConnection(TLBotError): pass

class NoDbResult(TLBotError): pass

class CantLogon(TLBotError): pass

class URLNotEnabled(TLBotError): pass

class JSONParseError(TLBotError): pass

class StreamError(TLBotError): pass

class RequireError(TLBotError): pass

class CannotAuth(TLBotError): pass

class NotConnected(TLBotError): pass

class FeedAlreadyExists(TLBotError): pass

class MemcachedCounterError(TLBotError): pass

class NoSuchFile(TLBotError): pass

class BotNotEnabled(TLBotError): pass

class NoProperDigest(TLBotError): pass

class NoChannelProvided(TLBotError): pass

class NoInput(TLBotError): pass

class PropertyIgnored(TLBotError): pass

class BotNotSetInEvent(TLBotError): pass

class FeedProviderError(TLBotError): pass

class CantSaveConfig(TLBotError): pass

class NoOwnerSet(TLBotError): pass

class NameNotSet(TLBotError): pass

class NoSuchUser(TLBotError): pass

class NoUserProvided(TLBotError): pass

class NoSuchBotType(TLBotError): pass

class NoChannelSet(TLBotError): pass

class NoSuchWave(TLBotError): pass

class NoSuchCommand(TLBotError): pass

class NoSuchPlugin(TLBotError): pass

class NoOwnerSet(TLBotError): pass

class PlugsNotConnected(TLBotError): pass

class NoEventProvided(TLBotError): pass

class WrongType(TLBotError): pass

