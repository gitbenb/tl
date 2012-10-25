# plugs/karma.py
#
#

""" karma plugin """

## tl imports

from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.datadir import getdatadir
from tl.utils.exception import handle_exception
from tl.utils.locking import lockdec
from tl.utils.statdict import StatDict
from tl.lib.aliases import setalias

## basic imports

import _thread
import pickle
import time
import os
import logging

## defines

ratelimited = []
limiterlock = _thread.allocate_lock()
limlock = lockdec(limiterlock)

db = None

## KarmaDb class

class KarmaDb(object):

    """ karma object """

    def save(self):
        pass

    def size(self):
        """ return number of karma items """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        nritems = db.execute(""" SELECT COUNT(*) FROM karma """)
        return nritems[0][0]

    def get(self, item):
        """ get karma of item """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        item = item.lower()
        value = db.execute(""" SELECT value FROM karma WHERE item = %s """, item)
        if value: return value[0][0]
        else: return 0

    def delete(self, item):
        """ delete karma item """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        item = item.lower()
        value = db.execute(""" DELETE FROM karma WHERE item = %s """, item)
        return value

    def addwhy(self, item, updown, reason):
        """ add why of karma up/down """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        item = item.lower()
        result = db.execute(""" INSERT INTO whykarma(item, updown, why) VALUES (%s, %s, %s) """, (item, updown, reason))
        return result
            
    def upitem(self, item, reason=None):
        """ up a karma item with/without reason """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        item = item.lower()
        value = db.execute(""" SELECT value FROM karma WHERE item = %s """, item)
        try: val = value[0][0]
        except (TypeError, IndexError):
            result = db.execute(""" INSERT INTO karma(item, value) VALUES (%s, 1) """, item)
            if reason: self.addwhy(item, 'up', reason.strip())
            return result
        val += 1
        result = db.execute(""" UPDATE karma SET value = %s WHERE item = %s """, (val, item))
        if reason: self.addwhy(item, 'up', reason.strip())
        return result

    def down(self, item, reason=None):
        """ lower a karma item with/without reason """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        item = item.lower()
        value = db.execute(""" SELECT value FROM karma WHERE item = %s """, item)
        try: val = value[0][0]
        except (TypeError, IndexError):
            result = db.execute(""" INSERT INTO karma(item, value) VALUES (%s, -1) """, item)
            if reason: self.addwhy(item, 'down', reason.strip())
            return result
        val -= 1
        result = db.execute(""" UPDATE karma SET value = %s WHERE item = %s """, (val, item))
        if reason: self.addwhy(item, 'down', reason.strip())
        return result

    def whykarmaup(self, item):
        """ get why of karma ups """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        item = item.lower()
        result = db.execute(""" SELECT why FROM whykarma WHERE item = %s AND updown = 'up' """, item)
        res = []
        if result:
             for i in result: res.append(i[0])
        return res

    def whykarmadown(self, item):
        """ get why of karma downs """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        item = item.lower()
        result = db.execute(""" SELECT why FROM whykarma WHERE item = %s AND updown = 'down' """, item)
        res = []
        if result:
             for i in result: res.append(i[0])
        return res

    def setwhoup(self, item, nick):
        """ set who upped a karma item """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        item = item.lower()
        nick = nick.lower()
        result = db.execute(""" INSERT INTO whokarma(item, nick, updown) VALUES(%s, %s, %s) """, (item, nick, 'up'))
        return result
 
    def setwhodown(self, item, nick):
        """ set who lowered a karma item """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return 0
        item = item.lower()
        nick = nick.lower()
        result = db.execute(""" INSERT INTO whokarma(item, nick, updown) VALUES(%s, %s, %s) """, (item, nick, 'down'))
        return result

    def getwhoup(self, item):
        """ get list of who upped a karma item """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        item = item.lower()
        result = db.execute(""" SELECT nick FROM whokarma WHERE item = %s AND updown = 'up' """, item)
        res = []
        if result:
             for i in result: res.append(i[0])
        return res

    def getwhodown(self, item):
        """ get list of who downed a karma item """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        item = item.lower()
        result = db.execute(""" SELECT nick FROM whokarma WHERE item = %s AND updown = 'down' """, item)
        res = []
        if result:
             for i in result: res.append(i[0])
        return res

    def search(self, item):
        """ search for matching karma item """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        item = item.lower()
        result = db.execute(""" SELECT item,value FROM karma WHERE item LIKE %s """, '%%%s%%' % item)
        res = []
        if result:
             for i in result: res.append(i)
        return res

    def good(self, limit=10):
        """ show top 10 of karma items """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        statdict = StatDict()
        result = db.execute(""" SELECT item, value FROM karma """)
        if not result: return []
        for i in result:
            if i[0].startswith('quote '): continue
            statdict.upitem(i[0], value=i[1])
        return statdict.top(limit=limit)

    def bad(self, limit=10):
        """ show lowest 10 of negative karma items """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        statdict = StatDict()
        result = db.execute(""" SELECT item, value FROM karma """)
        if not result: return []
        for i in result:
            if i[0].startswith('quote '): continue
            statdict.upitem(i[0], value=i[1])
        return statdict.down(limit=limit)

    def quotegood(self, limit=10):
        """ show top 10 of karma items """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        statdict = StatDict()
        result = db.execute(""" SELECT item, value FROM karma """)
        if not result: return []
        for i in result:
            if not i[0].startswith('quote '): continue
            statdict.upitem(i[0], value=i[1])
        return statdict.top(limit=limit)

    def quotebad(self, limit=10):
        """ show lowest 10 of negative karma items """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        statdict = StatDict()
        result = db.execute(""" SELECT item, value FROM karma """)
        if not result: return []
        for i in result:
            if not i[0].startswith('quote '): continue
            statdict.upitem(i[0], value=i[1])
        return statdict.down(limit=limit)

    def whatup(self, nick):
        """ show what items are upped by nick """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        nick = nick.lower()
        statdict = StatDict()
        result = db.execute(""" SELECT item FROM whokarma WHERE nick = %s AND updown = 'up' """, nick)
        if not result: return []
        for i in result: statdict.upitem(i[0])
        return statdict.top()

    def whatdown(self, nick):
        """ show what items are lowered by nick """
        global db
        if not db: logging.error("plugin isnt initialised yet") ; return []
        nick = nick.lower()
        statdict = StatDict()
        result = db.execute(""" SELECT item FROM whokarma WHERE nick = %s AND updown = 'down' """, nick)
        if not result:
            return []
        for i in result:
            statdict.upitem(i[0])
        return statdict.top()

