# tl/utils/name.py
#
#

"""
name related helper functions.

google requirements on file names:
  - It must contain only letters, numbers, _, +, /, $, ., and -.
  - It must be less than 256 chars.
  - It must not contain "/./", "/../", or "//".
  - It must not end in "/".
  - All spaces must be in the middle of a directory or file name.


"""

## tl imports

from tl.lib.datadir import getdatadir
from tl.utils.generic import toenc, fromenc
from tl.lib.errors import NameNotSet

## basic imports

import string
import os
import re
import logging

## defines

allowednamechars = string.ascii_letters + string.digits + "-."

## slugify function taken from django (not used now)

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value)
    value = str(re.sub('[^\w\s-]', '', value).strip())
    return re.sub('[-\s]+', '-', value)

## stripname function

def stripname(namein, allowed=""):
    """ strip all not allowed chars from name. """
    if not namein: raise NameNotSet(namein)
    n = namein
    res = []
    allow = allowednamechars + allowed
    for c in n:
        if ord(c) < 31: continue
        elif c in allow: res.append(c)
        else: res.append("_" + str(ord(c)))
    return ''.join(res)

## reversename function

reversere = re.compile("_(\d\d)")

def reversename(namein, allowed=""):
    """ strip all not allowed chars from name. """
    if not namein: raise NameNotSet(namein)
    n = namein
    for t in re.findall(reversere, namein):
       n = n.replace("_"+t, chr(int(t)))
    return n


def stripdatadir(fname):
    res = []
    ddir = getdatadir()
    for i in fname.split(os.sep):
         if i in ddir: continue
         res.append(i)
    return os.sep.join(res)

## testname function

def testname(name):
    """ test if name is correct. """
    for c in name:
        if c not in allowednamechars or ord(c) < 31: return False
    return True

def oldname(name):
    from tl.lib.datadir import getdatadir
    if name.startswith("-"): name[0] = "+"
    name = name.replace("@", "+")
    if os.path.exists(getdatadir() + os.sep + name): return name
    name = name.replace("-", "#")
    name  = prevchan.replace("+", "@")
    if os.path.exists(getdatadir() + os.sep + name): return name
    return ""

## old tl functions

oldallowednamechars = string.ascii_letters + string.digits + '_+/$.-'

## oldstripname function

def oldstripname(namein, allowed=""):
    """ strip all not allowed chars from name. """
    if not namein: raise NameNotSet(namein)
    n = namein.replace(os.sep, '+')
    n = n.replace("/", '+')
    n = n.replace("@", '+')
    n = n.replace("#", '-')
    n = n.replace("!", '.')
    res = []
    allow = oldallowednamechars + allowed
    for c in n:
        if ord(c) < 31: continue
        elif c in allow: res.append(c)
        else: res.append("-" + str(ord(c)))
    return ''.join(res)

