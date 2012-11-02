# tl/id.py
#
#

""" uid helper functions. """

## tl imports

from tl.utils.name import stripname
from tl.utils.path import normdir
from tl.lib.errors import NoSuchUser

## basic imports

import logging
import getpass
import os
import time

## defines

logignore = ["TICK", "TICK10", "TICK60"]

user = None
host = None

## get_id function

def get_hid():
    """ return a host id. """
    from tl.lib.datadir import getdatadirstr
    from tl.utils.resolve import resolve_host
    global host
    if not host: host = resolve_host()
    return host

## get_did function

def get_did():
    """ return a datadir id. """
    dstr = getdatadirstr()
    if dstr.startswith("/"): dstr = dstr[1:]
    return normdir(dstr)

## get_id function

def get_id():
    """ return a datadir id. """
    return get_did()

## get_urlid function

def get_urlid(port=None):
    return "http://%s@%s:%s/%s" % (shelluser, get_hid(), port or 10102, get_did())

## get_bid function

def get_bid(bot):
    bid = "/bots/%s" % bot.cfg.name
    bid = normdir(bid)
    logging.warn("bid is %s" % bid)
    return bid

## get_uid function

def get_uid(target=None):
    """ make a uid (userid) based on username). """
    if not target: target = "/console/" + getpass.getuser()
    from tl.lib.users import getusers
    user = getusers().byname(target)
    if not user: user = getusers().getuser(target)
    if not user: raise NoSuchUser(target)
    name = user.data.name
    uid = "/users/" + name
    uid = normdir(uid)
    logging.warn("uid is %s" % uid)
    return uid

## get_eid function

def get_eid(event):
    """ make a event id. """
    logging.warn(event.tojson())
    eid = "/events/%s-%s-%s" % (event.ctime, event.token, event.cbtype) 
    eid = normdir(eid)
    if event.nobind: logging.debug("eid is %s" % eid) 
    else: logging.warn("eid is %s" % eid)
    return eid

## get_teid function

def get_tlid(event):
    """ make a timed event id. """
    from tl.lib.users import getusers
    user = getusers().byname(target)
    if not target: user = getusers().getuser(target)
    if not user: raise NoSuchUser(userhost)
    tlid = "/timeline/%s-%s-%s" % (event.ctime, event.token, stripname(user.data.name)) 
    tlid = normdir(tlid)
    logging.warn("tlid is %s" % tlid)
    return tlid

## get_pid function

def get_pid(obj):
    """ make a persistent object id. """
    pid = "/persist/%s" % obj.logname
    pid = normdir(pid) 
    logging.warn("pid is %s" % pid)
    return pid

## get_cid function

def get_cid(cfg):
    """ make a config file id. """
    cid = "/config/" + cfg.cfgname
    cid = normdir(cid)
    logging.warn("cid is %s" % cid)
    return cid
