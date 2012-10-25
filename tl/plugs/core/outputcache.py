# tl/plugs/core/outputcache.py
#
#

""" outputcache used when reply cannot directly be delivered. """

## tl imports

from tl.lib.commands import cmnds
from tl.lib.outputcache import get, set, clear
from tl.lib.callbacks import callbacks
from tl.lib.examples import examples

## basic imports

import logging

## outputcache command

def handle_outputcache(bot, event):
    """ no arguments - forward the output cache to the user. """
    res = get(event.channel)
    logging.debug("outputcache - %s - %s" % (bot.type, len(res)))
    if res:
        for result in res[::-1]:
            if result:
                try: bot.saynocb(event.channel, result, event=event)
                except Exception as ex: logging.error("outputcache - %s - %s" % (str(ex), result))
    event.done()

cmnds.add('outputcache', handle_outputcache, ['OPER', 'USER', 'GUEST'])
examples.add('outputcache', 'forward the outputcache to the user.', 'outputcache')

## outputcache-clear command

def handle_outputcacheclear(bot, event):
    """ no arguments - flush outputcache of a channel. """
    clear(event.channel)
    event.done()

cmnds.add('outputcache-clear', handle_outputcacheclear, ['OPER', 'USER', 'GUEST'])
examples.add('outputcache-clear', 'flush output cache of a channel', 'outputcache-clear')
