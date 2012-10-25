# tl/plugs/common/feedback.py
#
#

""" give feedback on the bot to feedbackloop@gmail.com. needs a xmpp server, so use tl-xmpp or tl-fleet. """

## tl imports

from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.fleet import getfleet
from tl.lib.factory import bot_factory
from tl.utils.lazydict import LazyDict
from tl.utils.generic import waitforqueue

## basic imports

import uuid
import time

## feedback command

def handle_feedback(bot, event):
    """ 
        arguments: <feedbacktxt> - give feedback to feedbackloop@gmail.com, this needs a jabber server to be able to send the feedback.
        the feedback command can be used in a pipeline.
    
    """ 
    if not event.rest and event.inqueue: payload = waitforqueue(event.inqueue, 2000)
    else: payload = event.rest 
    fleet = getfleet()
    feedbackbot = fleet.getfirstjabber()
    if not feedbackbot: event.reply("can't find an xmpp bot to send the feedback with") ; return
    event.reply("sending to feedbackflowe@gmail.com")
    feedbackbot.say("feedbackflow@gmail.com", "%s send you this: %s" % (event.userhost, payload), event=event)
    event.done()

cmnds.add("feedback", handle_feedback, ["OPER", "USER", "GUEST"], threaded=True)
examples.add("feedback", "send a message to feedbackflow@gmail.com", "1) admin-exceptions ! feedback 2) feedback the bot is missing some spirit !")
