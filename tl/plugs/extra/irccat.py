# tl/plugs/socket/irccat2.py
#
#

"""
    irccat2.py - tl "irccat2" Module

    Copyright 2011, Richard Bateman
    Licensed under the New BSD License.

    Written to be used in the #firebreath IRC channel: http://www.firebreath.org

    To test, set up the host and port, then use something like:

    echo "@taxilian I am awesome" | netcat -g0 localhost 54321

    echo "#channel I am awesome" | netcat -g0 localhost 54321

    you can specify multiple users (with @) and channels (with #) by seperating them
    with commas.  Not that with jabber, channels tend to be treated as users
    unless you set up an alias in your channel:

    !irccat-add_alias #channel

    BHJTW - 28-02-2012 .. move to irccat2.py to use the normal irccat-cfg functions
    BHJTW - 15-08-2012 .. ported to GGZBOT
    BHJTW - 28-09-2012 .. ported to TIMELINE

"""

## tl imports

from tl.utils.exception import handle_exception
from tl.lib.threads import start_new_thread
from tl.lib.persist import PlugPersist
from tl.lib.fleet import getfleet
from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.callbacks import callbacks
from tl.lib.persistconfig import PersistConfig
from tl.utils.generic import fromenc, toenc

## basic imports

import logging
import time

## plugin configuration

cfg = PersistConfig()
cfg.define("botnames", ["default-sxmpp","default-irc"])
cfg.define("host", "localhost")
cfg.define("port", "54321")
cfg.define("aliases", {})
cfg.define("enable", False)

## SocketServer imports

import socketserver
from socketserver import ThreadingMixIn, StreamRequestHandler

## defines

shared_data = {}

server = None

## IrcCatListener class

class IrcCatListener(ThreadingMixIn, StreamRequestHandler):
    def handle(self):
        try:
            fleet = getfleet()
            msg = str(self.rfile.readline().strip())
            logging.warn("received %s" % msg)
            dest, msg = self.splitMsg(msg)
            for chan in dest:
                logging.info("sending to %s" % chan)
                for botname in fleet.list():
                    if botname not in cfg.botnames: continue
                    bot = fleet.byname(botname)
                    if bot: bot.say(chan, msg)
                    else: logging.error("can't find %s bot in fleet" % botname)
        except Exception as ex: handle_exception()

    def splitMsg(self, message):
        if message[0] not in ('#', '@'): return [], message
        if not message: return [], message
        if message.startswith('"'): messsage = message[1:-1]
        dest, message = message.split(" ", 1)
        dest = dest.split(",")
        finalDest = []
        for d in dest:
            if not d: continue
            d = d.strip().strip("@")
            finalDest.append(d)
            if d in list(cfg["aliases"].keys()):
                for alias in cfg["aliases"][d]:
                    finalDest.append(alias)
        return finalDest, message

## load on START

def irccatstart(bot, event): pass

callbacks.add("START", irccatstart)

## plugin init

def init_threaded():
    global server
    if server: logging.warn("irccat server is already running.") ; return
    if not cfg.enable: logging.warn("irccat is not enabled.") ; return 
    time.sleep(2)
    if not cfg.host or not cfg.port:
        cfg["host"] = "localhost"
        cfg["port"] = 54321
        cfg["botnames"] = ["default-sxmpp",]
        cfg["aliases"] = {}
    if not cfg.aliases: cfg.aliases = {}
    cfg.save()
    try:
        server = socketserver.TCPServer((cfg["host"], int(cfg["port"])), IrcCatListener)
    except Exception as ex: logging.error("%s - %s:%s" % (str(ex), cfg["host"], cfg["port"])) ; return
    logging.warn("starting irccat server on %s:%s" % (cfg["host"], cfg["port"]))
    thr = start_new_thread(server.serve_forever, ())
    thr.join(3)

def shutdown():
    global server
    if server:
        logging.warn("shutting down the irccat server")
        start_new_thread(server.shutdown, ())
        time.sleep(2)

## irccat-addalias command

def handle_irccat_add_alias(bot, ievent):
    if len(ievent.args) != 1:
        ievent.reply("syntax: irccat-addalias <alias> (where <alias> is the channel you want notifications for)")
        return
    dest = ievent.args[0]
    if not cfg.aliases: cfg.aliases = {}
    if dest not in cfg["aliases"]:
        cfg["aliases"][dest] = []
    if ievent.channel not in cfg["aliases"][dest]:
        cfg["aliases"][dest].append(ievent.channel)
    cfg.save()
    ievent.reply("%s will now receive irccat messages directed at %s" % (ievent.channel, dest))
cmnds.add("irccat-addalias", handle_irccat_add_alias, ['OPER'])
examples.add("irccat-addalias", "add an alias to the current channel from the specified one", "irccat-addalias #firebreath")

## irccat-listaliases command

def handle_irccat_list_aliases(bot, ievent):
    """ List all aliases defined for the current channel """
    aliases = [dest for dest, chanlist in cfg["aliases"].items() if ievent.channel in chanlist]

    ievent.reply("%s is receiving irccat messages directed at: %s" % (ievent.channel, ", ".join(aliases)))
cmnds.add("irccat_-listaliases", handle_irccat_list_aliases, ['OPER'])
examples.add("irccat-listaliases", "lists the aliases for the current channel", "irccat-listaliases")

## irccat-delalias command

def handle_irccat_del_alias(bot, ievent):
    if len(ievent.args) != 1:
        ievent.reply("syntax: irccat-delalias <alias> (where <alias> is the channel you no longer want notifications for)")
        return
    dest = ievent.args[0]
    if dest not in cfg["aliases"]or ievent.channel not in cfg["aliases"][dest]:
        ievent.reply("%s is not an alias for %s" % (ievent.channel, dest))
        return
    cfg["aliases"][dest].remove(ievent.channel)
    ievent.reply("%s will no longer receive irccat messages directed at %s" % (ievent.channel, dest))
    cfg.save()
cmnds.add("irccat-delalias", handle_irccat_del_alias, ['OPER'])
examples.add("irccat-delalias", "add an alias to the current channel from the specified one", "irccat-delalias #firebreath")

## irccat-enable command

def handle_irccat_enable(bot, event):
    cfg.enable = True ; cfg.save() ; event.done()
    init_threaded()
    
cmnds.add("irccat-enable", handle_irccat_enable, "OPER")
examples.add("irccat-enable", "enable irccat server", "irccat-enable")

## irccat-disable command

def handle_irccat_disable(bot, event):
    cfg.enable = False ; cfg.save() ; event.done()
    shutdown()
    
cmnds.add("irccat-disable", handle_irccat_disable, "OPER")
examples.add("irccat-disable", "disable irccat server", "irccat-disable")
