# tl/lib/factory.py
#
#

""" Factory to produce instances of classes. """

## tl imports

from tl.utils.exception import handle_exception
from tl.lib.errors import NoSuchBotType, NoUserProvided

## basic imports

import logging

## Factory base class

class Factory(object):
     pass

## BotFactory class

class BotFactory(Factory):

    def create(self, type=None, cfg={}):
        try: type = cfg['type'] or type or None
        except KeyError: pass
        try:
            if type == 'irc':
                from tl.drivers.irc.bot import IRCBot
                bot = IRCBot(cfg)
            elif type == 'console':
                from tl.drivers.console.bot import ConsoleBot
                bot = ConsoleBot(cfg)
            elif type == 'base':
                from tl.lib.botbase import BotBase
                bot = BotBase(cfg)
            elif type == 'tornado':
                from tl.drivers.tornado.bot import TornadoBot
                bot = TornadoBot(cfg)
            elif type == 'sleek' or "xmpp" in type:
                from tl.drivers.sleek.bot import SleekBot
                bot = SleekBot(cfg)
            else: raise NoSuchBotType('%s bot .. unproper type %s' % (type, cfg.dump()))
            return bot
        except NoUserProvided as ex: logging.info("%s - %s" % (cfg.name, str(ex)))
        except AssertionError as ex: logging.warn("%s - assertion error: %s" % (cfg.name, str(ex)))
        except Exception as ex: handle_exception()

bot_factory = BotFactory()
