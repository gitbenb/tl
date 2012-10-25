# tl/utils/url.py
#
# most code taken from maze

""" url related functions. """

## tl imports

from .statdict import StatDict
from .help import istr, ibytes, cstr
from .lazydict import LazyDict
from .generic import fromenc, toenc, printline
from tl.lib.errors import URLNotEnabled

## basic imports

import logging
import time
import sys
import re
import traceback
import queue
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import socket
import random
import os
import _thread
import types
import http.client
import io
import html.entities
import tempfile
import cgi

## defines

re_url_match  = re.compile('((?:http|https)://\S+)')

try: import chardet
except ImportError: chardet = None

enabled = True
stats = StatDict()

# url_disable function

def url_enable():
    global enabled
    enabled = True

# url_enable function

def url_disable():
    global enabled
    enabled = False
    logging.error("url fetching is disabled.")

## useragent function

def useragent():
    """ provide useragent string """
    from tl.version import getversion
    (name, version) = getversion().split()[0:2]
    return 'Mozilla/5.0 (X11; Linux x86_64); %s %s; http:///docs/tl)' % (name, version)

## Url class

class Url(LazyDict):

    def __init__(self, url, *args, **kwargs):
        self.url = url
        self.urls = []
        self.parse()

    def parse(self, url=None):
        """
        
        Attribute	Index	Value			Value if not present
        scheme		0	URL scheme specifier	empty string
        netloc		1	Network location part	empty string
        path		2	Hierarchical path	empty string
        query		3	Query component		empty string
        fragment	4	Fragment identifier	empty string
        
        """
        if url: self.url = url
        self.parsed = urllib.parse.urlsplit(url or self.url)
        self.target = self.parsed[2].split("/")
        if "." in self.target[-1]:
            self.basepath = "/".join(self.target[:-1])
            self.file = self.target[-1]
        else: self.basepath = self.parsed[2] ; self.file = None
        if self.basepath.endswith("/"): self.basepath = self.basepath[:-1]
        self.base = urllib.parse.urlunsplit((self.parsed[0], self.parsed[1], self.basepath , "", ""))
        self.root = urllib.parse.urlunsplit((self.parsed[0], self.parsed[1], "", "", ""))

    def fetch(self, *args, **kwargs):
        self.html = geturl2(self.url, html=True, *args,**kwargs)
        self.status = self.html.status
        self.txt = striphtml(self.html)
        self.lastpolled = time.time()
        self.parse()
        return self.html

    def geturls(self):
        if not self.html: self.fetch()
        urls = []
        from tl.imports import getBeautifulSoup
        soup = getBeautifulSoup()
        s = soup.BeautifulSoup(self.html)
        tags = s('a')
        for tag in tags:
           href = tag.get("href")
           if href:
               href = href.split("#")[0]
               if not href: continue
               if not href.endswith(".html"): continue
               if ".." in href: continue
               if href.startswith("mailto"): continue
               if not "http" in href:
                    if href.startswith("/"): href = self.root + href
                    else: href = self.base + "/" + href
               if not self.root in href: logging.warn("%s not in %s" % (self.root, href)) ; continue
               if href not in urls: urls.append(href)
        logging.warn("found %s urls" % len(urls))
        return urls

## CBURLopener class

class CBURLopener(urllib.request.FancyURLopener):
    """ our URLOpener """
    def __init__(self, version, *args):
        if version: self.version = version
        else: self.version = useragent()
        urllib.request.FancyURLopener.__init__(self, *args)

## geturl function

def geturl(url, version=None):
    """ fetch an url. """
    global enabled
    if not enabled: raise URLNotEnabled(url)
    urllib.request._urlopener = CBURLopener(version)
    logging.warn('fetching %s' % url)
    result = urllib.request.urlopen(url)
    tmp = result.read()
    result.close()
    return tmp

## geturl2 function

def geturl2(url, decode=False, timeout=5, dobytes=False, html=False, *args, **kwargs):
    """ use urllib2 to fetch an url. """
    global enabled
    if not enabled: stats.upitem("urlnotenabled") ; raise URLNotEnabled(url)
    logging.warn('fetching %s' % url)
    request = urllib.request.Request(url)
    request.add_header('User-Agent', useragent())
    opener = urllib.request.build_opener()
    result = opener.open(request, timeout=timeout)
    res = result.read()
    if not res: return res
    #res = fromenc(res, "utf-8")
    if html: res = res.replace("//", "/")
    res = cstr(res)
    #else: res = ibytes(bytes(res, "utf-8"))
    info = result.info()
    result.close()
    res.status = result.code
    res.info = info
    return res

## geturl4 function

