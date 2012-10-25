# tl/plugs/extra/twitter.py
#
#

""" a twitter plugin for the TIMELINE, currently post only .. uses tweepy oauth. """

## tl imports

from tl.utils.exception import handle_exception
from tl.lib.commands import cmnds
from tl.lib.callbacks import callbacks, first_callbacks, last_callbacks
from tl.lib.examples import examples
from tl.utils.pdol import Pdol
from tl.utils.textutils import html_unescape
from tl.utils.generic import waitforqueue, strippedtxt, splittxt
from tl.lib.persist import PlugPersist
from tl.utils.twitter import twitter_out, get_token, get_users, twitterapi, twittertoken, getcreds, getauth
from tl.lib.datadir import getdatadir

## tweppy imports

from tl.contrib import tweepy

## basic imports

import os
import urllib.request, urllib.error, urllib.parse
import types
import logging

## load on start

def twitterstart(bot, event): pass

callbacks.add("START", twitterstart)

## twitter callbacks

def twitterpre(bot, event):
    try:
         twittername = event.chan.data.twittername
         if twittername: return True
    except Exception as ex: pass
    return False
    
def twittercb(bot, event):
    event.dontbind = False
    event.bind(force=True)
    try: twittername = event.chan.data.twittername
    except Exception as ex: handle_exception() ; twittername = None
    try: username = event.origin ; logging.info("using origin %s" % event.origin)
    except Exception as ex: handle_exception() ; username = None
    if twittername:
        try: twitter_out(twittername or username or "tl", event.txt, event)
        except Exception as ex: logging.warn("error posting to twitter: %s" % str(ex))

last_callbacks.add("RSS", twittercb, twitterpre)

## twitter command

def handle_twitter(bot, ievent):
    """ arguments: <txt> - send a twitter message. """
    go = getauth()
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the .tl/config dir. see the examples directory") ; return
    txt = ievent.rest
    if ievent.ispipelined:
        txt = ievent.wait()
    if not txt: ievent.missing('<txt>') ; return
    else:
        if ievent.chan:
            taglist = ievent.chan.data.taglist
            if taglist:
                for tag in taglist:
                   txt += " %s" % tag
        twitter_out(ievent.user.data.name, txt, ievent) ; ievent.reply("tweet posted")
 
cmnds.add('twitter', handle_twitter, ['USER', 'GUEST'])
examples.add('twitter', 'posts a message on twitter', 'twitter just found the http://jsonbot.org project')

## twitter-cmnd command

def handle_twittercmnd(bot, ievent):
    """ arguments: <API cmnd> - do a twitter API cmommand. """
    go = getauth()
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the .tl/config dir. see the examples dir") ; return
    if not ievent.args: ievent.missing('<API cmnd>') ; return
    target =  strippedtxt(ievent.args[0])
    try:
        from tl.utils.twitter import get_token
        token = get_token(ievent.user.data.name)
        if not token: ievent.reply("you are not logged in yet .. run the twitter-auth command.") ; return 
        key, secret = getcreds(getdatadir())
        token = tweepy.oauth.OAuthToken(key, secret).from_string(token)
        twitter = twitterapi(key, secret, token)
        cmndlist = dir(twitter)
        cmnds = []
        for cmnd in cmndlist:
            if cmnd.startswith("_") or cmnd == "auth": continue
            else: cmnds.append(cmnd)
        if target not in cmnds: ievent.reply("choose one of: %s" % ", ".join(cmnds)) ; return
        try: method = getattr(twitter, target)
        except AttributeError: ievent.reply("choose one of: %s" % ", ".join(cmnds)) ; return
        result = method()
        res = []
        for item in result:
            try: res.append("%s - %s" % (item.screen_name, item.text))
            except AttributeError:
                try: res.append("%s - %s" % (item.screen_name, item.description))
                except AttributeError:
                    try: res.append(str(item.__getstate__()))
                    except AttributeError: res.append(dir(i)) ; res.append(str(item))
        ievent.reply("result of %s: " % target, res) 
    except KeyError: ievent.reply('you are not logged in yet. see the twitter-auth command.')
    except (tweepy.TweepError, urllib.error.HTTPError) as e: ievent.reply('twitter failed: %s' % (str(e),))

