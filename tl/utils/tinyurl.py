# tl/utils/tinyurl.py
#
#

""" tinyurl.com feeder """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

## tl imports

from tl.utils.url import striphtml, useragent
from tl.utils.exception import handle_exception
from tl.lib.cache import get, set
from tl.lib.errors import URLNotEnabled

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

posturl = 'http://tinyurl.com/create.php'

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

def parseurl(txt):
    test_url = re_url_match.search(txt)
    if test_url:
        url = test_url.group(1)
        if url: return url

def get_tinyurl(url):
    """ grab a tinyurl. """
    from tl.utils.url import enabled
    if not enabled: raise URLNotEnabled
    res = get(url, namespace='tinyurl') ; logging.debug('tinyurl - cache - %s' % str(res))
    if res and res[0] == '[': return json.loads(res)
    postarray = [
        ('submit', 'submit'),
        ('url', url),
        ]
    postdata = urllib.parse.urlencode(postarray)
    postbytes = bytes(postdata, "utf-8")
    req = urllib.request.Request(url=posturl, data=postbytes)
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
        bline = str(line, "utf-8")
        if bline.startswith('<blockquote><b>'): urls.append(striphtml(bline.strip()).split('[Open')[0])
    if len(urls) == 3: urls.pop(0)
    set(url, json.dumps(urls), namespace='tinyurl')
    return urls
