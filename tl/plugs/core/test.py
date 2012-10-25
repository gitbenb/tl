# tl/plugs/core/test.py
# encoding: utf-8
#
#

""" test plugin. """

import tl
from tl.utils.exception import exceptionmsg, handle_exception, exceptionevents, exceptionlist
from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.eventbase import EventBase
from tl.lib.users import users
from tl.lib.threads import start_new_thread
from tl.utils.generic import waitforqueue, waitevents
from tl.lib.runner import cmndrunner, defaultrunner, threadrunner
from tl.lib.errors import NoSuchCommand
from tl import setglobal, getglobal

## basic imports

import time
import random
import copy
import logging
import queue

## defines

cpy = copy.deepcopy

#donot = ['tinyurl', 'deadline', 'imdb', 'wiki', 'translate', 'rss', 'docmnd', 'exception', 'forward', 'admin', 'urlinfo', 'spider', 'fleet', 'validate', 'silent', 'test-plugs', 'markov-learn', 'loglevel', 'twitter', 'snarf', 'relay', 'reboot', 'quit']
donot = ["boot", "docmnd", "loglevel", "admin-stop", "test-plugs", "quit"]
disabled = ['tinyurl', 'imdb', 'wikipedia', 'translate', 'rss', 'forward', 'admin', 'urlinfo', 'spider', 'fleet', 'twitter', 'snarf', 'relay']
errors = {}
teller = 0

## dotest function

def dotest(bot, event, filter="", direct=False):
    """ do 1 test loop on the bot, e.g. execute all the examples found. """
    global teller
    global errors
    match = filter
    waiting = []
    examplez = examples.getexamples(disabled)
    first = []
    for example in examples:
        try:
            mod = bot.plugs.get(example.modname)
            first = mod.__first__
        except AttributeError: pass
    random.shuffle(examplez)
    for example in first + examplez:
        if match and match not in example: continue
        skip = False
        for dont in donot:
            if dont in example: skip = True
        if skip: continue
        teller += 1
        e = bot.make_event(event.auth, event.channel, ";" + example, event, cbtype=event.cbtype)
        e.speed = teller % 5
        e.nodispatch = False
        e.iscommand = True
        e.globalerrors = True
        try:
            if direct: e.execute()
            else:
                bot.put(e)
                waiting.append(e)               
        except NoSuchCommand as ex: logging.error("failed to find %s command" % str(ex)) ; continue
        except Exception as ex: altar.testerrors[example] = str(ex)
        teller += 1
        time.sleep(0.01)
    for e in waiting: e.join()
    event.reply("%s commands executed" % teller)

## test-plugs command

def handle_testplugs(bot, event):
    """ no arguments - test the plugins by executing all the available examples. """
    #bot.plugs.loadall(force=True)
    global teller
    try: threaded = event.args[0]
    except (ValueError, IndexError): threaded = 1
    try: loop = int(event.args[1])
    except (ValueError, IndexError): loop = 1
    try: filter = event.args[2]
    except (ValueError, IndexError): filter = ""
    threads = []
    teller = 0
    jobs = []
    #bot.plugs.disable(disabled)
    event.dontclose = True
    for i in range(loop):
        if threaded:
            job = threadrunner.put(5, "dotest", dotest, bot, event, filter)
            jobs.append(job)
        else: dotest(bot, event)
    if jobs:
        logging.error("%s jobs launched" % len(jobs))
        for job in jobs:
            if job: logging.info("trying to join %s" % str(job)) ; job.join()
    testerrors = getglobal("testerrors")
    if testerrors:
        event.reply("there are %s test errors .. " % len(testerrors))
        for cmnd, error in testerrors.items(): event.reply("%s - %s" % (cmnd, error))
    else: event.reply("no errors")
    errors = getglobal("errors")
    if errors:
        event.reply("there are %s errors .. " % len(errors))
        for cmnd, error in errors.items(): event.reply("%s - %s" % (cmnd, error))
    else: event.reply("no errors")
    for (event, msg) in exceptionevents: event.reply("EXCEPTION: %s - %s" % (event.txt,msg))
    for msg in exceptionlist: event.reply("EXCEPTION: %s" % msg)
    #event.outqueue.append(None)

cmnds.add('test-plugs', handle_testplugs, ['TEST', 'USER'], speed=3, threaded=True)
examples.add('test-plugs', 'test all plugins by running there examples', 'test-plugs')

## test-forcedconnection command

def handle_forcedreconnect(bot, ievent):
    """ no arguments - do a forced reconnect. """
    if not bot.sock: ievent.reply("%s bot has no socket to close" % bot.cfg.name) ; return
    if not bot.cfg.ssl: bot.sock.shutdown(2)
    else: bot.sock.shutdown()

cmnds.add('test-forcedreconnect', handle_forcedreconnect, 'TEST')

## test-forcedexception command

def handle_forcedexception(bot, ievent):
    """ no arguments - raise a exception. """
    ievent.reply("raising exception.")
    raise Exception('test exception')

cmnds.add('test-forcedexception', handle_forcedexception, 'TEST')
examples.add('test-forcedexception', 'throw an exception as test', 'test-forcedexception')

## test-forcedexceptionthreaded command

def handle_forcedexceptionthreaded(bot, ievent):
    """ no arguments - raise a exception. """
    ievent.reply("raising exception")
    raise Exception('test exception')

