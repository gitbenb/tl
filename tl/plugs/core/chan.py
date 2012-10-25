# tl/plugs/core/chan.py
#
#

""" channel related commands. """

## tl imports

from tl.lib.persist import Persist
from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.callbacks import callbacks
from tl.lib.channelbase import ChannelBase
from tl.lib.datadir import getdatadir
from tl.utils.exception import handle_exception

## basic imports

import os
import logging

## chan-join command

def handle_chanjoin(bot, ievent):
    """ arguments: <channel> - join a channel/conference/wave"""
    try: channel = ievent.rest
    except IndexError:
        ievent.missing("<channel> [password]")   
        return
    try: password = ievent.args[1]
    except IndexError: password = None
    bot.join(channel, password=password)
    ievent.done()

cmnds.add('chan-join', handle_chanjoin, ['OPER', 'JOIN'])
cmnds.add('join', handle_chanjoin, ['OPER', 'JOIN'])
examples.add('chan-join', 'chan-join <channel> [password]', '1) chan-join #test 2) chan-join #test mekker')

## chan-del command

def handle_chandel(bot, ievent):
    """ arguments: <channel> - remove channel from bot.cfg.channels. """
    try: chan = ievent.args[0].lower()
    except IndexError:  
        ievent.missing("<channel>")
        return
    try:
        if bot.state:
            bot.cfg.channels.remove(chan)
            bot.cfg.save()
    except ValueError: pass
    ievent.done()

cmnds.add('chan-del', handle_chandel, 'OPER')
examples.add('chan-del', 'remove channel from bot.channels', 'chan-del #mekker')

## chan-part command

def handle_chanpart(bot, ievent):
    """ arguments: [<channel>] - leave a channel (provided or current channel). """
    if not ievent.rest: chan = ievent.channel
    else: chan = ievent.rest
    ievent.reply('leaving %s chan' % chan)
    bot.part(chan)
    ievent.done()

cmnds.add('chan-part', handle_chanpart, 'OPER')
cmnds.add('part', handle_chanpart, 'OPER')
examples.add('chan-part', 'chan-part [<channel>]', '1) chan-part 2) chan-part #test')

## chan-list command

def handle_chanlist(bot, ievent):
    """ no arguments - channels .. show joined channels. """
    if bot.state: chans = bot.cfg.channels 
    else: chans = []
    if chans: ievent.reply("joined channels: ", chans)
    else: ievent.reply('no channels joined')

cmnds.add('chan-list', handle_chanlist, ['USER', 'GUEST'])
examples.add('chan-list', 'show what channels the bot is on', 'chan-list')

## chan-cycle command

def handle_chancycle(bot, ievent):
    """ no arguments - recycle channel. """
    ievent.reply('cycling %s' % ievent.channel)
    bot.part(ievent.channel)
    try: key = ievent.chan.data.password
    except (KeyError, TypeError): key = None
    bot.join(ievent.channel, password=key)  
    ievent.done()

cmnds.add('chan-cycle', handle_chancycle, 'OPER')
examples.add('chan-cycle', 'part/join channel', 'chan-cycle')

## chan-silent command

def handle_chansilent(bot, ievent):
    """ arguments [<channel>] - set silent mode of channel. """
    if ievent.rest: channel = ievent.rest.split()[0].lower()
    else:
        if ievent.cmnd == 'DCC': return
        channel = ievent.channel
    ievent.reply('putting %s to silent mode' % channel)
    ievent.chan.data.silent = True
    ievent.chan.save()
    ievent.done()

cmnds.add('chan-silent', handle_chansilent, 'OPER')
examples.add('chan-silent', 'set silent mode on channel the command was given in', 'chan-silent')

## chan-loud command

def handle_chanloud(bot, ievent):
    """ arguments: [<channel>] - enable output to the channel. """
    if ievent.rest: channel = ievent.rest.split()[0].lower()
    else:
        if ievent.cmnd == 'DCC': return
        channel = ievent.channel
    ievent.reply('putting %s into loud mode' % ievent.channel)
    ievent.chan.data.silent= False
    ievent.chan.save()
    ievent.done()

cmnds.add('chan-loud', handle_chanloud, 'OPER')
examples.add('chan-loud', 'disable silent mode of channel command was given in', 'chan-loud')

## chan-withnotice command

def handle_chanwithnotice(bot, ievent):
    """ arguments: [<channel>] - make bot use notice in channel. """
    if ievent.rest: channel = ievent.rest.split()[0].lower()
    else:
        if ievent.cmnd == 'DCC': return
        channel = ievent.channel
    ievent.reply('setting notice in %s' % channel)
    ievent.chan.data.how  = "notice"
    ievent.chan.save()
    ievent.done()
    
