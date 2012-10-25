# tl/reboot.py
#
#

""" reboot code. """

## tl imports

from tl.lib.fleet import getfleet
from tl.imports import getjson
json = getjson()

## basic imports

import os
import sys
import pickle
import tempfile
import logging
import time

## reboot function

def reboot():
    """ reboot the bot. """
    logging.warn("reboot - rebooting")
    os.execl(sys.argv[0], *sys.argv)

## reboot_stateful function

def reboot_stateful(bot, ievent, fleet, partyline):
    """ reboot the bot, but keep the connections (IRC only). """
    logging.warn("reboot - doing statefull reboot")
    session = {'bots': {}, 'name': bot.cfg.name, 'channel': ievent.channel, 'partyline': []}
    fleet = getfleet()
    for i in fleet.bots:
        logging.warn("reboot - updating %s" % i.cfg.name)
        data = i._resumedata()
        if not data: continue
        session['bots'].update(data)
        if i.type == "sxmpp": i.exit() ; continue
        if i.type == "convore": i.exit() ; continue
        if i.type == "tornado":
            i.exit()
            time.sleep(0.1)
            for socketlist in list(i.websockets.values()):
                for sock in socketlist: sock.stream.close()
    session['partyline'] = partyline._resumedata()
    sfile, sessionfile = tempfile.mkstemp('-session', 'tl-', text=True)
    logging.warn("writing session file %s" % sessionfile)
    json.dump(session, open(sessionfile, "w"))
    args = []
    skip = False
    for a in sys.argv[1:]:
        if skip: skip = False ; continue
        if a == "-r": skip = True ; continue
        args.append(a)
    os.execl(sys.argv[0], sys.argv[0], '-r', sessionfile, *args)
