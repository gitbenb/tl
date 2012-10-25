# tl/plugs/core/tail.py
#
#

""" tail bot results. """

## tl imports

from tl.utils.generic import waitforqueue
from tl.lib.commands import cmnds
from tl.lib.examples import examples

## basic imports

import time

## tail command

def handle_tail(bot, ievent):
    """ no arguments - show last <nr> elements, use this command in a pipeline. """
    try: nr = int(ievent.args[0])
    except (ValueError, IndexError): nr = 3
    if not ievent.inqueue: time.sleep(0.5)
    ievent.reply('results: ', list(ievent.inqueue)[-nr:])
    
cmnds.add('tail', handle_tail, ['OPER', 'USER', 'GUEST'])
examples.add('tail', 'show last <nr> lines of pipeline output', 'list ! tail 5')
