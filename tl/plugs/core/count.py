# tl/plugs/core/count.py
#
#

""" count number of items in result queue. """

## tl imports

from tl.lib.commands import cmnds
from tl.utils.generic import waitforqueue
from tl.lib.examples import examples

## basic imports

import time

## count command

def handle_count(bot, ievent):
    """ no arguments - show nr of elements in result list .. use this command in a pipeline. """
    #if ievent.prev: ievent.prev.wait()
    a = ievent.inqueue
    size = len(a)
    ievent.reply(str(size))

cmnds.add('count', handle_count, ['OPER', 'USER', 'GUEST'])
examples.add('count', 'count nr of items', 'list ! count')
