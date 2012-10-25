# tl/utils/opts.py
#
#

""" options related functions. """

## tl imports

from tl.lib.errors import NameNotSet, NoUserProvided, NoOwnerSet, NoOptsSet
from tl.version import version
from tl.utils.name import stripname
from tl.lib.errors import NoOptsSet, NoUsers
from tl.utils.log import setloglevel, getloglevel
from tl.lib.datadir import setdatadir, getdatadir
from tl.lib.users import users_boot
from tl.id import get_uid, get_id

from .lazydict import LazyDict

import tl
import tl.utils
import tl.utils.url
import tl.utils.log

## basic imports

import os
import uuid
import logging
import optparse
import pprint
import sys
import getpass


## defines

curopts = None

## setopts function

def setopts(opts):
    """ set curopts commandline options. """
    global curopts
    curopts = opts
    logging.info("curopts set to %s" % str(curopts))

## getops function

def getopts():
    """ get curopts commandline options. """
    global curopts
    return curopts

## EventOptionParser class

class EventOptionParser(optparse.OptionParser):

     def exit(self):
         pass

     def error(self):
         pass

## globals

# global opts list

globaloptslist = [
                ('', '--fleet', "store_true", False, 'fleet', "start the fleet"),
                ('', '--popen', "store_true", False, 'allowpopen', "allow plugins that use os.popen (spawn a new shell) - DANGER !!")
           ]

## makeopts function

core_opts = [
                ('', '--nourl', "store_true", False, 'nourl', "disable geturl functionality"),
                ('', '--nocolors', 'store_true', False, 'nocolors',  "enable the use of colors"),
                ('', '--save', 'store_true', False, 'save',  "save to config file"),
                ('-o', '--owner', 'string', "", 'owner',  "owner of the bot"),
                ('-b', '--bork', "store_true", False, 'bork', "quit the bot on exception"),
                ('-d', '--datadir', 'string', "", 'datadir',  "datadir of the bot"),
                ('-l', '--loglevel', 'string', "", 'loglevel',  "loglevel of the bot"),
                ('', '--exceptions', "store_true", False, 'exceptions', "show exceptions when terminating the bot"),
                ('', '--popen', "store_true", False, 'allowpopen', "allow plugins that use os.popen (spawn a new shell) - DANGER !!"),
                ('', '--fleet', "store_true", False, 'fleet', "start the fleet"),
                ('-c', '--channel', 'string', "", 'channel',  "channel to join")
            ]

bot_opts = [
                ('-r', '--resume', 'string', "", 'doresume', "resume the bot from the folder specified"),
                ('-e', '--enable', 'store_true', False, 'enable', "enable bot for fleet use"),
                ('-s', '--server', 'string', "", 'server',  "server to connect to (irc)"),
                ('-c', '--channel', 'string', "", 'channel',  "channel to join"),
                ('-p', '--password', 'string', "", 'password', "set password used to connect to the server"),
                ('', '--name', 'string', "", 'name', "bot's name"),
                ('', '--port', 'string', "", 'port',  "set port of server to connect to"),
                ('-n', '--nick', 'string', "", 'nick',  "nick of the bot"),
           ]

api_opts = [

                ('-a', '--api', 'store_true', False, 'api',  "enable api server"),
                ('', '--apiport', 'string', "", 'apiport', "port on which the api server will run"),
           ]

irc_opts = [
               ('', '--ssl', 'store_true', False, 'ssl',  "use ssl"),
               ('-y', '--nossl', 'store_true', False, 'nossl',  "don't use ssl"),
               ('-6', '--ipv6', 'store_true', False, 'ipv6', "enable ipv6 bot"),
               ('-u', '--username', "string", False, 'username', "user to auth to server with")
           ]

xmpp_opts = [
                ('-u', '--user', 'string', False, 'user',  "JID of the bot")
            ]

fleet_opts = [
               ('', '--all', 'store_true', False, 'all', "show available fleet bots")
           ]

console_opts = [
                ('', '--name', 'string', "", 'name', "bot's name"),
               ]

## opts_add function

def opts_add(parser, opts):
    """ add options from a list to the parser. """
    for option in opts:
        type, default, dest, help = option[2:]
        if "store" in type:
            try: parser.add_option(option[0], option[1], action=type, default=default, dest=dest, help=help)
            except Exception as ex: logging.error("error: %s - option: %s" % (str(ex), option)) ; continue 
        else:
            try: parser.add_option(option[0], option[1], type=type, default=default, dest=dest, help=help)
            except Exception as ex: logging.error("error: %s - option: %s" % (str(ex), option)) ; continue 