cmnds.add('test-forcedexceptionthreaded', handle_forcedexceptionthreaded, 'TEST', threaded=True)
examples.add('test-forcedexceptionthreaded', 'throw an exception as test in a thread', 'test-forcedexceptionthreaded')

## test-wrongxml command

def handle_testwrongxml(bot, ievent):
    """ no arguments - try sending borked xml. """
    if not bot.type == "sxmpp":
        ievent.reply('only sxmpp')
        return
    ievent.reply('sending bork xml')
    bot._raw('<message asdfadf/>')

cmnds.add('test-wrongxml', handle_testwrongxml, 'TEST')

## test-unicode command

def handle_testunicode(bot, ievent):
    """ no arguments - send unicode test down the output paths. """
    outtxt = "Đíť ìš éèñ ëņċøďıńğŧęŝţ· .. にほんごがはなせません .. ₀0⁰₁1¹₂2²₃3³₄4⁴₅5⁵₆6⁶₇7⁷₈8⁸₉9⁹ .. ▁▂▃▄▅▆▇▉▇▆▅▄▃▂▁ .. .. uǝʌoqǝʇsɹǝpuo pɐdı ǝɾ ʇpnoɥ ǝɾ"
    ievent.reply(outtxt)
    bot.say(ievent.channel, outtxt, event=ievent)

cmnds.add('test-unicode', handle_testunicode, 'TEST')
examples.add('test-unicode', 'test if unicode output path is clear', 'test-unicode')

## test-docmnd command

def handle_testdocmnd(bot, ievent):
    """ no arguments - call bot.docmnd(). """
    if ievent.rest: bot.docmnd(ievent.origin or ievent.userhost, ievent.channel, ievent.rest, event=ievent)
    else: ievent.missing("<cmnd>") ; return
    ievent.done()

cmnds.add('test-docmnd', handle_testdocmnd, 'TEST')
examples.add('test-docmnd', 'test the bot.docmnd() method', 'test-docmnd version')

## test-say command

def handle_testsay(bot, ievent):
    """ arguments: <txt> - call the say command on the current bot. """
    if not ievent.rest:
        ievent.missing("<txt>")
        return
    bot.say(ievent.channel, ievent.rest)

cmnds.add('test-say', handle_testsay, 'TEST')
examples.add('test-say', 'use bot.say()', 'test-say')

## test-options command

def handle_testoptions(bot, ievent):
    """ no arguments - show options in current event. """
    ievent.reply('"%s" - %s' % (ievent.txt, str(ievent.options)))

cmnds.add('test-options', handle_testoptions, 'TEST')
examples.add('test-options', "test event options", "test-options")

## test-deadline command

def handle_testdeadline(bot, ievent):
    """ no arguments - slee for 40 seconds in the mainloop. """
    ievent.reply('starting 40 sec sleep')
    time.sleep(40)

cmnds.add('test-deadline', handle_testdeadline, 'TEST')
examples.add('test-deadline', "sleep 40 sec to trigger deadlineexceeded exception (GAE)", "test-deadline")

## test-html command

def handle_testhtml(bot, ievent):
    """ arguments: [<txt>] - test the html=True option to event.reply(). """
    if not ievent.rest: data = '<span style="font-family: fixed; font-size: 10pt"><b>YOOOO BROEDERS</b></span>'
    else: data = ievent.rest
    ievent.reply(data, html=True)

cmnds.add('test-html', handle_testhtml, 'TEST')
examples.add('test-html', 'test html output', '1) test-html 2) test-html <h1><YOO</h1>')

## test-uuid command

def handle_testuuid(bot, ievent):
    """ no arguments - show a uuid4. """
    import uuid
    ievent.reply(str(uuid.uuid4()))

cmnds.add('test-uuid', handle_testuuid, 'TEST')
examples.add("test-uuid", "show a uuid4.", "test-uuid")

## test-threaded command

def handle_testthreaded(bot, ievent):
    """ no arguments - run a threaded command. """
    ievent.reply("yoooo!")

cmnds.add("test-threaded", handle_testthreaded, "TEST", threaded=True)
examples.add("test-threaded", "run a threaded command.", "test-threaded")

## test-backend command

def handle_testbackend(bot, ievent):
    """ no arguments - run a threaded command. """
    ievent.reply("backend yoooo!")

cmnds.add("test-backend", handle_testthreaded, "TEST", threaded="backend")
examples.add("test-backend", "run a test command on the backend", "test-backend")

## test-re command

def handle_testre(bot, event):
    """ no arguments - test the bots RE handling. """
    event.reply(str(event.groups))

cmnds.add("test-re (.*)$", handle_testre, "TEST", regex=True)
examples.add("test-re", "regular expression as command test", "test-re mekker")

## test-bork command

def handle_testioerror(bot, event):
    """ test the reconnect code by raise an exception in bot._raw(). """
    if bot.ownercheck(event.userhost): bot.doioerror = True
    else: event.reply("you need to be owner to use this command") ; return
    event.done()

cmnds.add("test-ioerror", handle_testioerror, "TEST")
examples.add("test-ioerror", "test the reconnect code by raising a Excepton in Bot._raw", "test-ioerror")

## test-multi command

def handle_testmulti(bot, event):
    try: nr = int(event.rest)
    except: event.missing("<nr>") ; return
    if nr > 5: nr = 5
    for i in range(nr): event.reply("bla %s" % i)

cmnds.add("test-multi", handle_testmulti, ["OPER",])
