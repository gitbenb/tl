# tl/plugs/common/url.py
#
#

""" maintain log of urls. """

## tl imports

from tl.utils.exception import handle_exception
from tl.lib.callbacks import callbacks
from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.persiststate import PlugState

## basic imports

import re
import os
import logging

## defines
    
re_url_match  = re.compile('((?:http|https)://\S+)')
state = None
initdone = False

## init function

def init():
    global state
    global initdone
    state = PlugState()
    state.define('urls', {})
    initdone = True
    return 1

## size function

def size():
    """ show number of urls. """
    s = 0
    if not initdone: return s
    for i in list(state['urls'].values()):
        for j in list(i.values()): s += len(j)
    return s

## search function

def search(what, queue):
    """ search the url database. """
    global initdone
    result = []
    if not initdone: return result
    try:
        for i in list(state['urls'].values()):
            for urls in list(i.values()):
                for url in urls:
                    if what in url: result.append(url)
    except KeyError: pass
    for url in result: queue.put_nowait(url)

## get function

def latest(bot, event):
    if not state: return ""
    return state.data.urls[bot.cfg.name][event.channel][-1]

## url callbacks

def urlpre(bot, ievent):
    return re_url_match.findall(ievent.txt)

def urlcb(bot, ievent):
    if not state: return 
    try:
        test_urls = re_url_match.findall(ievent.txt)
        for i in test_urls:
            if bot.cfg.name not in state['urls']:
                state['urls'][bot.cfg.name] = {}
            if ievent.channel not in state['urls'][bot.cfg.name]:
                state['urls'][bot.cfg.name][ievent.channel] = []
            if not i in state['urls'][bot.cfg.name][ievent.channel]:
                state['urls'][bot.cfg.name][ievent.channel].append(i)  
        state.save()
        logging.warn("added url from %s" % ievent.auth)
    except Exception as ex: handle_exception()

callbacks.add('CONSOLE', urlcb, urlpre, threaded=True)
callbacks.add('PRIVMSG', urlcb, urlpre, threaded=True)
callbacks.add('MESSAGE', urlcb, urlpre, threaded=True)
callbacks.add('TORNADO', urlcb, urlpre, threaded=True)

## url-search command

def handle_urlsearch(bot, ievent):
    """ arguments: <searchtxt> - search the per channel url database for a search term. """
    if not state: ievent.reply('rss state not initialized') ; return
    if not ievent.rest: ievent.missing('<searchtxt>') ; return
    result = []
    try:
        for i in state['urls'][bot.cfg.name][ievent.channel]:
            if ievent.rest in i: result.append(i)
    except KeyError: ievent.reply('no urls known for channel %s' % ievent.channel) ; return
    except Exception as ex: ievent.reply(str(ex)) ; return
    if result: ievent.reply('results matching %s: ' % ievent.rest, result)
    else: ievent.reply('no result found') ; return

cmnds.add('url-search', handle_urlsearch, ['OPER', 'USER', 'GUEST'])
examples.add('url-search', 'search matching url entries', 'url-search tl')

## url-searchall command

def handle_urlsearchall(bot, ievent):
    """ arguments: <searchtxt> - search all urls. """
    if not state: ievent.reply('rss state not initialized') ; return
    if not ievent.rest: ievent.missing('<searchtxt>') ; return
    result = []
    try:
        for i in list(state['urls'].values()):
            for urls in list(i.values()):
                for url in urls:
                    if ievent.rest in url: result.append(url)
    except Exception as ex: ievent.reply(str(ex)) ; return
    if result: ievent.reply('results matching %s: ' % ievent.rest, result)
    else: ievent.reply('no result found') ; return

cmnds.add('url-searchall', handle_urlsearchall, ['OPER', 'USER', 'GUEST'])
examples.add('url-searchall', 'search matching url entries', 'url-searchall tl')

## url-size command

def handle_urlsize(bot, ievent):
    """ no arguments - show number of urls stored. """
    ievent.reply(str(size()))

cmnds.add('url-size', handle_urlsize, 'OPER')
examples.add('url-size', 'show number of urls in cache', 'url-size')

## url-tail command

def handle_urltail(bot, ievent):
    """ print the last n urls. """
    if not ievent.rest:
        lines = 5
    else:
        try: lines = int(ievent.rest)
        except: lines = 5
    try:
       ievent.reply("last %s urls: " % lines, state['urls'][bot.cfg.name][ievent.channel][-lines:])
    except KeyError: ievent.reply('no urls known for channel %s' % ievent.channel) ; return

cmnds.add('url-tail', handle_urltail, ['OPER', 'USER', 'GUEST'])
examples.add('url-tail', 'show last n urls', 'url-tail 5')