## make_opts function

def make_opts(args, optslist=[], parser=None):
    """ bind a optionslist into the parser and parse txt to options. """
    parser = parser or optparse.OptionParser(usage='usage: %prog [options]', version=version)
    opts_add(parser, core_opts)
    if optslist: opts_add(parser, optslist)
    if args: opts, args = parser.parse_args(args[1:])
    else: opts, args = parser.parse_args()
    for option in globaloptslist:
        type, default, dest, help = option[2:]
        try:
            opts[dest] =  default
        except TypeError: continue
    opts.args = args
    for option in optslist:
        type, default, dest, help = option[2:]
        try:
            opts[dest] =  default
        except TypeError: continue
    opts.args = args
    global curopts
    curopts = opts
    return opts

## do_opts function

def do_opts(type="console", args=[], *argslist, **kwargs):
    from tl.version import getversion
    if not args: args = sys.argv
    if type != "console": print(getversion(type.upper()))
    cfg = None
    if type == "irc": target = api_opts + bot_opts + irc_opts
    elif type in ["xmpp", "sxmpp", "sleek"]: target = api_opts + bot_opts + xmpp_opts
    elif type == "fleet": target = api_opts + fleet_opts
    elif type == "init": target = []
    elif type == "console": target = console_opts
    else: target = []
    opts =  make_opts(args, target, *argslist, **kwargs)
    if type == "console": ll = "error"
    else: ll = "warn" 
    setloglevel(opts.loglevel or ll)
    if opts.datadir: setdatadir(opts.datadir) #; logging.warn("datadir set to %s" % getdatadir())
    if opts.bork: tl.utils.exception.bork = True ; logging.warn("bork mode enabled")
    if opts.nourl: tl.utils.url.enabled = False ; logging.warn("url fetching disabled")
    if opts.nocolors: tl.utils.log.docolor = False ; logging.warn("colors in logging is disabled")
    if opts.owner:
        from tl.lib.users import getusers
        u = getusers()
        if u: u.make_owner(opts.owner)
        else: raise NoUsers()
    from tl.lib.config import getmainconfig
    maincfg = getmainconfig(opts.datadir)
    if type == "irc": cfg = makeircconfig(opts, opts.name)
    elif type == "xmpp" or type == "sleek": cfg = makexmppconfig(opts, opts.name)
    elif type == "console": cfg = makeconsoleconfig(opts, opts.name)
    else: cfg = makedefaultconfig(opts, opts.name) 
    if maincfg.dbtype: logging.warn("database type is %s" % maincfg.dbtype)
    return (opts, cfg)

## makeeventopts function

def makeeventopts(txt):
    """ create option parser for events. """
    parser = EventOptionParser()
    parser.add_option('', '--chan', type='string', default=False, dest='channel', help="target channel")
    parser.add_option('-c', '--chan-default', action='store_true', default=False, dest='dochan',  help="use the channel command is given in")
    parser.add_option('-a', '--all', action='store_true', default=False, dest='all',  help="use all results of the command")
    parser.add_option('-s', '--silent', action='store_true', default=False, dest='silent',  help="give bot response in /pm")
    try: opts, args = parser.parse_args(txt.split())
    except Exception as ex: logging.warn("opts - can't parse %s" % txt) ; return
    opts.args = args
    return opts

## makedefaultconfig function

def makedefaultconfig(opts, name):
    from tl.lib.config import Config
    cfg = Config('defaults' + os.sep + name + os.sep + 'config')
    cfg.type = "default"
    cfg.name = name
    if not cfg.owner: cfg.owner = []
    from tl.utils.uid import get_uid
    cfg.userid = userid = get_uid()
    if userid not in cfg.owner: cfg.owner.append(userid) ; cfg.save()
    if opts and opts.loglevel: cfg.loglevel = opts.loglevel
    else: cfg.loglevel = cfg.loglevel or "error"
    return cfg


## makeconsoleconfig function

def makeconsoleconfig(opts=None, botname=None):
    """ make config file based on options. """
    if not botname: botname = opts.name or "default-console" 
    botname = stripname(botname)
    from tl.lib.config import Config
    cfg = Config('fleet' + os.sep + botname + os.sep + 'config')
    cfg.type = "console"
    cfg.name = botname
    if not cfg.owner: cfg.owner = []
    userid = get_id()
    cfg.userid = userid
    if userid not in cfg.owner: cfg.owner.append(userid) ; cfg.save()
    if opts and opts.loglevel: cfg.loglevel = opts.loglevel
    else: cfg.loglevel = cfg.loglevel or "error"
    return cfg

## makeircconfig function

