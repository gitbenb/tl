# tl/plugs/core.admin.py
#
#

""" admin related commands. these commands are mainly for maintaining the bot. """

## tl imports

from tl.lib.eventhandler import mainhandler
from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.persist import Persist
from tl.lib.boot import savecmndtable, savepluginlist, boot, plugin_packages, clear_tables, getcmndtable, getcallbacktable
from tl.lib.plugins import plugs
from tl.lib.botbase import BotBase
from tl.lib.exit import globalshutdown
from tl.lib.config import getmainconfig
from tl.utils.generic import stringsed, getwho
from tl.utils.exception import handle_exception
from tl.lib.aliases import setalias
from tl.lib.fleet import getfleet
from tl.lib.plugins import plugs

## basic imports

import logging

## admin-save command

def handle_adminsave(bot, ievent):
    """ no arguments - boot the bot .. do some initialisation. """
    ievent.reply("saving mainconfig")
    getmainconfig().save()
    ievent.reply("saving fleet bots")
    getfleet().save()
    ievent.reply("saving all plugins")
    plugs.save()
    ievent.done()

cmnds.add('admin-save', handle_adminsave, 'OPER')
examples.add('admin-save', 'initialize the bot', 'admin-boot')

## admin-boot command

def handle_adminboot(bot, ievent):
    """ no arguments - boot the bot .. do some initialisation. """
    ievent.reply("reloading all plugins")
    if 'saveperms' in ievent.rest: boot(force=True, saveperms=True, clear=True)
    else: boot(force=True, saveperms=False, clear=True)
    ievent.done()

cmnds.add('admin-boot', handle_adminboot, 'OPER')
examples.add('admin-boot', 'initialize the bot', 'admin-boot')

## admin-bootthreaded command

def handle_adminbootthreaded(bot, ievent):
    """ no arguments - boot the bot .. do some initialisation. """
    ievent.reply("reloading all plugins")
    if 'saveperms' in ievent.rest: boot(force=True, saveperms=True, clear=True)
    else: boot(force=True, saveperms=False, clear=True)
    ievent.done()

cmnds.add('admin-bootthreaded', handle_adminbootthreaded, 'OPER', threaded=True)
examples.add('admin-bootthreaded', 'initialize the bot in a seperate thread', 'admin-bootthreaded')

## admin-bootbackend command

def handle_adminbootbackend(bot, ievent):
    """ no arguments - boot the bot .. do some initialisation. """
    ievent.reply("reloading all plugins")
    if 'saveperms' in ievent.rest: boot(force=True, saveperms=True, clear=True)
    else: boot(force=True, saveperms=False, clear=True)
    ievent.done()

cmnds.add('admin-bootbackend', handle_adminbootbackend, 'OPER', threaded="backend")
examples.add('admin-bootbackend', 'initialize the bot on a backend', 'admin-bootbackend')

## admin-commands command

def handle_admincommands(bot, ievent):
    """ no arguments - load all available plugins. """
    cmnds = getcmndtable()
    if not ievent.rest: ievent.reply("commands: ", cmnds)
    else:
        try: ievent.reply("%s command is found in %s " % (ievent.rest, cmnds[ievent.rest]))
        except KeyError: ievent.reply("no such commands available") 

cmnds.add('admin-commands', handle_admincommands, 'OPER')
examples.add('admin-commands', 'show runtime command table', 'admin-commands')

## admin-callbacks command

def handle_admincallbacks(bot, ievent):
    """ no arguments - load all available plugins. """
    cbs = getcallbacktable()
    if not ievent.rest: ievent.reply("callbacks: ", cbs)
    else:
        try: ievent.reply("%s callbacks: " % ievent.rest, cbs[ievent.rest])
        except KeyError: ievent.reply("no such callbacks available") 

cmnds.add('admin-callbacks', handle_admincallbacks, 'OPER')
examples.add('admin-callbacks', 'show runtime callback table', 'admin-callbacks')

## admin-userhostscache command

def handle_userhostscache(bot, ievent):
    """ no arguments - show userhostscache of the bot the command is given on. """
    ievent.reply("userhostcache of %s: " % ievent.channel, list(bot.userhosts.keys()) + list(bot.userhosts.values()))

cmnds.add('admin-userhostscache', handle_userhostscache, 'OPER')
examples.add('admin-userhostscache', 'show userhostscache ', 'admin-userhostscache')

## admin-loadall command

def handle_loadall(bot, ievent):
    """ no arguments - load all available plugins. """
    plugs.loadall(plugin_packages, force=True)
    ievent.done()

cmnds.add('admin-loadall', handle_loadall, 'OPER', threaded=True)
examples.add('admin-loadall', 'load all plugins', 'admin-loadall')

## admin-errors command

def handle_adminerrors(bot, ievent):
    """ no arguments - show logged errors (not exceptions). """
    from tl.utils.log import errors
    if errors: ievent.reply("errors so far: ", errors)
    else: ievent.reply("no errors")

cmnds.add('admin-errors', handle_adminerrors, 'OPER')
examples.add('admin-errors', 'show logged errors so far (not exceptions)', 'admin-errors')

## admin-makebot command

def handle_adminmakebot(bot, ievent):
    """ arguments: <botname> <bottype> - create a bot of given type. """
    try: botname, bottype = ievent.args
    except ValueError: ievent.missing("<name> <type>") ; return
    newbot = BotBase()
    newbot.botname = botname
    newbot.type = bottype
    newbot.owner = bot.owner
    newbot.save()
    ievent.done()

