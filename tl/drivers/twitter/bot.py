# jsb/drivers/twitter/bot.py
#
#

""" the twitter bot is here !! (finally). """

## jsb imports

from tl.lib.botbase import BotBase
from tl.utils.tinyurl import get_tinyurl,  parseurl
from tl.utils.twitter import get_token

## basic imports

import logging
import urllib.parse

## TwitterBot class

class TwitterBot(BotBase):

    def __init__(self, username):
        BotBase.__init__(self, botname="twitter-%s" % username)
        self.username = username
        self.users = TwitterUsers(getdatadir() + os.sep + "twitter" + os.sep + "users")

    def _raw(self, txt, event=None):
        """ post a message on twitter. """
        try:
            if event and event.chan:
                taglist = event.chan.data.taglist
                if taglist:
                   for tag in taglist:
                       txt += " %s" % tag
            url = parseurl(txt)
            tiny = get_tinyurl(url)
            if tiny:
                tinyurl = tiny[0]
                txt = txt.replace(url, tinyurl)
            if len(txt) > 140: logging.error("size of twitter message > 140 chars: %s" % txt) ; return
            token = get_token(self.users, username)
            if not token: raise tweepy.TweepError("Can't get twitter token")
            twitter = twitterapi(key, secret, token)
            status = twitter.update_status(txt)
            logging.warn("posted 1 tweet (%s chars) for %s" % (len(txt), username))
            return status
        except tweepy.TweepError as ex: logging.error("twitter - error: %s" % str(ex))
