# tl/common/urban.py
#
#

""" query urbandictionary """

__copyright__ = 'this file is in the public domain'
__author__ = "Bas van Oostveen"
__status__ = "seen"

## tl imports

from tl.utils.exception import handle_exception
from tl.utils.url import geturl2
from tl.lib.commands import cmnds
from tl.lib.aliases import aliases
from tl.lib.examples import examples
from tl.lib.persistconfig import PersistConfig

## basic imports

import urllib.request, urllib.parse, urllib.error
import json

## defines

url = "http://www.urbandictionary.com/iphone/search/define?term="

## urban command

def handle_urban(bot, ievent):
    """ urban <what> .. search urban for <what> """
    if len(ievent.args) > 0: what = " ".join(ievent.args)
    else: ievent.missing('<search query>') ; return
    try:
        data = geturl2(url + urllib.parse.quote_plus(what))
        if not data: ievent.reply("word not found: %s" % what) ; return
        data = json.loads(data)
        if data['result_type'] == 'no_result': ievent.reply("word not found: %s" % what) ; return
        res = []
        for r in data['list']: res.append(r['definition'])
        ievent.reply("result: ", res)
    except Exception as ex: ievent.reply(str(ex))

cmnds.add('urban', handle_urban, ['OPER', 'USER', 'GUEST'])
examples.add('urban', 'urban <what> .. search urbandictionary for <what>','1) urban bot 2) urban shizzle')

#### BHJTW 23-01-2012
#### BHJTW 10-03-2012
