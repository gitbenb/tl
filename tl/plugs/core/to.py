# tl/plugs/core/to.py
#
#

""" send output to another user .. used in a pipeline. """

## tl imports

from tl.lib.commands import cmnds
from tl.utils.generic import getwho, waitforqueue
from tl.lib.examples import examples

## basic imports

import time

## to command

def handle_to(bot, ievent):
    """ arguments: <nick> - direct output to <nick>, use this command in a pipeline. """
    try: nick = ievent.args[0]
    except IndexError: ievent.reply('to <nick>') ; return
    if nick == 'me': nick = ievent.nick
    if not getwho(bot, nick): ievent.reply("don't know %s" % nick) ; return
    if not ievent.inqueue: time.sleep(1)
    if ievent.inqueue:
        bot.say(nick, "%s sends you this:" % ievent.nick)
        bot.say(nick, " ".join(ievent.inqueue))
        if len(ievent.inqueue) == 1: ievent.reply('1 element sent')
        else: ievent.reply('%s elements sent' % len(ievent.inqueue))
    else: ievent.reply('nothing to send')

cmnds.add('to', handle_to, ['OPER', 'USER', 'TO'])
examples.add('to', 'send pipeline output to another user', 'list ! to dunker')
