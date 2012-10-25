# plugs/quote.py
#
#

""" quotes plugin """

## tl imports

from tl.lib.persist import Persist
from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.datadir import datadir
from tl.utils.locking import lockdec
from tl.db.direct import Db
from tl.lib.plugins import plugs
from tl.lib.aliases import setalias

## basic imports

import random
import re
import time
import _thread
import os
import logging

## main db

db = None

## plugin initialisation

def init():
    global db
    from tl.db import getmaindb
    db = getmaindb()
    setalias('aq', 'quote-add')
    setalias('wq', 'quote-who')
    setalias('dq', 'quote-del')
    setalias('lq', 'quote-last')
    setalias('2q', 'quote-2')
    setalias('iq', 'quote-id')
    setalias('q', 'quote')
    setalias('sq', 'quote-search')
    setalias('cq', 'quote-count')
    setalias('q-good', 'quote-good')
    setalias('q-bad', 'quote-bad')


## locks

quoteslock = _thread.allocate_lock()
locked = lockdec(quoteslock)

## QuoteItem class

class QuoteItem(object):

    """ object representing a quote """

    def __init__(self, idnr, txt, nick=None, userhost=None, ttime=None):
        self.id = idnr
        self.txt = txt
        self.nick = nick
        self.userhost = userhost
        self.time = ttime

## QuetesDb class

class QuotesDb(object):

    """ quotes db interface """

    def size(self):
        """ return nr of quotes """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        result = db.execute(""" SELECT COUNT(*) FROM quotes """)
        return result[0][0]

    def add(self, nick, userhost, quote):
        """ add a quote """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        result = db.execute(""" INSERT INTO quotes(quote, userhost, createtime, nick) VALUES (%s, %s, %s, %s) """, (quote, userhost, time.time(), nick))
        return result

    def delete(self, quotenr):
        """ delete quote with id == nr """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        result = db.execute(""" DELETE FROM quotes WHERE indx = %s """, (quotenr, ))
        return result

    def random(self):
        """ get random quote """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return
        result = db.execute(""" SELECT indx FROM quotes """)
        indices = []
        if not result: return None
        for i in result: indices.append(i[0])
        if indices: idnr = random.choice(indices) ; return self.idquote(idnr)

    def idquote(self, quotenr):
        """ get quote by id """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return
        if quotenr == 0: return
        result = db.execute(""" SELECT indx, quote FROM quotes WHERE indx = %s """, quotenr)
        if result: return QuoteItem(*result[0])

    def whoquote(self, quotenr):
        """ get who quoted the quote """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return
        result = db.execute(""" SELECT nick, createtime FROM quotes WHERE indx = %s """, (quotenr, ))
        if result: return result[0]

    def last(self, nr=1):
        """ get last quote """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        result = db.execute(""" SELECT indx, quote FROM quotes ORDER BY indx DESC LIMIT %s """, (nr, ))
        res = []
        if result:
            for i in result: res.append(QuoteItem(*i))
        return res

    def search(self, what):
        """ search quotes """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        result = db.execute(""" SELECT indx, quote FROM quotes WHERE quote LIKE %s """, '%%%s%%' % what)
        res = []
        if result:
            for i in result: res.append(QuoteItem(*i))
        return res

    def searchlast(self, what, nr):
        """ search quotes """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        result = db.execute(""" SELECT indx, quote FROM quotes WHERE quote LIKE %s ORDER BY indx DESC LIMIT %s """, ('%%%s%%' % what, nr))
        res = []
        if result:
            for i in result: res.append(QuoteItem(*i))
        return res

## defines

quotes = QuotesDb()

## size function

def size():
    """ return number of quotes """
    return quotes.size()

## quote-add command

def handle_quoteadd(bot, ievent):
    """ quote-add <txt> .. add a quote """
    if not ievent.rest: ievent.missing("<quote>") ; return
    idnr = quotes.add(ievent.nick, ievent.userhost, ievent.rest)
    ievent.reply('quote %s added' % idnr)

cmnds.add('quote-add', handle_quoteadd, ['USER', 'QUOTEADD'], allowqueue=False)
examples.add('quote-add', 'quote-add <txt> .. add quote', 'quote-add mekker')

