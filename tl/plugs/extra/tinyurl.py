# tl/plugs/common/tinyurl.py
#
#

""" tinyurl.com feeder """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

## tl imports

from tl.lib.commands import cmnds
from tl.utils.url import striphtml, useragent
from tl.lib.examples import examples
from tl.utils.exception import handle_exception
from tl.lib.persistconfig import PersistConfig
from tl.lib.cache import get, set

## plug config

plugcfg = PersistConfig()
plugcfg.define("url", 'http://tinyurl.com/create.php')

## simpljejson

from tl.imports import getjson
json = getjson()

## basic imports

import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import re
import logging

## defines

re_url_match  = re.compile('((?:http|https)://\S+)')
urlcache = {}

## functions

def valid_url(url):
    """ check if url is valid """
    if not re_url_match.search(url): return False
    parts = urllib.parse.urlparse(url)
    cleanurl = '%s://%s' % (parts[0], parts[1])
    if parts[2]: cleanurl = '%s%s' % (cleanurl, parts[2])
    if parts[3]: cleanurl = '%s;%s' % (cleanurl, parts[3])
    if parts[4]: cleanurl = '%s?%s' % (cleanurl, parts[4])
    return cleanurl

## callbacks

def precb(bot, ievent):
    test_url = re_url_match.search(ievent.txt)
    if test_url: return True

def privmsgcb(bot, ievent):
    """ callback for urlcaching """
    test_url = re_url_match.search(ievent.txt)
    if test_url:
        url = test_url.group(1)
        if bot.cfg.name not in urlcache: urlcache[bot.cfg.name] = {}
        urlcache[bot.cfg.name][ievent.target] = url

# not enabled right now
#callbacks.add('PRIVMSG', privmsgcb, precb)

def get_tinyurl(url):
    """ grab a tinyurl. """
    res = get(url, namespace='tinyurl') ; logging.debug('tinyurl - cache - %s' % str(res))
    if res and res[0] == '[': return json.loads(res)
    postarray = [
        ('submit', 'submit'),
        ('url', url),
        ]
    postdata = urllib.parse.urlencode(postarray)
    req = urllib.request.Request(url=plugcfg.url, data=bytes(postdata, "utf-8"))
    req.add_header('User-agent', useragent())
    try: res = urllib.request.urlopen(req).readlines()
    except urllib.error.URLError as e: logging.warn('tinyurl - %s - URLError: %s' % (url, str(e))) ; return
    except urllib.error.HTTPError as e: logging.warn('tinyurl - %s - HTTP error: %s' % (url, str(e))) ; return
    except Exception as ex:
        if "DownloadError" in str(ex): logging.warn('tinyurl - %s - DownloadError: %s' % (url, str(e)))
        else: handle_exception()
        return
    urls = []
    for line in res:
        l = str(line, "utf-8")
        if l.startswith('<blockquote><b>'): urls.append(striphtml(l.strip()).split('[Open')[0])
    if len(urls) == 3: urls.pop(0)
    set(url, json.dumps(urls), namespace='tinyurl')
    return urls

## tinyurl command

def handle_tinyurl(bot, ievent):
    """ arguments: <url> - get tinyurl from provided url. """
    if not ievent.rest and (bot.cfg.name not in urlcache or ievent.target not in urlcache[bot.cfg.name]):
        ievent.missing('<url>')
        return
    elif not ievent.rest: url = urlcache[bot.cfg.name][ievent.target]
    else: url = ievent.rest
    url = valid_url(url)
    if not url: ievent.reply('invalid or bad URL') ; return
    tinyurl = get_tinyurl(url)
    if tinyurl: ievent.reply(' .. '.join(tinyurl))
    else: ievent.reply('failed to create tinyurl')

cmnds.add('tinyurl', handle_tinyurl, ['OPER', 'USER', 'GUEST'], threaded=True)
examples.add('tinyurl', 'show a tinyurl', 'tinyurl http://jsonbbot.org')
