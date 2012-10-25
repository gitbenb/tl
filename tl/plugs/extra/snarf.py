# gozerplugs/plugs/snarf.py
# 
#

""" fetch title of url. """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'
__gendoclast__ = ['snarf-disable', ]
__depend__ = ['url', ]

## tl imports

from tl.lib.callbacks import callbacks
from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.utils.url import decode_html_entities, get_encoding, geturl, geturl2
from tl.utils.exception import handle_exception
from tl.lib.persist import Persist, PlugPersist
from tl.lib.persistconfig import PersistConfig
from tl.lib.plugins import plugs as plugins

## basic imports

import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import copy
import re
import socket

## defines

cfg           = PlugPersist('snarf.cfg')
pcfg          = PersistConfig()
pcfg.define('allow', ['text/plain', 'text/html', 'application/xml'])

re_html_title = re.compile('<title>(.*?)</title>', re.I | re.M | re.S)

re_url_match  = re.compile('((?:http|https)://\S+)')

re_html_valid = {
    'result':   re.compile('(Failed validation, \d+ errors?|Passed validation)', re.I | re.M),
    'modified': re.compile('<th>Modified:</th><td colspan="2">([^<]+)</td>', re.I | re.M),
    'server':   re.compile('<th>Server:</th><td colspan="2">([^<]+)</td>', re.I | re.M),
    'size':     re.compile('<th>Size:</th><td colspan="2">([^<]+)</td>', re.I | re.M),
    'content':  re.compile('<th>Content-Type:</th><td colspan="2">([^<]+)</td>', re.I | re.M),
    'encoding': re.compile('<td>([^<]+)</td><td><select name="charset" id="charset">', re.I | re.M),
    'doctype':  re.compile('<td>([^<]+)</td><td><select id="doctype" name="doctype">', re.I | re.M)
    }

urlvalidate   = 'http://validator.w3.org/check?charset=%%28\
detect+automatically%%29&doctype=Inline&verbose=1&%s'

## SnarfException class

class SnarfException(Exception): pass

## geturl_title function

def geturl_title(url):
    """ fetch title of url """
    try: result = geturl2(url)
    except urllib.error.HTTPError as ex: logging.warn("HTTPError: %s" % str(ex)) ; return False
    except urllib.error.URLError as ex: logging.warn("URLError %s" % str(ex)) ; return False
    except IOError as ex:
        try: errno = ex[0]
        except IndexError: handle_exception() ; return
        return False
    if not result: return False
    test_title = re_html_title.search(result)
    if test_title:
        # try to find an encoding and standardize it to utf-8
        encoding = get_encoding(result)
        title = test_title.group(1).replace('\n', ' ')
        title = title.strip()
        return decode_html_entities(title)
    return False

## geturl_validate function

def geturl_validate(url):
    """ validate url """
    url = urlvalidate % urllib.parse.urlencode({'uri': url})
    try: result = geturl2(url)
    except IOError as ex:
        try: errno = ex[0]
        except IndexError: handle_exception() ; return
        return False
    if not result: return False
    results = {}
    for key in list(re_html_valid.keys()):
        results[key] = re_html_valid[key].search(result)
        if results[key]: results[key] = results[key].group(1)
        else: results[key] = '(unknown)'
    return results

## valid_url function

def valid_url(url):
    """ check if url is valid """
    if not re_url_match.match(url): return False
    parts = urllib.parse.urlparse(url)
    # do a HEAD request to get the content-type
    request = urllib.request.Request(url)
    request.get_method = lambda: "HEAD"
    content = urllib.request.urlopen(request)
    if content.headers['content-type']:
        type = content.headers['content-type'].split(';', 1)[0].strip()
        if type not in pcfg.get('allow'): raise SnarfException("Content-Type %s is not allowed" % type)
    cleanurl = '%s://%s' % (parts[0], parts[1])
    if parts[2]: cleanurl = '%s%s' % (cleanurl, parts[2])
    if parts[3]: cleanurl = '%s;%s' % (cleanurl, parts[3])
    if parts[4]: cleanurl = '%s?%s' % (cleanurl, parts[4])
    return cleanurl

