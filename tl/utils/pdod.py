# tl/utils/pdod.py
#
#

""" pickled dicts of dicts """

## tl imports

from tl.utils.lazydict import LazyDict
from tl.lib.persist import Persist

## Pdod class

class Pdod(Persist):

    """ pickled dicts of dicts """

    def __getitem__(self, name):
        """ return item with name """
        if name in self.data: return self.data[name]

    def __delitem__(self, name):
        """ delete name item """
        if name in self.data: return self.data.__delitem__(name)

    def __setitem__(self, name, item):
        """ set name item """
        self.data[name] = item

    def __contains__(self, name):
        return self.data.__contains__(name)

    def setdefault(self, name, default):
        """ set default of name """
        return self.data.setdefault(name, default)

    def has_key(self, name):
        """ has name key """
        return name in self.data

    def has_key2(self, name1, natl):
        """ has [name1][natl] key """
        if name1 in self.data: return natl in self.data[name1]

    def get(self, name1, natl):
        """ get data[name1][natl] """
        try:
            result = self.data[name1][natl]
            return result
        except KeyError: pass

    def set(self, name1, natl, item):
        """ set name, natl item """
        if name1 not in self.data: self.data[name1] = {}
        self.data[name1][natl] = item
