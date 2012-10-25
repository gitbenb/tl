# tl/utils/mainloop.py
#
#

""" main loop used in tl binairies. """

## tl imports

from tl.utils.exception import handle_exception
from tl.lib.eventhandler import mainhandler
from tl.lib.exit import globalshutdown
from tl.lib.errors import TLStop

## basic imports

import os
import time

## mainloop function

def mainloop():
    """ function to be used as mainloop. """
    while 1:
        try:
            time.sleep(1)
            mainhandler.handle_one()
        except TLStop: break
        except KeyboardInterrupt: break
        except Exception as ex:
            handle_exception()
            break
    globalshutdown()