cmnds.add('twitter-cmnd', handle_twittercmnd, 'OPER')
examples.add('twitter-cmnd', 'do a cmnd on the twitter API', 'twitter-cmnd home_timeline')

## twitter-users command

def handle_twitterusers(bot, event):
    event.reply("twitter users: ", get_users().users())

cmnds.add("twitter-users", handle_twitterusers, "OPER")
examples.add("twitter-users", "show twitter users", "twitter-users")

## twitter-confirm command

def handle_twitter_confirm(bot, ievent):
    """ arguments: <PIN code> - confirm auth with PIN. """
    go = getauth()
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the %s/config dir. see the examples directory" % getdatadir()) ; return
    pin = ievent.args[0]
    if not pin: ievent.missing("<PIN> .. see the twitter-auth command.") ; return
    try: access_token = getauth(getdatadir()).get_access_token(pin)
    except (tweepy.TweepError, urllib.error.HTTPError) as e: ievent.reply('twitter failed: %s' % (str(e),)) ; return
    twitteruser = get_users()
    twitteruser.add(ievent.user.data.name, access_token.to_string())
    ievent.reply("%s access token saved." % ievent.user.data.name)

cmnds.add('twitter-confirm', handle_twitter_confirm, ['OPER', 'USER', 'GUEST'])
examples.add('twitter-confirm', 'confirm your twitter account', 'twitter-confirm 6992762')

## twitter-auth command

def handle_twitter_auth(bot, ievent):
    """ no arguments - get url to get the auth PIN needed for the twitter-confirm command. """
    go = getauth()
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the .tl/config dir. see the examples directory") ; return
    try: auth_url = getauth(getdatadir()).get_authorization_url()
    except (tweepy.TweepError, urllib.error.HTTPError) as e: ievent.reply('twitter failed: %s' % (str(e),)) ; return
    if bot.type == "irc":
        bot.say(ievent.nick, "sign in at %s" % auth_url)
        bot.say(ievent.nick, "use the provided code in the twitter-confirm command.")
    else:
        ievent.reply("sign in at %s" % auth_url)
        ievent.reply("use the provided code in the twitter-confirm command.")

cmnds.add('twitter-auth', handle_twitter_auth, ['OPER', 'USER', 'GUEST'])
examples.add('twitter-auth', 'adds your twitter account', 'twitter-auth')

## twitter-friends command

def handle_twitterfriends(bot, ievent):
    """ no arguments - show friends timeline (your normal twitter feed). """
    go = getauth()
    if not go: ievent.reply("the twitter plugin needs the credentials.py file in the .tl/config dir. see the examples directory") ; return
    try:
        token = get_token(ievent.user.data.name)
        if not token: ievent.reply("you are not logged in yet .. run the twitter-auth command.") ; return 
        key , secret = getcreds(getdatadir())
        token = tweepy.oauth.OAuthToken(key, secret).from_string(token)
        twitter = twitterapi(key, secret, token)
        method = getattr(twitter, "friends_timeline")
        result = method()
        res = []
        for item in result:
            try: res.append("%s - %s" % (item.author.screen_name, item.text))
            except Exception as ex: handle_exception()
        ievent.reply("results: ", res) 
    except KeyError: ievent.reply('you are not logged in yet. see the twitter-auth command.')
    except (tweepy.TweepError, urllib.error.HTTPError) as e: ievent.reply('twitter failed: %s' % (str(e),))

cmnds.add('twitter-friends', handle_twitterfriends, ['OPER', 'USER', 'GUEST'], threaded=True)
examples.add('twitter-friends', 'show your friends_timeline', 'twitter-friends')

def init():
    from tl.utils.twitter import getcreds
    creds = getcreds()