## karma object

karma = KarmaDb()

## size function

def size():
    """ return number of kamra items """
    return karma.size()

## karma ratelimiter

@limlock
def ratelimit(bot, ievent):
    """ karma rate limiter """
    waittime = 30
    limit = 2
    try:
        name = ievent.userhost
        if name not in bot.state: bot.state[name] = {}
        if 'karma' not in bot.state[name]:
            bot.state[name]['karma'] = {'count': 0, 'time': time.time() } 
        if time.time() > (bot.state[name]['karma']['time'] + waittime):
            bot.state[name]['karma']['count'] = 0 
        bot.state[name]['karma']['count'] += 1
        if bot.state[name]['karma']['count'] > limit:
            if name in ratelimited: return 0
            ievent.reply("karma limit reached, you'll have to wait %s seconds" % int((bot.state[name]['karma']['time'] + waittime) - time.time()))
            ratelimited.append(name)
            return 0
        bot.state[name]['karma']['time'] = time.time()
        try: ratelimited.remove(name)
        except ValueError: pass
        return 1
    except Exception as ex: handle_exception(ievent)

## karma-get command

def handle_karmaget(bot, ievent):
    """ karma-get <item> .. show karma of item """
    if not ievent.rest: ievent.missing('<item>') ; return
    else: item = ievent.rest
    result = karma.get(item)
    if result: ievent.reply("%s has karma %s" % (item, str(result)))
    else: ievent.reply("%s has no karma yet" % item)

