# tl/utils/twitter.py
#
#

""" twitter related helper functions .. uses tweepy. """

## tl imports

from tl.utils.exception import handle_exception
from tl.utils.pdol import Pdol
from tl.utils.textutils import html_unescape
from tl.utils.generic import waitforqueue, strippedtxt, splittxt
from tl.lib.persist import PlugPersist
from tl.lib.datadir import getdatadir
from tl.lib.tlimport import import_byfile
from tl.lib.persist import Persist
from tl.utils.tinyurl import parseurl, get_tinyurl
from tl.utils.creds import getcredsmod
from tl.lib.errors import RequireError

## tweepy imports

from tl.imports import gettweepy
tweepy = gettweepy()
import tweepy.oauth
import tweepy.auth

## basic imports

import logging 
import os
import urllib.request, urllib.error, urllib.parse
import types

## defines

go = False
auth = None
users = None

## twitterapi function

def twitterapi(CONSUMER_KEY, CONSUMER_SECRET, token=None, force=False, *args, **kwargs):
    """ return twitter API object - with or without access token. """
    global auth
    if not auth: auth = tweepy.auth.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    if token: auth.set_access_token(token.key, token.secret)
    tweetapi = tweepy.API(auth, *args, **kwargs) 
    if not tweetapi: raise Exception("no api returned - %s" % str(auth))
    logging.debug("twitter api returned: %s" % str(tweetapi))
    return tweetapi

## twittertoken function

def twittertoken(CONSUMER_KEY, CONSUMER_SECRET, twitteruser, username):
    """ get access token from stored token string. """
    token = twitteruser.get(username)
    if not token: raise Exception("no token found for %s" % username)
    return tweepy.oauth.OAuthToken(CONSUMER_KEY, CONSUMER_SECRET).from_string(token)

def getcreds(datadir=None):
    if not datadir: datadir = getdatadir()
    mod = getcredsmod(datadir)
    if not mod: raise RequireError("credentials.py is needed in %s/config dir. see %s/examples" % (datadir, datadir))
    return mod.CONSUMER_KEY, mod.CONSUMER_SECRET

def getauth(datadir=None):
    """ get auth structure from datadir. """
    global auth
    if auth: return auth
    if not datadir: datadir = getdatadir()    
    try: key, secret = getcreds(datadir)
    except RequireError as ex: logging.warn(str(ex)) ; return None
    auth = tweepy.OAuthHandler(key, secret)
    return auth

## TwitterUsers class

class TwitterUsers(Persist):

    """ manage users tokens. """

    def add(self, user, token):
        """ add a user with his token. """
        user = user.strip().lower()
        self.data[user] = token
        self.save()

    def get(self, username):
        try: return self.data[username]
        except KeyError: return

    def remove(self, user):
        """ remove a user. """
        user = user.strip().lower()
        if user in self.data:
            del self.data[user]
            self.save()

    def users(self):
        return self.data.keys()

    def size(self):
        """ return size of twitter users. """
        return len(self.data)

    def __contains__(self, user):
        """ check if user exists. """
        user = user.strip().lower()
        return user in self.data

def get_users():
    global users
    if users: return users
    users = TwitterUsers(getdatadir() + os.sep + "twitter" + os.sep + "users")
    return users

def get_token(username):
    global users
    if not users: users = TwitterUsers(getdatadir() + os.sep + "twitter" + os.sep + "users")
    if not users: raise Exception("can't get twitter users object") ; return
    key, secret = getcreds(getdatadir())
    if not key: raise Exception(getdatadir())
    if not secret: raise Exception(getdatadir())
    token = twittertoken(key, secret, users, username)
    if not token: raise Exception("%s %s" % (str(user), username))
    api = twitterapi(key, secret, token)
    if not api: raise Exception("%s %s" % (str(user), name))
    return (token, api)

def twitter_out(username, txt, event=None):
    """ post a message on twitter. """
    if event and event.chan:
        taglist = event.chan.data.taglist
        if taglist:
           for tag in taglist:
               txt += " %s" % tag
    url = parseurl(txt)
    if url:
        tiny = get_tinyurl(url)
        if tiny:
            tinyurl = tiny[0]  
            if tinyurl: txt = txt.replace(url, tinyurl)
    if len(txt) > 140: logging.error("size of twitter message > 140 chars: %s" % txt) ; return
    token, api = get_token(username)
    if token and api:
        status = api.update_status(txt)
        logging.warn("posted 1 tweet (%s chars) for %s" % (len(txt), username))
    else: logging.error("no token or API available")
    return status
