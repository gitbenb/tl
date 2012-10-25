# tl/plugs/common/imdb.py
#
# author: melmoth

""" query the imdb database. """

## tl imports

from tl.lib.examples import examples
from tl.lib.commands import cmnds
from tl.utils.url import geturl2, striphtml, decode_html_entities
from tl.imports import getjson

## basic imports

import logging

## defines

URL = "http://www.deanclatworthy.com/imdb/?q=%s"

## imdb command

def handle_imdb(bot, event):
    """ arguments: <query> - query the imdb databae at http://www.deanclatworthy.com/imdb/ """
    if not event.rest:  event.missing("<query>") ; return
    query = event.rest.strip()
    urlquery = query.replace(" ", "+")
    result = {}
    res = geturl2(URL % urlquery)
    if not res: event.reply("%s didn't return a result" % (URL % urlquery)) ; return
    try: rawresult = getjson().loads(res)
    except ValueError: event.reply("sorry cannot parse data returned from the server: %s" % res) ; return
    # the API are limited to 30 query per hour, so avoid querying it just for testing purposes
    # rawresult = {u'ukscreens': 0, u'rating': u'7.7', u'genres': u'Animation,&nbsp;Drama,Family,Fantasy,Music', u'title': u'Pinocchio', u'series': 0, u'country': u'USA', u'votes': u'23209', u'languages': u'English', u'stv': 0, u'year': None, u'usascreens': 0, u'imdburl': u'http://www.imdb.com/title/tt0032910/'}
    if not rawresult: event.reply("couldn't look up %s" % query) ; return
    if 'error' in rawresult: event.reply("%s" % rawresult['error']) ; return
    for key in list(rawresult.keys()):
        if not rawresult[key]: result[key] = "n/a"
        else: result[key] = rawresult[key]
    for key in list(result.keys()):
        try: result[key] = striphtml(decode_html_entities(str(rawresult[key])))
        except AttributeError: pass
    if "year" in list(rawresult.keys()): event.reply("%(title)s (%(country)s, %(year)s): %(imdburl)s | rating: %(rating)s (out of %(votes)s votes) | Genres %(genres)s | Language: %(languages)s" % result )
    else: event.reply("%(title)s (%(country)s): %(imdburl)s | rating: %(rating)s (out of %(votes)s votes) | Genres %(genres)s | Language: %(languages)s" % result )

cmnds.add("imdb", handle_imdb, ["OPER", "USER", "GUEST"])
examples.add("imdb", "query the imdb database.", "imdb the matrix")
