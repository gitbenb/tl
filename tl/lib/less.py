# tl/less.py
#
#

""" maintain bot output cache. """

# tl imports

from tl.utils.exception import handle_exception
from tl.utils.limlist import Limlist
from tl.lib.cache import get, set, delete

## basic imports

import logging


## Less class

class Less(object):

    """ output cache .. caches upto <nr> item of txt lines per channel. """

    def clear(self, channel):
        """ clear outcache of channel. """
        channel = str(channel).lower()
        try: delete("outcache-" + channel) 
        except KeyError: pass

    def add(self, channel, listoftxt):
        """ add listoftxt to channel's output. """
        channel = str(channel).lower()
        data = get("outcache-" + channel)
        if not data: data = []
        data.extend(listoftxt)
        set("outcache-" + channel, data, 3600)

    def set(self, channel, listoftxt):
        """ set listoftxt to channel's output. """
        channel = str(channel).lower()
        set("outcache-" + channel, listoftxt, 3600)

    def get(self, channel):
        """ return 1 item popped from outcache. """
        channel = str(channel).lower()
        global get
        data = get("outcache-" + channel)
        if not data: txt = None
        else: 
            try: txt = data.pop(0) ; set("outcache-" + channel, data, 3600)
            except (KeyError, IndexError): txt = None
        if data: size = len(data)
        else: size = 0
        return (txt, size)

    def copy(self, channel):
        """ return 1 item popped from outcache. """
        channel = str(channel).lower()
        global get
        return get("outcache-" + channel)

    def more(self, channel):
        """ return more entry and remaining size. """
        return self.get(channel)

outcache = Less()