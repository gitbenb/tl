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

def get_id():
    from tl.lib.datadir import getdatadirstr
    from tl.utils.resolve import resolve_host
    global host
    if not host: host = resolve_host()
    dstr = getdatadirstr()
    if dstr.startswith("/"): dstr = dstr[1:]
    return "%s/%s" % (host, normdir(dstr))

## get_bid function

def get_bid(bot):
    bid = get_id() + "-" + bot.cfg.name
    return bid

## get_uid function

def get_uid(target=None):
    """ make a uid (userid) based on username). """
    if target:
        from tl.lib.users import getusers
        user = getusers().byname(target)
        if not target: user = getusers().getuser(target)
        if not user: raise NoSuchUser(userhost)
        name = user.data.name
    else: name = "console/" + getpass.getuser()
    uid = get_id() + "/users/" + name
    logging.warn("uid is %s" % uid)
    return uid

## get_eid function

def get_eid(event):
    """ make a event id. """
    from tl.id import get_id
    logging.warn(event.tojson())
    eid = get_id() + "/events/%s-%s-%s" % (event.ctime, event.token, event.cbtype) 
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
    tlid = get_id() + "/timeline/%s-%s-%s" % (stripname(user.data.name), event.ctime, event.token) 
    logging.warn("tlid is %s" % tlid)
    return tlid

## get_pid function

def get_pid(obj):
    """ make a persistent object id. """
    pid = get_id() + "/persist/%s-%s" % (obj.data.ctime, obj.data.uuid) 
    logging.warn("pid is %s" % pid)
    return pid

## get_cid function

def get_cid(cfg):
    """ make a config file id. """
    cid = get_id() + "/config/" + cfg.cfgname
    logging.warn("cid is %s" % cid)
    return cid
