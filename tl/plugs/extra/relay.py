# tl/plugs/common/relay.py
#
#

""" relay to other users/channels. """

## tl imports

from tl.lib.commands import cmnds
from tl.lib.callbacks import first_callbacks
from tl.lib.persist import PlugPersist
from tl.lib.examples import examples
from tl.lib.fleet import getfleet
from tl.lib.errors import NoSuchWave
from tl.utils.exception import handle_exception
from tl.utils.generic import stripcolor

## basic imports

import logging
from copy import deepcopy as cpy

# plugin state .. this is where the relay plugin data lives. It's JSON string
# put into the database with memcache in between. The data is accessible
# through object.data. When data changes call object.save()
# see tl/persist/persist.py

block = PlugPersist('block')
relay = PlugPersist('relay')

## CALLBACKS

# these are the callbacks that do the hard work of the relay plugin takes 
# place. The precondition is called to see whether the callback should fire 
# or not. It should return True or False.
# see tl/callbacks.py
  
def relayprecondition(bot, event):
    """ precondition to check whether the callback needs to be executed. """
    if event.how == "background": return False
    if event.isrelayed: logging.info("%s already relayed" % bot.cfg.name) ; return False
    if event.forwarded: logging.info("%s forarded" % bot.cfg.name) ; return False
    txt = event.txt.strip()
    if txt:
        txt = txt.lower()
        if event.nick and bot.cfg.nick and (txt.startswith("[%s]" % event.nick.lower()) or txt.find("[%s]" % bot.cfg.nick.lower()) != -1): return False 
    origin = str((bot.cfg.name, event.printto or event.channel))
    logging.debug("precondition - origin is %s" % origin)
    if event.txt:
        if origin and origin in relay.data: return True
    return False

# CORE BUSINESS

# this callback does all the relaying. It receives the event that triggered
# the callback and checks whether there are relays for the channel the event
# took place (the bot uses the users JID in the jabber and web case (web users
# must be registered)

def relaycallback(bot, event):
    """ this is the callbacks that handles the responses to questions. """
    # determine where the event came from
    #event.isrelayed = True
    e = cpy(event)
    origin = str((bot.cfg.name, e.channel))
    e.isrelayed = True
    e.headlines = True
    try:
        # loop over relays for origin
        for botname, type, target in relay.data[origin]:
            try:
                logging.debug('trying relay of %s to (%s,%s)' % (origin, type, target))
                #if target == origin: continue
                # tests to prevent looping
                if origin == (botname, target): continue
                # check whether relay is blocked
                if origin in block.data:
                    if [botname, type, target] in block.data[origin]: continue
                # retrieve the bot from fleet (based on type)
                fleet = getfleet()
                outbot = fleet.byname(botname)
                if not outbot: outbot = fleet.makebot(type, botname)
                if outbot:
                    logging.info('outbot found - %s - %s' % (outbot.cfg.name, outbot.type))
                    # we got bot .. use it to send the relayed message
                    if e.nick == bot.cfg.nick: txt = "[!] %s" % e.txt
                    else: txt = "[%s] %s" % (e.nick, e.txt)
                    if event: t = "[%s]" % outbot.cfg.nick
                    logging.debug("sending to %s (%s)" % (target, outbot.cfg.name)) 
                    txt = outbot.normalize(txt)
                    txt = stripcolor(txt)
                    outbot.outnocb(target, txt, "normal", event=e)
                else: logging.info("can't find bot for (%s,%s,%s)" % (botname, type, target))
            except Exception as ex: handle_exception()
    except KeyError: pass

# MORE CORE BUSINESS
# this is the place where the callbacks get registered. The first argument is
# the string representation of the event type, MESSAGE is for jabber message,
# EXEC is for the gadget handling, WEB for the website, BLIP_SUBMITTED for
# wave and OUTPUT for the outputcache (both used in wave and web).

first_callbacks.add('MESSAGE', relaycallback, relayprecondition)
first_callbacks.add('EXEC', relaycallback, relayprecondition)
first_callbacks.add('WEB', relaycallback, relayprecondition)
first_callbacks.add('BLIP_SUBMITTED', relaycallback, relayprecondition)
first_callbacks.add('OUTPUT', relaycallback, relayprecondition)
first_callbacks.add('PRIVMSG', relaycallback, relayprecondition)
first_callbacks.add('CONVORE', relaycallback, relayprecondition)
first_callbacks.add('TORNADO', relaycallback, relayprecondition)

## COMMANDS

# this is where the commands for the relay plugin are defined, Arguments to a
# command function are the bot that the event occured on and the event that
# triggered the command. Think the code speaks for itself here ;]

## relay command

