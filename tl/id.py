# tl/id.py
#
#

""" uid helper functions. """

## basic imports

import logging
import getpass
import os

## defines

user = None
host = None

## get_id function

def get_id():
    from tl.lib.datadir import getdatadirstr
    from tl.utils.resolve import resolve_host
    global user
    if not user: user = getpass.getuser()
    global host
    if not host: host = resolve_host()
    dstr = getdatadirstr()
    if dstr.startswith("/"): dstr = dstr[1:]
    return "%s@%s/%s" % (user, host, dstr)

## get_bid function

def get_bid(bot):
    id = get_id()
    if not bot.cfg.id in id: id = get_id() + "-" + bot.cfg.cid
    return id

## get_uid function

def get_uid(username):
    """ make a uid (userid) based on username). """
    from tl.lib.users import getusers
    if not username: username = getusers().get(username)
    uid = get_id()
    if not username in uid: uid = username + "!" + uid
    logging.info("uid is %s" % uid)
    return uid

## get_eid function

def get_eid(event):
    """ make a event id. """
    from tl.id import get_uid
    eid = event.bot.cfg.name + get_uid(event.userhost) + "-" + event.uuid
    logging.info("eid is %s" % eid)
    return eid

## get_pid function

def get_pid(obj):
    """ make a persistent object id. """
    from tl.lib.datadir import getdatadir
    pid = get_id() + os.sep + getdatadir() + os.sep + obj.logname
    logging.info("pid is %s" % pid)
    return pid

## get_cid function

def get_cid(cfg):
    """ make a config file id. """
    from tl.lib.datadir import getdatadir
    cid = get_id() + os.sep + getdatadir() + os.sep + cfg.filename
    logging.info("cid is %s" % cid)
    return cid