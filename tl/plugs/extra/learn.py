# tl/plugs/common/learn.py
#
#

""" learn information items .. facts .. factoids. """

## tl imports

from tl.lib.callbacks import callbacks
from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.aliases import setalias
from tl.utils.lazydict import LazyDict
from tl.lib.persist import PlugPersist, GlobalPersist

## basic imports

import logging

## learn command

def handle_learn(bot, event):
    """" arguments: <item> is <description> - set an information item. """
    if not event.rest: event.missing("<item> is <description>") ; return
    try: (what, description) = event.rest.split(" is ", 1)
    except ValueError: event.missing("<item> is <description>") ; return
    what = what.lower()
    items = GlobalPersist("learndb")
    if not items.data: items.data = LazyDict()
    if what not in items.data: items.data[what] = []
    if description not in items.data[what]: items.data[what].append(description)
    items.save()
    event.reply("%s item added to global database" % what)

cmnds.add('learn', handle_learn, ['OPER', 'USER', 'GUEST'])
examples.add('learn', 'learn the bot a description of an item.', "learn dunk is botpapa")

## learn-chan command

def handle_learnchan(bot, event):
    """" arguments: <item> is <description> - set an information item. """
    if not event.rest: event.missing("<item> is <description>") ; return
    try: (what, description) = event.rest.split(" is ", 1)
    except ValueError: event.missing("<item> is <description>") ; return
    what = what.lower()
    items = PlugPersist(event.channel)
    if not items.data: items.data = LazyDict()
    if what not in items.data: items.data[what] = []
    if description not in items.data[what]: items.data[what].append(description)
    items.save()
    event.reply("%s item added to %s database" % (what, event.channel))

cmnds.add('learn-chan', handle_learnchan, ['OPER', 'USER', 'GUEST'])
examples.add('learn-chan', 'learn the bot a description of an item. (channel specific)', "learn-chan dunk is botpapa")

## learn-forget command

def handle_forget(bot, event):
    """" arguments: <item> and <matchstring> - set an information item. """
    if not event.rest: event.missing("<item> and <match>") ; return
    try: (what, match) = event.rest.split(" and ", 2)
    except ValueError: event.missing("<item> and <match>") ; return
    what = what.lower()
    items = GlobalPersist("learndb")
    if not items.data: items.data = LazyDict()
    if what in items.data:
        for i in range(len(items.data[what])):
            if match in items.data[what][i]:
                del items.data[what][i]                
                break
        items.save()
    event.reply("item removed from global database")

cmnds.add('learn-forget', handle_forget, ['OPER', 'USER'])
examples.add('learn-forget', 'forget a description of an item.', "learn-forget dunk and botpapa")
setalias("forget", "learn-forget")

## learn-forgetchan command

def handle_forgetchan(bot, event):
    """" arguments: <item> and <matchstring> - set an information item. """
    if not event.rest: event.missing("<item> and <match>") ; return
    try: (what, match) = event.rest.split(" and ", 2)
    except ValueError: event.missing("<item> and <match>") ; return
    what = what.lower()
    items = PlugPersist(event.channel)
    if not items.data: items.data = LazyDict()
    if what in items.data:
        for i in range(len(items.data[what])):
            if match in items.data[what][i]:
                del items.data[what][i]                
                items.save()
                break
    event.reply("item removed from %s database" % event.channel)

cmnds.add('learn-forgetchan', handle_forgetchan, ['OPER', 'USER'])
examples.add('learn-forgetchan', 'forget a description of an item. (channel specific)', "learn-forgetchan dunk and botpapa")
setalias("forgetchan", "learn-forgetchan")

## learn-whatis command

def handle_whatis(bot, event):
    """ arguments: <item> - show what the bot has learned about a factoid. """
    items = PlugPersist(event.channel)
    what = event.rest.lower().split('!')[0].strip()
    result = []
    if what in items.data and items.data[what]: result = items.data[what]
    globalitems = GlobalPersist("learndb")
    if what in globalitems.data and globalitems.data[what]: result.extend(globalitems.data[what])
    if result: event.reply("%s is " % event.rest, result, dot=", ")
    else: event.reply("no information known about %s" % what)

cmnds.add('learn-whatis', handle_whatis, ['OPER', 'USER', 'GUEST'])
examples.add("learn-whatis", "whatis learned about a subject", "learn-whatis tl")
setalias("whatis", "learn-whatis")

## learn-items command

def handle_items(bot, event):
    """ no arguments - show what items the bot has learned. """
    items = list(PlugPersist(event.channel).data.keys())
    globalitems = list(GlobalPersist("learndb").data.keys())
    result = items + globalitems
    event.reply("i know %s items: " % len(result), result)

cmnds.add('learn-items', handle_items, ['OPER', 'USER', 'GUEST'])
examples.add("learn-items", "show what items the bot knows", "learn-items")
setalias("items", "learn-items")

## learn-searchitems command

def handle_searchitems(bot, event):
    """ argument: <searchtxt>  - search the items the bot has learned. """
    if not event.rest: event.missing("<searchtxt>") ; return
    items = list(PlugPersist(event.channel).data.keys())
    globalitems = list(GlobalPersist("learndb").data.keys())
    got = []
    for i in items + globalitems:
        if event.rest in i: got.append(i)
    event.reply("found %s items: " % len(got), got)

cmnds.add('learn-searchitems', handle_searchitems, ['OPER', 'USER', 'GUEST'])
examples.add("learn-searchitems", "search the items the bot knows", "learn-searchitems tl")
setalias("searchitems", "learn-searchitems")

## learn-toglobal command

def handle_learntoglobal(bot, event):
    """ argument: <searchtxt>  - search the items the bot has learned. """
    items = PlugPersist(event.channel)
    globalitems = GlobalPersist("learndb")
    for i in list(items.data.keys()):
        if i not in globalitems.data: globalitems.data[i] = []
        globalitems.data[i].extend(items.data)
    globalitems.save()
    event.reply("%s items copy to the global database. " % len(items.data))

cmnds.add('learn-toglobal', handle_learntoglobal, ['OPER', ])
examples.add("learn-toglobal", "move channel specific learn data to the global database.", "learn-toglobal")

## callbacks

def prelearn(bot, event):
    """ learn precondition. """
    if event.iscommand: return False
    if len(event.txt) < 2: return False
    if event.txt and (event.txt[0] == "?" or event.txt[-1] == "?") and not event.forwarded: return True
    return False

def learncb(bot, event):
    """ learn callback, is for catching ? queries. """
    if bot.type == "convore" and not event.chan.data.enable: return
    event.bind(bot)
    result = []
    items = PlugPersist(event.channel)
    target = event.txt.lower()
    if target[0] == "?": target = target[1:]
    if target[-1] == "?": target = target[:-1]
    if target in items.data: result = items.data[target]
    globalitems = GlobalPersist("learndb")
    if target in globalitems.data:
        if not target in result: result.extend(globalitems.data[target])    
    if result: event.reply("%s is " % target, result, dot=", ")
    event.ready()

callbacks.add("PRIVMSG", learncb, prelearn)
callbacks.add("MESSAGE", learncb, prelearn)
callbacks.add("DISPATCH", learncb, prelearn)
callbacks.add("CONSOLE", learncb, prelearn)
callbacks.add("EVENT", learncb, prelearn)
callbacks.add("CONVORE", learncb, prelearn)
callbacks.add("BLIP_SUBMITTED", learncb, prelearn)
callbacks.add("TORNADO", learncb, prelearn)