## quote-who command

def handle_quotewho(bot, ievent):
    """ quote-who <nr> .. show who added a quote """
    try: quotenr = int(ievent.args[0])
    except IndexError: ievent.missing("<nr>") ; return
    except ValueError: ievent.reply("argument must be an integer") ; return
    result = quotes.whoquote(quotenr)
    if not result or not result[0] or not result[1]: ievent.reply('no who quote data available') ; return
    ievent.reply('quote #%s was made by %s on %s' % (quotenr, result[0], result[1]))

cmnds.add('quote-who', handle_quotewho, ['USER', 'WEB', 'ANON', 'ANONQUOTE'])
examples.add('quote-who', 'quote-who <nr> .. show who quote <nr>', 'quote-who 1')

## quote-del command

def handle_quotedel(bot, ievent):
    """ quote-del <nr> .. delete quote by id """
    try: quotenr = int(ievent.args[0])
    except IndexError: ievent.missing('<nr>') ; return
    except ValueError: ievent.reply('argument needs to be an integer') ; return
    if quotes.delete(quotenr): ievent.reply('quote deleted')
    else: ievent.reply("can't delete quote with nr %s" % quotenr)

cmnds.add('quote-del', handle_quotedel, ['QUOTEDEL', 'OPER', 'QUOTE'])
examples.add('quote-del', 'quote-del <nr> .. delete quote', 'quote-del 2')

## quote-last command

def handle_quotelast(bot, ievent):
    """ quote-last .. show last quote """
    search = ""
    try:
        (nr, search) = ievent.args
        nr = int(nr)  
    except ValueError:
        try:
            nr = ievent.args[0]
            nr = int(nr)
        except (IndexError, ValueError):
            nr = 1
            try: search = ievent.args[0]
            except IndexError: search = ""
    if nr < 1 or nr > 4: ievent.reply('nr needs to be between 1 and 4') ; return
    search = re.sub('^d', '', search)
    if search: quotelist = quotes.searchlast(search, nr)
    else: quotelist = quotes.last(nr)
    if quotelist != None:
        for quote in quotelist:
            karma = plugs.get("tl.plugs.db.karma")
            if karma: qkarma = karma.karma.get('quote %s' % quote.id)
            else: qkarma = None
            if qkarma: ievent.reply('#%s (%s) %s' % (quote.id, qkarma, quote.txt))
            else: ievent.reply('#%s %s' % (quote.id, quote.txt))
    else: ievent.reply("can't fetch quote")

cmnds.add('quote-last', handle_quotelast, ['USER', 'WEB', 'ANON', 'ANONQUOTE'])
examples.add('quote-last', 'show last quote', 'quote-last')

## quote-2 command

def handle_quote(bot, ievent):
    """ quote-2 .. show 2 random quotes """
    qkarma = None
    karma = plugs.get("tl.plugs.db.karma")
    quote = quotes.random()
    if quote != None:
        if karma: qkarma = karma.karma.get('quote %s' % quote.id)
        if qkarma: ievent.reply('#%s (%s) %s' % (quote.id, qkarma, quote.txt))
        else: ievent.reply('#%s %s' % (quote.id, quote.txt))
    else: ievent.reply('no quotes yet') ; return
    quote = quotes.random()
    if quote != None:
        if karma: qkarma = karma.karma.get('quote %s' % quote.id)
        if qkarma: ievent.reply('#%s (%s) %s' % (quote.id, qkarma, quote.txt))
        else: ievent.reply('#%s %s' % (quote.id, quote.txt))

cmnds.add('quote-2', handle_quote, ['USER', 'WEB', 'ANON', 'ANONQUOTE'])
examples.add('quote-2', 'quote-2 .. show 2 random quotes', 'quote-2')

## quote-id command

def handle_quoteid(bot, ievent):
    """ quote-id <nr> .. show quote by id """
    try: quotenr = int(ievent.args[0])
    except IndexError: ievent.missing('<nr>') ; return
    except ValueError: ievent.reply('argument must be an integer') ; return
    qkarma = None
    quote = quotes.idquote(quotenr)
    if quote != None:
        karma = plugs.get("tl.plugs.db.karma")
        if karma: qkarma = karma.karma.get('quote %s' % quote.id)
        if qkarma: ievent.reply('#%s (%s) %s' % (quote.id, qkarma, quote.txt))
        else: ievent.reply('#%s %s' % (quote.id, quote.txt))
    else: ievent.reply("can't fetch quote with id %s" % quotenr)

