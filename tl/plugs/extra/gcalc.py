# tl/plugs/common/gcalc.py
# encoding: utf-8
#
#

""" use google to calculate e.g. !gcalc 1 + 1 """

## tl imports

from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.utils.url import useragent, geturl2

## basic imports

import urllib.request, urllib.error, urllib.parse

## defines

url = "http://www.google.com/ig/calculator?hl=en&q=%s"

## gcalc command

def handle_gcalc(bot, ievent):
    """ arguments: <expression> - use google calc. """
    if len(ievent.args) > 0: expr = " ".join(ievent.args).replace("+", "%2B").replace(" ", "+")
    else: ievent.missing('Missing an expression') ; return
    #req = urllib.request.Request(url % expr, None,  {'User-agent': useragent()})
    data = geturl2(url % expr)
    try:
        rhs = data.split("rhs")[1].split("\"")[1]
        lhs = data.split("lhs")[1].split("\"")[1]
        if rhs and lhs:
            ievent.reply("%s = %s" % (lhs,rhs.replace('\\x26#215;', '*').replace('\\x3csup\\x3e', '**').replace('\\x3c/sup\\x3e', '')))
        else: ievent.reply("hmmm can't get a result ..")
    except Exception as ex:
        ievent.reply(str(ex))    

cmnds.add('gcalc', handle_gcalc, ['OPER', 'USER', 'GUEST'])
examples.add('gcalc', 'calculate an expression using the google calculator', 'gcalc 1 + 1')
