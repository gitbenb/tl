# tl/lib/examples.py
#
#

""" examples is a dict of example objects. """

## tl imports

from tl.utils.trace import whichplugin

## basic imports

import re

## Example class

class Example(object):

    """ an example. """

    def __init__(self, descr, ex, url=False, modname=None):
        self.descr = descr
        self.example = ex
        self.url = url
        self.modname = modname or whichplugin(2)

## Collection of exanples

class Examples(dict):

    """ examples holds all the examples. """

    def add(self, name, descr, ex, url=False):
        """ add description and example. """
        self[name.lower()] = Example(descr, ex, url)

    def size(self):
        """ return size of examples dict. """
        return len(list(self.keys()))

    def getexamples(self, disabled=None):
        """ get all examples in list. """
        result = []
        for i in list(self.values()):
            if disabled:
                for d in disabled:
                    if d in i.modname: continue
            ex = i.example.lower()
            exampleslist = re.split('\d\)', ex)
            for example in exampleslist:
                if example: result.append(example.strip())
        return result

## global examples object

examples = Examples()

def size():
    return examples.size()