def makeircconfig(opts=None, botname=None):
    """ make config file based on options. """
    if not opts: botname = botname or "default-irc"
    else:
        if not botname: botname = opts.name or "default-irc"
    origname = botname
    botname = stripname(botname)
    logging.warn("botname is %s (%s)" % (origname, botname)) 
    from tl.lib.config import Config
    cfg = Config('fleet' + os.sep + botname + os.sep + 'config')
    cfg.type = 'irc'
    cfg.name = botname
    if not opts:
        cfg.password = cfg.password or ""
        cfg.ssl = cfg.ssl or False
        cfg.port = cfg.port or 6667
        cfg.server = cfg.server or "localhost"
        cfg.owner = cfg.owner or []
        cfg.ipv6 = cfg.ipv6 or False
        cfg.nick = cfg.nick or "tl"
        cfg.channels = []
        return cfg          
    if not cfg.channels: cfg.channels = []
    if not cfg.disable: cfg.disable = False
    if opts.enable: cfg.disable = False ; logging.warn("enabling %s bot in %s" % (botname, cfg.cfile))
    if opts.password: cfg.password = opts.password
    if opts.ipv6: cfg.ipv6 = True
    else: cfg.ipv6 = cfg.ipv6 or False
    if opts.ssl: cfg.ssl = True
    else: cfg.ssl = cfg.ssl or False
    if opts.nossl: cfg.ssl = False
    if opts.port: cfg.port = opts.port or cfg.port or 6667
    else: cfg.port = cfg.port or 6667
    if opts.server: cfg.server = opts.server
    else: cfg.server = cfg.server or "localhost"
    if not cfg.owner: cfg.owner = []
    if opts.owner and opts.owner not in cfg.owner: cfg.owner.append(opts.owner)
    if opts.ipv6: cfg.ipv6 = opts.ipv6
    if opts.nick: cfg.nick = opts.nick
    else: cfg.nick = cfg.nick or "tl"
    if opts.username: cfg.username = opts.username
    else: cfg.username = cfg.username or "tl"
    if opts.channel:
        if not opts.channel in cfg.channels: cfg.channels.append(opts.channel)
    else: cfg.channels = cfg.channels or []
    return cfg

## makexmppconfig function

def makexmppconfig(opts=None, botname=None, type="sleek"):
    """ make config file based on options. """
    if not opts: botname = botname or "default-%s" % type
    else:
        if not botname: botname = opts.name or "default-%s" % type
    botname = stripname(botname)
    from tl.lib.config import Config, makedefaultconfig
    cfg = Config('fleet' + os.sep + botname + os.sep + 'config')
    cfg.type = type
    cfg.name = botname
    dosave = False
    if not opts:
        cfg.user = cfg.user or ""
        cfg.host = cfg.host or ""
        cfg.password =  cfg.password or ""
        cfg.server = cfg.server or ""
        cfg.owner = cfg.owner or []
        cfg.loglevel = cfg.lowlevel or "warn" 
        cfg.nick = cfg.nick or "tl"
        cfg.channels = []
        cfg.openfire = False
        return cfg        
    if not cfg.disable: cfg.disable = False
    if opts.enable: cfg.disable = 0 ; logging.warn("enabling %s bot in %s" % (botname, cfg.cfile))
    if not cfg.channels: cfg.channels = []
    if opts.user: cfg.user = opts.user ; dosave = True
    if not cfg.user: raise NoUserProvided("try giving the -u option to the bot (and maybe -p as well) or run tl-init and edit %s" % cfg.cfile)
    if opts.user:
        try: cfg.host = opts.user.split('@')[1]
        except (IndexError, ValueError): print("user is not in the nick@server format")
    if not cfg.host:
        try: cfg.host = cfg.user.split('@')[1]
        except (IndexError, ValueError): print("user is not in the nick@server format")
    if opts.password: cfg.password = opts.password
    if opts.server: cfg.server = opts.server
    else: cfg.server = cfg.server or ""
    if opts.name: cfg.jid = opts.name
    if not cfg.owner: cfg.owner = []
    if opts.owner and opts.owner not in cfg.owner: cfg.owner.append(opts.owner) ; dosave = True
    if not cfg.owner: raise NoOwnerSet("try using the -o option or run tl-init and edit %s" % cfg.cfile)
    if opts.nick: cfg.nick = opts.nick
    else: cfg.nick = cfg.nick or "tl"
    if opts.channel:
        if not opts.channel in cfg.channels: cfg.channels.append(opts.channel) ; dosave = True
    else: cfg.channels = cfg.channels or []
    if dosave: cfg.save()
    return cfg