cmnds.add('chan-withnotice', handle_chanwithnotice, 'OPER')
examples.add('chan-withnotice', 'make bot use notice on channel the command was given in', 'chan-withnotice')

## chan-withprivmsg command

def handle_chanwithprivmsg(bot, ievent):
    """ arguments: [<channel>] - make bot use privmsg in channel. """
    if ievent.rest: channel = ievent.rest.split()[0].lower()
    else:
        if ievent.cmnd == 'DCC': return
        channel = ievent.channel
    ievent.reply('setting privmsg in %s' % ievent.channel)
    ievent.chan.data.how = "msg"
    ievent.chan.save()
    ievent.done()

cmnds.add('chan-withprivmsg', handle_chanwithprivmsg, 'OPER')
examples.add('chan-withprivmsg', 'make bot use privmsg on channel command was given in', 'chan-withprivmsg')

## chan-mode command

def handle_channelmode(bot, ievent):
    """ arguments: [<channel>] - show channel mode. """
    if bot.type != 'irc':
        ievent.reply('channelmode only works on irc bots')
        return
    try: chan = ievent.args[0].lower()
    except IndexError: chan = ievent.channel.lower()
    if not chan in bot.cfg.channels:
        ievent.reply("i'm not on channel %s" % chan)
        return
    ievent.reply('channel mode of %s is %s' % (chan, ievent.chan.data.mode))

cmnds.add('chan-mode', handle_channelmode, 'OPER')
examples.add('chan-mode', 'show mode of channel', '1) chan-mode 2) chan-mode #test')

## mode callback

def modecb(bot, ievent):
    """ callback to detect change of channel key. """
    if ievent.postfix.find('+k') != -1:
        key = ievent.postfix.split('+k')[1]
        ievent.chan.data.key = key
        ievent.chan.save()

callbacks.add('MODE', modecb)

## chan-denyplug command

def handle_chandenyplug(bot, event):
    """ arguments: <plugname> - deny a plugin to be active in a channel. """
    if not event.rest: event.missing("<plugin name>") ; return
    if not event.rest in event.chan.data.denyplug:
        event.chan.data.denyplug.append(event.rest)
        event.chan.save()
        event.done()
    else: event.reply("%s is already being denied in channel %s" % (event.rest, event.channel))

cmnds.add("chan-denyplug", handle_chandenyplug, 'OPER')
examples.add("chan-denyplug", "deny a plugin command or callbacks to be executed in a channel", "chan-denyplug idle")

## chan-allowplug command

def handle_chanallowplug(bot, event):
    """ arguments: <plugname> - allow a plugin to be active in a channel. """
    if not event.rest: event.missing("<plugin name>") ; return
    if event.rest in event.chan.data.denyplug:
        event.chan.data.denyplug.remove(event.rest)
        event.chan.save()
        event.done()
    else: event.reply("%s is already being allowed in channel %s" % (event.rest, event.channel))

cmnds.add("chan-allowplug", handle_chanallowplug, 'OPER')
examples.add("chan-allowplug", "allow a plugin command or callbacks to be executed in a channel", "chan-denyplug idle")

## chan-allowcommand command

def handle_chanallowcommand(bot, event):
    """ allow a command in the channel. """
    try: cmnd = event.args[0] 
    except (IndexError, KeyError): event.missing("<cmnd>") ; return
    if not cmnd in event.chan.data.allowcommands: event.chan.data.allowcommands.append(cmnd) ; event.chan.save() ; event.done()

cmnds.add("chan-allowcommand", handle_chanallowcommand, ["OPER", ])
examples.add("chan-allowcommand", "add a command to the allow list. allows for all users.", "chan-allowcommand learn")

## chan-silentcommand command

def handle_chansilentcommand(bot, event):
    """ arguments: <cmnd> - silence a command in the channel. /msg the result of a command."""
    try: cmnd = event.args[0] 
    except (IndexError, KeyError): event.missing("<cmnd>") ; return
    if not cmnd in event.chan.data.silentcommands: event.chan.data.silentcommands.append(cmnd) ; event.chan.save() ; event.done()

cmnds.add("chan-silentcommand", handle_chansilentcommand, ["OPER", ])
examples.add("chan-silentcommand", "add a command to the allow list.", "chan-silentcommand learn")

## chan-loudcommand command

def handle_chanloudcommand(bot, event):
    """ arguments: <cmnd> - allow output of a command in the channel. """
    try: cmnd = event.args[0] ; event.chan.data.silentcommands.remove(cmnd) ; event.chan.save() ; event.done()
    except (IndexError, ValueError): event.reply("%s is not in the silencelist" % event.rest)