cmnds.add('karma-get', handle_karmaget, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-get', 'karma-get <item> .. show karma of <item>', 'karma-get dunker')

## karma-del command

def handle_karmadel(bot, ievent):
    """ karma-del <item> .. delete karma item """
    if not ievent.rest: ievent.missing('<item>') ; return
    item = ievent.rest
    result = karma.delete(item)
    if result: ievent.reply("%s deleted" % item)
    else: ievent.reply("can't delete %s" % item)

cmnds.add('karma-del', handle_karmadel, ['OPER'])
examples.add('karma-del', 'karma-del <item> .. delete karma item', 'karma-del dunker')

## karmaup RE

def handle_karmaup(bot, ievent):
    """ <item>++ ['#' <reason>] .. increase karma of item with optional \
        reason """
    if not ratelimit(bot, ievent): return
    (item, reason) = ievent.groups
    item = item.strip().lower()
    karma.upitem(item, reason=reason)
    karma.setwhoup(item, ievent.nick)
    ievent.reply('karma of '+ item + ' is now ' + str(karma.get(item)))

cmnds.add('^(.+)\+\+\s+#(.*)$', handle_karmaup, ['USER', 'KARMA', 'ANONKARMA'],  regex=True)
examples.add('++', "<item>++ ['#' <reason>] .. higher karma of item with 1 (use optional reason)", '1) tl++ 2) tl++ # top bot')

def handle_karmaup2(bot, ievent):
    """ increase karma without reason """
    ievent.groups += [None, ]
    handle_karmaup(bot, ievent)

cmnds.add('^(.+)\+\+$', handle_karmaup2, ['USER', 'ANON', 'ANONKARMA'], regex=True)

## karmadown RE

def handle_karmadown(bot, ievent):
    """ <item>-- ['#' <reason> .. decrease karma item with reason """
    if not ratelimit(bot, ievent): return
    (item, reason) = ievent.groups
    item = item.strip().lower()
    karma.down(item, reason=reason)
    karma.setwhodown(item, ievent.nick)
    ievent.reply('karma of ' + item + ' is now ' + str(karma.get(item)))

cmnds.add('^(.+)\-\-\s+#(.*)$', handle_karmadown, ['USER', 'KARMA', 'ANONKARMA'], regex=True)
examples.add('--', "<item>-- ['#' <reason>] .. lower karma of item with 1 (use optional reason)", '1) fuckbot-- 2) fuckbot-- # bad bot')

def handle_karmadown2(bot, ievent):
    """ decrease karma item without reason """
    ievent.groups += [None, ]
    handle_karmadown(bot, ievent)

cmnds.add('^(.+)\-\-$', handle_karmadown2, ['USER', 'KARMA', 'ANONKARMA'], regex=True)

## karma-whyup command

def handle_karmawhyup(bot, ievent):
    """ karma-whyup <item> .. show why karma of item has been increased """
    if not ievent.rest: ievent.missing('<item>') ; return
    item = ievent.rest
    result = karma.whykarmaup(item)
    if result: ievent.reply('whykarmaup of %s: ' % item, result)
    else: ievent.reply('%s has no reason for karmaup yet' % item)

cmnds.add('karma-whyup', handle_karmawhyup, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-whyup', 'karma-whyup <item> .. show the reason why karma of <item> was raised', 'karma-whyup ggzpreventie.nl')

## karma-whydown command

def handle_whykarmadown(bot, ievent):
    """ karma-whydown <item> .. show why karma of item has been decreased """
    if not ievent.rest: ievent.missing('<item>') ; return
    item = ievent.rest
    result = karma.whykarmadown(item)
    if result: ievent.reply('whykarmadown of %s: ' % item, result)
    else: ievent.reply('%s has no reason for karmadown yet' % item)

cmnds.add('karma-whydown', handle_whykarmadown, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-whydown', 'karma-whydown <item> .. show the reason why karma of <item> was lowered', 'karma-whydown ggzpreventie.nl')

## karma-good command

def handle_karmagood(bot, ievent):
    """ karma-good .. show top 10 karma items """
    result = karma.good(limit=10)
    if result:
        res = []
        for i in result:
            if i[1] > 0: res.append("%s=%s" % (i[0], i[1]))
        ievent.reply('goodness: ', res)
    else: ievent.reply('karma void')

cmnds.add('karma-good', handle_karmagood, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-good', 'show top 10 karma', 'karma-good')

## karma-bad command

def handle_karmabad(bot, ievent):
    """ karma-bad .. show 10 most negative karma items """
    result = karma.bad(limit=10)
    if result:
        res = []
        for i in result:
            if i[1] < 0: res.append("%s=%s" % (i[0], i[1]))
        ievent.reply('badness: ', res)
    else: ievent.reply('karma void')

cmnds.add('karma-bad', handle_karmabad, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-bad', 'show lowest top 10 karma', 'karma-bad')

## karma-whoup command

def handle_whokarmaup(bot, ievent):
    """ karma-whoup <item> .. show who increased a karma item """
    if not ievent.rest: ievent.missing('<item>') ; return
    item = ievent.rest
    result = karma.getwhoup(item)
    statdict = StatDict()
    if result:
        for i in result: statdict.upitem(i)
        res = []
        for i in statdict.top(): res.append("%s=%s" % i)
        ievent.reply("whokarmaup of %s: " % item, res)
    else: ievent.reply('no whokarmaup data available for %s' % item)

cmnds.add('karma-whoup', handle_whokarmaup, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-whoup', 'karma-whoup <item> .. show who raised the karma of <item>', 'karma-whoup ggzpreventie.nl')

## karma-whodown command

def handle_whokarmadown(bot, ievent):
    """ karma-whodown <item> .. show who decreased a karma item """
    if not ievent.rest: ievent.missing('<item>') ; return
    item = ievent.rest
    result = karma.getwhodown(item)
    statdict = StatDict()
    if result:
        for i in result: statdict.upitem(i)
        res = []
        for i in statdict.top(): res.append("%s=%s" % i)
        ievent.reply("whokarmadown of %s: " % item, res)
    else: ievent.reply('no whokarmadown data available for %s' % item)

cmnds.add('karma-whodown', handle_whokarmadown, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-whodown', 'karma-whodown <item> .. show who lowered the karma of <item>', 'karma-whodown ggzpreventie.nl')

## karma-search command

def handle_karmasearch(bot, ievent):
    """ karma-search <txt> .. search for karma items """
    what = ievent.rest
    if not what: ievent.missing('<txt>') ; return
    result = karma.search(what)
    if result:
        res = []
        for i in result: res.append("%s (%s)" % (i[0], i[1]))
        ievent.reply("karma items matching %s: " % what, res)
    else: ievent.reply('no karma items matching %s found' % what)

cmnds.add('karma-search', handle_karmasearch, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-search', 'karma-search <txt> .. search karma' , 'karma-search ggzpreventie.nl')

## karma-whatup command

def handle_karmawhatup(bot, ievent):
    """ show what karma items have been upped by nick """
    try: nick = ievent.args[0]
    except IndexError: ievent.missing('<nick>') ; return
    result = karma.whatup(nick)
    if result:
        res = []
        for i in result: res.append("%s (%s)" % i)
        ievent.reply("karma items upped by %s: " % nick, res)
    else: ievent.reply('no karma items upped by %s' % nick)

cmnds.add('karma-whatup', handle_karmawhatup, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-whatup', 'karma-whatup <nick> .. show what karma items <nick> has upped' , 'karma-whatup dunker')

## karma-whatdown command

def handle_karmawhatdown(bot, ievent):
    """ show what karma items have been lowered by nick """
    try: nick = ievent.args[0]
    except IndexError: ievent.missing('<nick>') ; return
    result = karma.whatdown(nick)
    if result:
        res = []
        for i in result: res.append("%s (%s)" % i)
        ievent.reply("karma items downed by %s: " % nick, res)
    else: ievent.reply('no karma items downed by %s' % nick)

cmnds.add('karma-whatdown', handle_karmawhatdown, ['USER', 'WEB', 'ANON', 'ANONKARMA'])
examples.add('karma-whatdown', 'karma-whatdown <nick> .. show what karma items <nick> has downed' , 'karma-whatdown dunker')

## plugin initialisation

def init():
    global db
    from tl.db import getmaindb
    db = getmaindb()
    setalias('k', 'karma-get')
    setalias('k-del', 'karma-del')
    setalias('whyup', 'karma-whyup')
    setalias('whydown', 'karma-whydown')
    setalias('good', 'karma-good')
    setalias('bad', 'karma-bad')
    setalias('whoup', 'karma-whoup')
    setalias('whodown', 'karma-whodown')
    setalias('k-search', 'karma-search')
    setalias('whatup', 'karma-whatup')
    setalias('whatdown', 'karma-whatdown')
