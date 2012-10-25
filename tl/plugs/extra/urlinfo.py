# tl/plugs/common/urlinfo.py
# -*- coding: utf-8 -*-
#
#

"""
    Catches URLs on channel and gives information about them like title, image size, etc.
    Uses http://whatisthisfile.appspot.com/ via XMLRPC

    Example:
    19:20 <@raspi> http://www.youtube.com/watch?v=9RZ-hYPAMFQ
    19:20 <@bot> Title: "YouTube - Black Knight Holy Grail"
    19:28 <@raspi> test http://www.raspi.fi foobar http://raspi.fi/wp-includes/images/rss.png
    19:28 <@bot> 1. Title: "raspi.fi" Redirect: http://raspi.fi/  2. Image: 14x14

"""

__author__ = "Pekka 'raspi' Järvinen - http://raspi.fi/"
__license__ = 'BSD'

## tl imports

from tl.utils.exception import handle_exception
from tl.lib.callbacks import callbacks
from tl.lib.commands import cmnds
from tl.lib.persist import PlugPersist
from tl.lib.examples import examples
from tl.plugs.extra.tinyurl import get_tinyurl
from tl.lib.errors import URLNotEnabled

## basic import

import re
import urllib.parse
import xmlrpc.client
import socket
import logging

## defines

cfg = PlugPersist('urlinfo', {})

## sanitize function

def sanitize(text):
    """ Remove non-urls word by word. """
    text = text.strip()
    text = re.sub('\s\s+', ' ', text)
    tmp = ''
    for i in text.split(' '):
        if len(i) >= 5:
            if i.find('www.') != -1 or i.find('http') != -1: tmp += i + ' '
    tmp = tmp.strip()
    tmp2 = ''
    for i in tmp.split(' '):
        if not i: continue
        if (i[0] == '(' and i[-1] == ')') or (i[0] == '[' and i[-1] == ']') or (i[0] == '<' and i[-1] == '>') or (i[0] == '{' and i[-1] == '}'):
            # First and last character is one of ()[]{}<>
            tmp2 += i[1:-1:1] + ' '
        else: tmp2 += i + ' '
    tmp2 = tmp2.strip();
    tmp = ''
    for i in tmp2.split(' '):
        if i.find('www.') == 0: tmp += 'http://' + i + ' '
        else: tmp += i + ' '
    tmp = tmp.strip();
    out = tmp;
    return out;

## getUrls function

def getUrls(text):
    """ get valid urls. """
    regex = r"http[s]?://[-A-Za-z0-9+&@#/%=~_()|!:,.;?]*[-A-Za-z0-9+&@#/%=~_()|?]"
    p = re.compile(regex)
    urls = []
    for i in text.split(' '):
        for x in p.findall(i):
            url = urllib.parse.urlparse(x)
            if url.geturl() not in urls: urls.append(url.geturl())
    return urls

## getUrlInfo function

def getUrlInfo(text):
    """ get info of urls in given txt. """
    from tl.utils.url import enabled
    if not enabled: raise URLNotEnabled
    out = ''
    text = sanitize(text)
    urls = getUrls(text)
    if urls:
        idx = 1
        for i in urls:
            o = ''
            try:
                server = xmlrpc.client.ServerProxy("http://whatisthisfile.appspot.com/xmlrpc")
                logging.info('urlinfo - XMLRPC query: %s' % i)
                urlinfo = server.app.query(i)
                if 'html' in urlinfo:
                     if 'title' in urlinfo['html']: o += 'Title: "%s" ' % urlinfo['html']['title'].strip()
                elif 'image' in urlinfo: o += 'Image: %dx%d ' % (urlinfo['image']['width'], urlinfo['image']['height'])
                if not o: continue
                if len(o):
                    if len(urls) > 1: out += ' ' + str(idx) + '. ' ; idx += 1
                out += o
                if "tinyurl" in i: out = out.strip() ; out += " - %s" % i
                elif not "http://" in out: out = out.strip() ; out += " - %s" % get_tinyurl(i)[0]
            except Exception: pass
    return out.strip()

## callbacks

def catchHasUrls(bot, ievent):
    """ catch channel chat for possible URLs. """
    if ievent.how == "background": return 0
    if ievent.channel in cfg.data and cfg.data[ievent.channel]:
        if len(ievent.txt) >= 5:
            if (ievent.txt.find('www.') != -1) or (ievent.txt.find('http') != -1): return 1
    return 0  


def catchUrls(bot, ievent):
    """ the urlinfo callback. """
    bot.say(ievent.channel, getUrlInfo(ievent.txt))

callbacks.add('PRIVMSG', catchUrls, catchHasUrls, threaded=True)
callbacks.add('CONSOLE', catchUrls, catchHasUrls, threaded=True)
callbacks.add('MESSAGE', catchUrls, catchHasUrls, threaded=True)
callbacks.add('DISPATCH', catchUrls, catchHasUrls, threaded=True)
callbacks.add('TORNADO', catchUrls, catchHasUrls, threaded=True)

## urlinfo-enable command

def handle_urlinfo_enable(bot, ievent):
    """ no arguments - enable urlinfo in a channel. """
    cfg.data[ievent.channel] = True
    cfg.save()
    ievent.reply('urlinfo enabled')

cmnds.add('urlinfo-enable', handle_urlinfo_enable, ['OPER'])
examples.add('urlinfo-enable', 'enable urlinfo in the channel', 'urlinfo-enable')

## urlinfo-disable command

def handle_urlinfo_disable(bot, ievent):
    """ no arguments - disable urlinfo in a channel. """
    cfg.data[ievent.channel] = False
    cfg.save()
    ievent.reply('urlinfo disabled')

cmnds.add('urlinfo-disable', handle_urlinfo_disable, 'OPER')
examples.add('urlinfo-disable', 'disable urlinfo in the channel', 'urlinfo-disable')

## urlinfo-list command

def handle_urlinfo_list(bot, ievent):
    """ no arguments - list what channels are using urlinfo. """
    chans = []
    names = list(cfg.data.keys())
    names.sort()
    if not names: ievent.reply('none')
    else: ievent.reply('urlinfo enabled on channels: ', names)

cmnds.add('urlinfo-list', handle_urlinfo_list, 'OPER')
examples.add('urlinfo-list', 'show in which channels urlinfo is enabled', 'urlinfo-list')
