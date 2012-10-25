# tl/plugs/core/data.py
#
#

""" data dumper commands. """

## tl imports

from tl.lib.aliases import setalias
from tl.lib.config import getmainconfig
from tl.lib.commands import cmnds
from tl.lib.examples import examples

## data-event command

def handle_dataevent(bot, event):
    """ no arguments - dump event to json. """
    event.reply(event.fordisplay())

cmnds.add("data-event", handle_dataevent, "OPER")
examples.add('data-event', 'dump event data', 'data-event')

## data-chan command

def handle_datachan(bot, event):
    """ no arguments - dump channel data to json. """
    event.reply(event.chan.data.fordisplay())

cmnds.add("data-chan", handle_datachan, "OPER")
examples.add('data-chan', 'dump channel data', 'data-chan')

## data-bot command

def handle_databot(bot, event):
    """ no arguments - dump bot as json dict. """
    event.reply(bot.fordisplay())

cmnds.add("data-bot", handle_databot, "OPER")
examples.add('data-bot', 'dump bot data', 'data-bot')

## data-cfg command

def handle_datacfg(bot, event):
    """ no arguments - dump bot as json dict. """
    event.reply(bot.cfg.fordisplay())

cmnds.add("data-cfg", handle_datacfg, "OPER")
examples.add('data-cfg', 'dump bot config data', 'data-cfg')

## data-main command

def handle_datamain(bot, event):
    """ no arguments - dump bot as json dict. """
    event.reply(getmainconfig().fordisplay())

cmnds.add("data-main", handle_datamain, "OPER")
examples.add('data-main', 'dump mainconfig data', 'data-main')