def geturl4(url, myheaders={}, postdata={}, keyfile="", certfile="", port=80):
    """ use httplib to fetch an url. """
    global enabled
    if not enabled: raise URLNotEnabled(url)
    headers = {'Content-Type': 'text/html', 'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
    headers.update(myheaders)
    urlparts = urllib.parse.urlparse(url)
    try:
       port = int(urlparts[1].split(':')[1])
       host = urlparts[1].split(':')[0]
    except: host = urlparts[1]
    if keyfile: connection = http.client.HTTPSConnection(host, port, keyfile, certfile)
    elif 'https' in urlparts[0]: connection = http.client.HTTPSConnection(host, port)
    else: connection = http.client.HTTPConnection(host, port)
    if type(postdata) == dict: postdata = urllib.parse.urlencode(postdata)
    logging.warn('fetching %s' % url)
    connection.request('GET', urlparts[2])
    return connection.getresponse()


## posturl function

def posturl(url, myheaders, postdata, keyfile=None, certfile="",port=80):
    """ very basic HTTP POST url retriever. """
    global enabled
    if not enabled: raise URLNotEnabled(url)
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
    headers.update(myheaders)
    urlparts = urllib.parse.urlparse(url)
    if keyfile: connection = http.client.HTTPSConnection(urlparts[1], port, keyfile, certfile)
    else: connection = http.client.HTTPConnection(urlparts[1])
    if type(postdata) == dict: postdata = urllib.parse.urlencode(postdata)
    logging.warn('post %s' % url)
    connection.request('POST', urlparts[2], postdata, headers)
    return connection.getresponse()

## delete url function

def deleteurl(url, myheaders={}, postdata={}, keyfile="", certfile="", port=80):
    """ very basic HTTP DELETE. """
    global enabled
    if not enabled: raise URLNotEnabled(url)
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
    headers.update(myheaders)
    urlparts = urllib.parse.urlparse(url)
    if keyfile and certfile: connection = http.client.HTTPSConnection(urlparts[1], port, keyfile, certfile)
    else: connection = http.client.HTTPConnection(urlparts[1])
    if type(postdata) == dict: postdata = urllib.parse.urlencode(postdata)
    logging.info('delete %s' % url)
    connection.request('DELETE', urlparts[2], postdata, headers)
    return connection.getresponse()

## put url function

def puturl(url, myheaders={}, postdata={}, keyfile="", certfile="", port=80):
    """ very basic HTTP PUT. """
    global enabled
    if not enabled: raise URLNotEnabled(url)
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain; text/html', 'User-Agent': useragent()}
    headers.update(myheaders)
    urlparts = urllib.parse.urlparse(url)
    if keyfile: connection = http.client.HTTPSConnection(urlparts[1], port, keyfile, certfile)
    else: connection = http.client.HTTPConnection(urlparts[1])
    if type(postdata) == dict: postdata = urllib.parse.urlencode(postdata)
    logging.info('put %s' % url)
    connection.request('PUT', urlparts[2], postdata, headers)
    return connection.getresponse()

## getpostdata function

def getpostdata(event):
    """ retrive post data from url data. """
    try:
        ctype, pdict = cgi.parse_header(event.headers.getheader('content-type'))
    except AttributeError: ctype, pdict = cgi.parse_header(event.headers.get('content-type'))
    body = cgi.FieldStorage(fp=event.rfile, headers=event.headers, environ = {'REQUEST_METHOD':'POST'}, keep_blank_values = 1)
    result = {}
    for name in dict(body): result[name] = body.getfirst(name)
    return result

## getpostdata_gae function

def getpostdata_gae(request):
    """ retrive post data from url data. """
    #try:
    #    ctype, pdict = cgi.parse_header(request.headers.getheader('content-type'))
    #except AttributeError: ctype, pdict = cgi.parse_header(request.headers.get('content-type'))
    #body = cgi.FieldStorage(headers=request.headers, environ = {'REQUEST_METHOD':'POST'}, keep_blank_values = 1)
    return urllib.parse.unquote_plus(request.body[:-1].strip())
    #result = {}
    #for name in dict(body): result[name] = body.getfirst(name)
    #return result

## decode_html_entities function

def decode_html_entities(s):
    """ smart decoding of html entities to utf-8 """
    if not type(s) == str: return s
    re_ent_match = re.compile('&([^;]+);')
    re_entn_match = re.compile('&#([^;]+);')
    try: s = s.decode('utf-8', 'replace')
    except: return s

    def to_entn(match):
        """ convert to entities """
        if match.group(1) in html.entities.entitydefs:
            return html.entities.entitydefs[match.group(1)].decode('latin1', 'replace')
        return match.group(0)

    def to_utf8(match):
        """ convert to utf-8 """
        return chr(int(match.group(1)))

    s = re_ent_match.sub(to_entn, s)
    s = re_entn_match.sub(to_utf8, s)
    return s

## get_encoding function

def get_encoding(data):
    """ get encoding from web data """
    if hasattr(data, 'info') and 'content-type' in data.info and 'charset' in data.info['content-type'].lower():
        charset = data.info['content-type'].lower().split('charset', 1)[1].strip()
        if charset[0] == '=':
            charset = charset[1:].strip()
            if ';' in charset: return charset.split(';')[0].strip()
            return charset
    if '<meta' in data.lower():
        metas = re.findall('<meta[^>]+>', data, re.I | re.M)
        if metas:
            for meta in metas:
                test_http_equiv = re.search('http-equiv\s*=\s*[\'"]([^\'"]+)[\'"]', meta, re.I)
                if test_http_equiv and test_http_equiv.group(1).lower() == 'content-type':
                    test_content = re.search('content\s*=\s*[\'"]([^\'"]+)[\'"]', meta, re.I)
                    if test_content:
                        test_charset = re.search('charset\s*=\s*([^\s\'"]+)', meta, re.I)
                        if test_charset: return test_charset.group(1)
    if chardet:
        test = chardet.detect(data)
        if 'encoding' in test: return test['encoding']
    return sys.getdefaultencoding()

## striphtml function

from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

def striphtml(html, strict=False):
    s = MLStripper()
    s.strict = strict
    s.feed(html)
    return s.get_data()