def handle_relay(bot, event):
    """ arguments: [<botname>] [<type>] <target> .. open a relay to a user. all input from us will be relayed. """
    try: (botname, type, target) = event.args
    except ValueError:
        try: botname = bot.cfg.name ; (type, target) = event.args
        except ValueError:
            try: botname = bot.cfg.name ; type = bot.cfg.bottype ; target = event.args[0]
            except IndexError: event.missing('[<botname>] [<bottype>] <target>') ; return 
    origin = str((bot.cfg.name, event.channel))
    if not getfleet().byname(botname): event.reply("no %s bot in fleet." % botname) ; return
    if origin not in relay.data: relay.data[origin] = []
    try:
        if not [type, target] in relay.data[origin]:
            relay.data[origin].append([botname, type, target])
            relay.save()
    except KeyError: relay.data[origin] = [[botname, type, target], ] ; relay.save()
    event.done()

cmnds.add('relay', handle_relay, ['OPER',])
examples.add('relay', 'open a relay to another user/channel', '1) relay default-sxmpp sxmpp feedbackloop@gmail.com')

## relay-stop command

def handle_relaystop(bot, event):
    """ arguments: [<botname>] [<bottype>] [<channel>] - stop a relay to a user. all relaying from the target will be ignored. """
    try: (botname, type, target) = event.args
    except ValueError:
        try: botname = bot.cfg.name ; (type, target) = event.args
        except (IndexError, ValueError): botname = bot.cfg.name ; type = bot.type ; target = event.channel 
    origin = str((bot.cfg.name, event.origin or event.channel))
    try:
        logging.debug('trying to remove relay (%s,%s)' % (type, target))
        relay.data[origin].remove([botname, type, target])
        relay.save()
    except (KeyError, ValueError):
        origin = event.origin or event.channel
        try:
            logging.debug('trying to remove relay (%s,%s)' % (type, target))
            relay.data[origin].remove([botname, type, target])
            relay.save()
        except (KeyError, ValueError): pass
    event.done()

cmnds.add('relay-stop', handle_relaystop, ['OPER',' USER'])
examples.add('relay-stop', 'close a relay to another user', 'relay-stop feedbackloop@gmail.com')

## relay-clear command

def handle_relayclear(bot, event):
    """ no arguments - clear all relays from a channel. all relaying to target will be ignored. """
    origin = str((bot.cfg.name, event.origin or event.channel))
    try:
        logging.debug('clearing relay for %s' % origin)
        relay.data[origin] = []
        relay.save()
    except (KeyError, ValueError):
        try:
            origin = event.origin or event.channel
            logging.debug('clearing relay for %s' % origin)
            relay.data[origin] = []
            relay.save()
        except (KeyError, ValueError): pass
    event.done()

cmnds.add('relay-clear', handle_relayclear, ['OPER',])
examples.add('relay-clear', 'clear all relays from a channel', 'relay-clear')

## relay-list command

def handle_askrelaylist(bot, event):
    """ no arguments - show all relay's of a user. """
    origin = str((bot.cfg.name, event.origin or event.channel))
    try: event.reply('relays for %s: ' % origin, relay.data[origin])
    except KeyError: event.reply('no relays for %s' % origin)

cmnds.add('relay-list', handle_askrelaylist, ['OPER', 'USER'])
examples.add('relay-list', 'show all relays of user/channel/wave.', 'relay-list')

## relay-block command

def handle_relayblock(bot, event):
    """ arguments: <bottype> <target> .. block a user/channel/wave from relaying to us. """
    try: (type, target) = event.args
    except ValueError: event.missing('<bottype> <target>') ; return 
    origin = str((bot.cfg.name, event.origin or event.channel))
    if origin not in block.data: block.data[origin] = []
    if not [type, origin] in block.data[target]: block.data[target].append([type, origin]) ; block.save()
    event.done()

cmnds.add('relay-block', handle_relayblock, ['OPER', 'USER'])
examples.add('relay-block', 'block a relay from another user', 'relay-block feedbackloop@gmail.com')

## relay-unblock command

def handle_relayunblock(bot, event):
    """ arguments: <target> .. remove a relay block of an user. """
    try: target = event.args[0]
    except IndexError: event.missing('<target>') ; return 
    origin = str((bot.cfg.name, event.origin or event.channel))
    try: block.data[origin].remove([bot.cfg.name, target]) ; block.save()
    except (KeyError, ValueError): pass
    event.done()

cmnds.add('relay-unblock', handle_relaystop, ['OPER', 'USER'])
examples.add('relay-unblock', 'remove a block of another user', 'relay-unblock feedbackloop@gmail.com')

## relay-blocklist command

def handle_relayblocklist(bot, event):
    """ no arguments - show all blocks of a user/channel.wave. """
    origin = str((bot.cfg.name, event.origin or event.channel))
    try: event.reply('blocks for %s: ' % origin, block.data[origin])
    except KeyError: event.reply('no blocks for %s' % origin)

cmnds.add('relay-blocklist', handle_relayblocklist, ['OPER', 'USER'])
examples.add('relay-blocklist', 'show blocked relays to us', 'relay-blocklist')
