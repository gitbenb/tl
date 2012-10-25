# tl/plugs/socket/fisheye.py
#
#

""" fisheye plugin. """

## tl imports

from tl.utils.exception import handle_exception
from tl.lib.callbacks import callbacks
from tl.lib.commands import cmnds
from tl.lib.persist import PlugPersist
from tl.lib.examples import examples
from tl.plugs.extra.tinyurl import get_tinyurl

## basic imports

import logging
import xmlrpc.client
import re

## defines

rpc_clients = {}

gitHashRule = re.compile(r'.*\b([0-9a-f]{7,40})\b.*')

cfg = PlugPersist('fisheye', {})

## getRpcClient function

def getRpcClient(project):
    if project["name"] not in rpc_clients:
        base_url = "%s/api/xmlrpc" % project["url"]
        server = xmlrpc.client.ServerProxy(base_url)
        auth = server.login(project["username"], project["password"])
        logging.info("Created new RPC client for %s with auth token: %s" % (project["name"], auth))
        rpc_clients[project["name"]] = (server, auth)

    return rpc_clients[project["name"]]

def containsHash(bot, ievent):
    if ievent.how == "backgound": return 0
    if ievent.channel in cfg.data and len(cfg.data[ievent.channel]):
        if gitHashRule.match(ievent.txt): return 1
    return 0

def doLookup(bot, ievent):
    logging.info("Doing lookup for fisheye changeset")
    fnd = gitHashRule.match(ievent.txt)
    for pname in cfg.data[ievent.channel]:
        project = cfg.data["projects"][pname]
        try:
            server, auth = getRpcClient(project)
            res = server.getChangeset(auth, pname, fnd.group(1))
            logging.info('response from fisheye: %s' % res)
            cs_url = "%s/changelog/%s?cs=%s" % (project["url"], pname, res["csid"])
            bot.say(ievent.channel, "%s- %s by %s: %s %s" % (pname, res["csid"][:7], res["author"], res["log"].strip()[:60], get_tinyurl(cs_url)[0]))
            return
        except:
            print("Couldn't find %s" % fnd.group(1))

callbacks.add('PRIVMSG', doLookup, containsHash, threaded=True)
callbacks.add('CONSOLE', doLookup, containsHash, threaded=True)
callbacks.add('MESSAGE', doLookup, containsHash, threaded=True)
callbacks.add('DISPATCH', doLookup, containsHash, threaded=True)
callbacks.add('TORNADO', doLookup, containsHash, threaded=True)

## add_fisheye_project command

def handle_add_fisheye_project(bot, ievent):
    """ configure a new fisheye project; syntax: add_fisheye_project [project name] [url] [username] [password] """
    if len(ievent.args) != 4:
        ievent.reply("syntax: add_fisheye_project [project name] [url] [username] [password]")
        return

    project = {
        "name": ievent.args[0],
        "url": ievent.args[1].strip("/"),
        "username": ievent.args[2],
        "password": ievent.args[3],
    }

    if "projects" not in cfg.data:
        cfg.data["projects"] = {}
    cfg.data["projects"][project["name"]] = project
    cfg.save()

    ievent.reply("Added fisheye project %s" % project["name"])
cmnds.add("add_fisheye_project", handle_add_fisheye_project, ["OPER"])
examples.add("add_fisheye_project", "add a fisheye project", "add_fisheye_project FireBreath http://code.firebreath.org myuser mypassword")

## fisheye_commit_lookup_enable command

def handle_fisheye_commit_lookup_enable(bot, ievent):
    """ enable fisheye commit lookups in a channel. """
    if len(ievent.args) != 1:
        ievent.reply("syntax: fisheye_commit_lookup_enable project (e.g. firebreath")
        return
    if ievent.channel not in cfg.data:
        cfg.data[ievent.channel] = []
    project = ievent.args[0]

    if "projects" not in cfg.data or project not in cfg.data["projects"]:
        ievent.reply("Unknown fisheye project %s" % project)
        return

    cfg.data[ievent.channel].append(project)
    cfg.save()
    ievent.reply("fisheye lookups enabled for %s" % project)
cmnds.add("fisheye_commit_lookup_enable", handle_fisheye_commit_lookup_enable, ['OPER'])
examples.add("fisheye_commit_lookup_enable", "enable fisheye commit lookups in the channel", "fisheye_commit_lookup_enable")

## fisheye_commit_lookup_disable command

def handle_fisheye_commit_lookup_disable(bot, ievent):
    """ no arguments - disable fisheye commit lookups in a channel. """
    cfg.data[ievent.channel] = []
    cfg.save()
    ievent.reply("fisheye lookups disabled")
cmnds.add("fisheye_commit_lookup_disable", handle_fisheye_commit_lookup_disable, ['OPER'])
examples.add("fisheye_commit_lookup_disable", "disable fisheye commit lookups in the channel", "fisheye_commit_lookup_disable")