## snarf command

def handle_snarf(bot, ievent, direct=True):
    """ snarf provided url or last url in log """
    url = None
    if ievent.rest: url = ievent.rest
    else:
        try: url = plugins.fetch("url").latest(bot, ievent)
        except Exception as ex: handle_exception()
    if not url: ievent.missing('<url>') ; return
    try: url = valid_url(url)
    except KeyError: ievent.reply("can't detect content type") ; return
    except SnarfException as e:
        if direct: ievent.reply('unable to snarf: %s' % str(e))
        return
    except urllib.error.HTTPError as e: ievent.reply('unable to snarf: %s' % str(e)) ; return 
    except urllib.error.URLError as ex: ievent.reply('unable to snarf: %s' % str(ex)) ; return 
    if not url: ievent.reply('invalid url') ; return
    try: title = geturl_title(url)
    except socket.timeout: ievent.reply('%s socket timeout' % url) ; return
    except urllib.error.HTTPError as e: ievent.reply('error: %s' % e) ; return
    if title:
        host = urllib.parse.urlparse(url)[1]
        if len(host) > 20: host = host[0:20] + '...'
        ievent.reply('%s: %s' % (host, title))
    else: ievent.reply('no title found at %s' % urllib.parse.urlparse(url)[1])

cmnds.add('snarf', handle_snarf, 'USER', threaded=True)
cmnds.add('@', handle_snarf, 'USER', threaded=True)
examples.add('snarf', 'fetch the title from an URL', 'snarf http://ggzpreventie.nl')

## snarf-enable command

def handle_snarf_enable(bot, ievent):
    """ enable snarfing in channel """
    if bot.name not in cfg.data: cfg.data[bot.name] = {}
    cfg.data[bot.name][ievent.printto] = True
    cfg.save()
    ievent.reply('ok')

cmnds.add('snarf-enable', handle_snarf_enable, 'OPER')
examples.add('snarf-enable', 'enable snarfing in the channel', 'snarf-enable')

## snarf-disable command

def handle_snarf_disable(bot, ievent):
    """ disable snarfing in channel """
    if bot.name not in cfg.data: ievent.reply('ok') ; return
    cfg.data[bot.name][ievent.printto] = False
    cfg.save()
    ievent.reply('ok')

cmnds.add('snarf-disable', handle_snarf_disable, 'OPER')
examples.add('snarf-disable', 'disable snarfing in the channel', 'snarf-disable')

## snarf-list command

def handle_snarf_list(bot, ievent):
    """ show channels in which snarfing is enabled """
    snarfs = []
    names  = list(cfg.data.keys())
    names.sort()
    for name in names:
        targets = list(cfg.data[name].keys())
        targets.sort()
        snarfs.append('%s: %s' % (name, ' '.join(targets)))
    if not snarfs: ievent.reply('none')
    else: ievent.reply('snarfers enable on: %s' % ', '.join(snarfs))

cmnds.add('snarf-list', handle_snarf_list, 'OPER')
examples.add('snarf-list', 'show in which channels snarfing is enabled', 'snarf-list')

## validate command

def handle_validate(bot, ievent):
    """ validate provided url or last url in log """
    url = None
    if ievent.rest: url = ievent.rest
    else:
        if plugins.url: url = plugins.fetch("url").latest(bot, ievent)
    if not url: ievent.missing('<url>') ; return
    try: url = valid_url(url)
    except urllib.error.HTTPError as e: ievent.reply('error: %s' % e) ; return
    if not url: ievent.reply('invalid or bad URL') ; return
    result = geturl_validate(url)
    if result:
        host = urllib.parse.urlparse(url)[1]
        if len(host) > 20: host = host[0:20] + '...'
        ievent.reply('%s: %s | modified: %s | server: %s | size: %s | content-type: %s | encoding: %s | doctype: %s' % \
            tuple([host] + [result[x] for x in ['result', 'modified', 'server', 'size', 'content', 'encoding', 'doctype']]))

cmnds.add('validate', handle_validate, 'USER', threaded=True)
examples.add('validate', 'validate an URL', 'validate http://ggzpreventie.nl')