cmnds.add('quote-id', handle_quoteid, ['USER', 'WEB', 'ANON', 'ANONQUOTE'])
examples.add('quote-id', 'quote-id <nr> .. get quote <nr>', 'quote-id 2')

## quote command

def handle_quote(bot, ievent):
    """ quote .. show random quote """
    quote = quotes.random()
    qkarma = None
    if quote != None:
        karma = plugs.get("tl.plugs.db.karma")
        if karma: qkarma = karma.karma.get('quote %s' % quote.id)
        if qkarma: ievent.reply('#%s (%s) %s' % (quote.id, qkarma, quote.txt))
        else: ievent.reply('#%s %s' % (quote.id, quote.txt))
    else: ievent.reply('no quotes yet')

cmnds.add('quote', handle_quote, ['USER', 'WEB', 'ANON', 'ANONQUOTE'])
examples.add('quote', 'show random quote', 'quote')

## quote-search command

def handle_quotesearch(bot, ievent):
    """ quote-search <txt> .. search quotes """
    if not ievent.rest: ievent.missing('<item>') ; return
    else: what = ievent.rest ; nrtimes = 3
    result = quotes.search(what)
    if result:
        if ievent.queues:
            res = []
            for quote in result: res.append('#%s %s' % (quote.id, quote.txt))
            ievent.reply(res)
            return            
        if nrtimes > len(result): nrtimes = len(result)
        randquotes = random.sample(result, nrtimes)
        for quote in randquotes:
            qkarma = None
            karma = plugs.get("tl.plugs.db.karma")
            if karma: qkarma = karma.karma.get('quote %s' % quote.id)
            if qkarma: ievent.reply('#%s (%s) %s' % (quote.id, qkarma, quote.txt))
            else: ievent.reply("#%s %s" % (quote.id, quote.txt))
    else: ievent.reply('no quotes found with %s' % what)

cmnds.add('quote-search', handle_quotesearch, ['USER', 'WEB', 'ANON', 'ANONQUOTE'])
examples.add('quote-search', 'quote-search <txt> .. search quotes for <txt>', 'quote-search bla')

## quote-count command

def handle_quotescount(bot, ievent):
    """ quote-count .. show number of quotes """
    ievent.reply('quotes count is %s' % quotes.size())

cmnds.add('quote-count', handle_quotescount, ['USER', 'WEB', 'ANON', 'ANONQUOTE'])
examples.add('quote-count', 'count nr of quotes', 'quote-count')

## quote-good command

def handle_quotegood(bot, ievent):
    """ show top ten positive karma """
    karma = plugs.get("tl.plugs.db.karma")
    if not karma: ievent.reply("karma plugin is not loaded") ; return
    result = karma.karma.quotegood(limit=10)
    if result:
        resultstr = ""
        for i in result:
            if i[1] > 0: resultstr += "%s: %s " % (i[0], i[1])
        ievent.reply('quote goodness: %s' % resultstr)
    else: ievent.reply('quote karma void')

cmnds.add('quote-good', handle_quotegood, ['USER', 'WEB', 'ANON', 'ANONQUOTE'])
examples.add('quote-good', 'show top 10 quote karma', 'quote-good')

## quote-bad command

def handle_quotebad(bot, ievent):
    """ show top ten negative karma """
    karma = plugs.get("tl.plugs.db.karma")
    if not karma: ievent.reply("karma plugin is not loaded") ; return
    result = karma.karma.quotebad(limit=10)
    if result:
        resultstr = ""
        for i in result:
            if i[1] < 0: resultstr += "%s: %s " % (i[0], i[1])
        ievent.reply('quote badness: %s' % resultstr)
    else: ievent.reply('quote karma void')

cmnds.add('quote-bad', handle_quotebad, ['USER', 'WEB', 'ANON', 'ANONQUOTE'])
examples.add('quote-bad', 'show lowest 10 quote karma', 'quote-bad')