cmnds.add('admin-makebot', handle_adminmakebot, 'OPER')
examples.add('admin-makebot', 'create a bot', 'admin-makebot cmndxmpp xmpp')

## admin-stop command

def handle_adminstop(bot, ievent):
    """ no arguments - stop the bot. """
    if bot.ownercheck(ievent.userhost): mainhandler.put(0, globalshutdown)
    else: ievent.reply("you are not the owner of the bot")
    ievent.done(silent=True)
    
cmnds.add("admin-stop", handle_adminstop, "OPER")
examples.add("admin-stop", "stop the bot.", "stop")
setalias("qq", "admin-stop")

## admin-setstatus command

def handle_adminsetstatus(bot, event):
    """ arguments: <status> [<statustxt>] - set the status of the bot (xmpp). """
    if bot.type != "sxmpp": event.reply("this command only works on sxmpp bots (for now)") ; return
    if not event.rest: event.missing("<status> [<show>]") ; return
    status = event.args[0]
    try: show = event.args[1]
    except IndexError: show = ""
    bot.setstatus(status, show)

cmnds.add("admin-setstatus", handle_adminsetstatus, ["STATUS", "OPER"])
examples.add("admin-setstatus", "set status of sxmpp bot", "admin-setstatus available Yooo dudes !")

## admin-reloadconfig command

def handle_adminreloadconfig(bot, event):
    """ no arguments - reload bot config and mainconfig files. """
    try:
        bot.cfg.reload()
        getmainconfig().reload()
    except Exception as ex: handle_exception()
    event.done()

cmnds.add("admin-reloadconfig", handle_adminreloadconfig, ["OPER"])
examples.add("admin-reloadconfig", "reload mainconfig", "admin-reloadconfig")

## admin-exceptions command

def handle_adminexceptions(bot, event):
    """ no arguments - show exceptions raised in the bot. """
    from tl.utils.exception import exceptionlist, exceptionevents
    for e, ex in exceptionevents: logging.warn("%s - exceptions raised is %s" % (e.bot.cfg.name, ex))
    event.reply("exceptions raised: ", exceptionlist, dot="<br><br>")

cmnds.add("admin-exceptions", handle_adminexceptions, ["OPER"])
examples.add("admin-exceptions", "show exceptions raised", "admin-exceptions")

## admin-debugon command

def handle_admindebugon(bot, event):
    """ no arguments - enable debug on a channel. """
    event.chan.data.debug = True;
    event.chan.save()
    event.reply("debugging is enabled for %s" % event.channel)

cmnds.add("admin-debugon", handle_admindebugon, ['OPER', ])
examples.add("admin-debugon", "enable debug on a channel.", "admin-debugon")

## admin-debugoff command

def handle_admindebugoff(bot, event):
    """ no arguments - disable debug on a channel. """
    event.chan.data.debug = False;
    event.chan.save()
    event.reply("debugging is disabled for %s" % event.channel)

cmnds.add("admin-debugoff", handle_admindebugoff, ['OPER', ])
examples.add("admin-debugoff", "disable debug on a channel.", "admin-debugoff")

## admin-mc command

def handle_adminmc(bot, event):
    """ flush memcached. """
    if event.rest == "stats":
        try:
            from tl.memcached import mc
            test = mc.get_stats()
            if not test: event.reply("no memcached found")
            else: event.reply("memcached stats: ", test[0][1])
        except Exception as ex:
            event.reply("memcached error: %s" % str(ex))
    elif event.rest == "flushall":
        try:
            from tl.memcached import mc
            if mc: test = mc.flush_all() ; event.done()
            else: event.reply("no memcached running")
        except Exception as ex:
            event.reply("memcached error: %s" % str(ex))
    else: event.reply("choose one of stats, flushall")

cmnds.add("admin-mc", handle_adminmc, "OPER")
examples.add("admin-mc", "bots interdace to memcached", "1) admin-mc stats 2) admin-mc flushall")

## admin-floodcontrol command

def handle_adminfloodcontrol(bot, event):
    """ no arguments - disable debug on a channel. """
    try:
        who, threshold = event.args
        threshold = int(threshold) 
    except ValueError: event.missing("<userhost> <threshold> [period] [wait]") ; return
    userhost = getwho(bot, who)
    if userhost: user = bot.users.getuser(userhost)
    else: user = bot.users.byname(who)
    if not user: event.reply("i don't know a user %s" % who) ; return
    if "OPER" in user.data.perms: event.reply("no flood control for OPER") ; return
    try: period = event.args[2]
    except IndexError: period = 60
    try: wait = event.args[3]
    except IndexError: wait = 120
    if threshold < 1: threshold = 1
    user.data.floodtime = period
    user.data.floodthreshold = threshold
    user.data.floodwait = wait
    user.data.floodrate = 1
    user.save()
    from tl.lib.floodcontrol import floodcontrol
    for u in user.data.userhosts: floodcontrol.reset(u)
    event.reply("floodrate for %s set to %s" % (user.data.name, threshold))

cmnds.add("admin-floodcontrol", handle_adminfloodcontrol, ['OPER', ])
examples.add("admin-floodcontrol", "set the floodcontrol parameters of a user", "1) admin-floodcontrol dunker 20 2) admin-floodcontrol dunker 20 300 500")

## admin-status command

def handle_adminstatus(bot, event):
    from tl.lib.runner import allrunners
    result = {}
    for runner in allrunners:
        result[runner.name] = runner.status(event.rest)
    event.reply("current runner status: ", result)

cmnds.add("admin-status", handle_adminstatus, "OPER")
examples.add("admin-status", "show status of current runners", "admin-status")
 
#### BHJTW 6-03-2012