cmnds.add("chan-loudcommand", handle_chanloudcommand, ["OPER", ])
examples.add("chan-loudcommand", "remove a command from the silence list.", "chan-loudcommand learn")

## chan-removecommand command 

def handle_chanremovecommand(bot, event):
    """ remove a command from the allowed list of a channel. """
    try: cmnd = event.args[0] ; event.chan.data.allowcommands.remove(cmnd) ; event.chan.save() ; event.done()
    except (IndexError, ValueError): event.reply("%s is not in the whitelist" % event.rest)

cmnds.add("chan-removecommand", handle_chanremovecommand, ["OPER", ])
examples.add("chan-removecommand", "remove a command from the allow list.", "chan-removecommand learn")

## chan-upgrade command

def handle_chanupgrade(bot, event):
    """ no arguments - upgrade the channel. """
    prevchan = event.channel
    # 0.4.1
    if prevchan.startswith("-"): prevchan[0] = "+"
    prevchan = prevchan.replace("@", "+")
    prev = Persist(getdatadir() + os.sep + "channels" + os.sep + prevchan)
    if prev.data: event.chan.data.update(prev.data) ; event.chan.save() ; event.reply("done")
    else: 
        prevchan = event.channel
        prevchan = prevchan.replace("-", "#")
        prevchan = prevchan.replace("+", "@")
        prev = Persist(getdatadir() + os.sep + "channels" + os.sep + prevchan)
        if prev.data: event.chan.data.update(prev.data) ; event.chan.save() ; event.reply("done")
        else: event.reply("can't find previous channel data")

cmnds.add("chan-upgrade", handle_chanupgrade, ["OPER", ])
examples.add("chan-upgrade", "upgrade the channel.", "chan-upgrade")

## chan-allowwatch command

def handle_chanallowwatch(bot, event):
    """ arguments: <JID/channel> - add a target channel to the allowwatch list. """
    if not event.rest: event.missing("<JID/channel>") ; return
    if event.rest not in event.chan.data.allowwatch: event.chan.data.allowwatch.append(event.rest) ; event.chan.save()
    event.done()

cmnds.add("chan-allowwatch", handle_chanallowwatch, "OPER")
examples.add("chan-allowwatch", "allow channel events to be watch when forwarded", "chan-allowwatch feedbackloop@gmail.com")

## chan-delwatch command

def handle_chandelwatch(bot, event):
    """ add a target channel to the allowout list. """
    if not event.rest: event.missing("<JID>") ; return
    try: event.chan.data.allowwatch.remove(event.rest) ; event.chan.save()
    except: event.reply("%s is not in the allowout list" % event.rest) ; return
    event.done()

cmnds.add("chan-delwatch", handle_chandelwatch, "OPER")
examples.add("chan-delwatch", "deny channel events to be watched when forwarded", "chan-delwatch feedbackloop@gmail.com")

## chan-enable command

def handle_chanenable(bot, event):
    """ no arguments - enable current channel. """
    event.chan.data.enable = True
    event.chan.save()
    event.reply("%s channel enabled" % event.channel)

cmnds.add("chan-enable", handle_chanenable, ["OPER", "USER"])
examples.add("chan-enable", "enable a channel (allow for handling of events concerning this channel (convore for now)", "chan-enable")

## chan-disable command

def handle_chandisable(bot, event):
    """ no arguments - enable current channel. """
    event.chan.data.enable = False
    event.chan.save()
    event.reply("%s channel disabled" % event.channel)

cmnds.add("chan-disable", handle_chandisable, ["OPER", "USER"])
examples.add("chan-disable", "disable a channel (disallow for handling of events concerning this channel (convore for now)", "chan-disable")

## chan-config

def handle_chanconfig(bot, event):
    if len(event.args) != 2: event.missing("<item> <value>") ; return
    event.chan.data[event.args[0]] = event.args[1]
    event.chan.save()
    event.done()

cmnds.add("chan-config", handle_chanconfig, "OPER")
examples.add("chan-config", "set simple <item> <value> pairs on the channeldata", "chan-config twittername tl")

def handle_chandelconfig(bot, event):
    if len(event.args) != 1: event.missing("<item>") ; return
    try: del event.chan.data[event.args[0]]
    except Exception as ex: event.reply("error: %s" % str(ex)) ; return
    event.chan.save()
    event.done()

cmnds.add("chan-delconfig", handle_chandelconfig, "OPER")
examples.add("chan-delconfig", "delete <item> <value> pairs from the channeldata", "chan-delconfig twittername")
