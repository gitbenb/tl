# tl/plugs/socket/fish.py
#
#

""" 
    Encrypts incoming and outgoing text using the FiSH encryption.

    Help on the fish command:

    event.reply("help                      -- shows this text")
    event.reply("keyx <nick>               -- Exchanges key")
    event.reply("key  <user|channel> <key> -- Set the key")
    event.reply("del  <user|channel>       -- Removes the key")

 """

__author__ = "Frank Spijkerman"

## tl imports

from tl.lib.commands import cmnds
from tl.lib.examples import examples
from tl.lib.callbacks import callbacks
from tl.lib.morphs import outputmorphs
from tl.lib.morphs import inputmorphs
from tl.lib.persiststate import PlugState
from tl.utils.lazydict import LazyDict
from tl.lib.persist import Persist
from tl.utils.name import stripname
from tl.lib.datadir import getdatadir
from tl.utils.generic import getwho
from tl.lib.users import getusers
from tl.lib.errors import RequireError
from tl.lib.persistconfig import PersistConfig

try: from tl.contrib.irccrypt import *
except Exception as ex: raise RequireError("irccrypt doesn't run on python3 (yet)")

## basic imports

import os
import logging
import pickle

## check for pycrypto dependancy
got = False

try:
    import Crypto.Cipher.Blowfish
    import Crypto.Cipher.AES
    got = True
except ImportError: 
    raise RequireError("PyCrypto is required for FiSH. Please install this library if you want to use this plug")

## defines

cfg = PersistConfig()
cfg.define("enable", 0)

users = getusers()

## KeyStore class

class KeyStore(Persist):
  def __init__(self, keyname):
    Persist.__init__(self, getdatadir() + os.sep + 'keys' + os.sep + 'fish' + os.sep + stripname(keyname))

## make sure we get loaded

def dummycb(bot, event): pass

callbacks.add("START", dummycb)

## plugin

def init():
  """ Init """
  if not got: raise RequireError("PyCrypto is required for FiSH. Please install this library if you want to use this plug")
  if cfg.enable:
    inputmorphs.add(fishin)
    outputmorphs.add(fishout)
    callbacks.add("NOTICE", dh1080_exchange)
    cmnds.add("fish", handle_fish, "OPER")
    examples.add("fish", "command that handles fish enrypting over IRC", "fish help")
  else: logging.warn("fish plugin is not enabled - use fish-cfg enable 1")

## fishin function

def fishin(text,event = None):
  if event and not (event.bottype == "irc" or event.bottype == "botbase"): return text
  if text.startswith('+OK '):
    target = None
    if event and event.channel and event.channel.startswith("#"):
      target = event.channel
    elif event:
      u  = users.getuser(event.userhost)
      if u: target = u.data.name

    if not target: return

    key = KeyStore(stripname(target))
    if not key.data.key:
      logging.debug("FiSHin: No key found for target %s" % target)
      return text

    try:
      #logging.debug("FiSHin raw: key: %s Raw: %s (%s)" % (key.data.key, text, target))
      text = decrypt(key.data.key, text)
      logging.debug("FiSHin raw decrypt: :%s:" % text)
      return text
    except (MalformedError, UnicodeDecodeError):
      return None 

  return text

## fishout function

def fishout(text, event):
  if event and not (event.bottype == "irc" or event.bottype == "botbase"): return text
  target = None
  if event and event.channel and event.channel.startswith("#"):
    target = event.channel
    if not target:
        u = users.getuser(event.userhost)
        if u: target = u.data.name
  
  if not target: return

  key = KeyStore(stripname(target))
  if not key.data.key:
    logging.debug("FiSHout: No key found for target %s" % target)
    return text 

  cipher = encrypt(key.data.key, text)
  return cipher

## encrypt function

def encrypt(key, text):
  b = Blowfish(key)
  return blowcrypt_pack(text, b)

## decrypt function

def decrypt(key, inp):
  b = Blowfish(key)
  return blowcrypt_unpack(inp, b)

## dh1080_exchange function

def dh1080_exchange(bot, ievent):
  # Not a known user, so also no key.
  u = users.getuser(ievent.userhost)
  if u: target = u.data.name
  else: return True
  if ievent.txt.startswith("DH1080_INIT "):
    logging.warn("FiSH: DH1080_INIT with %s" % target)
    key = KeyStore(stripname(target))

    dh = DH1080Ctx()
    if dh1080_unpack(ievent.txt, dh) != True:
      logging.warn("FiSH Key exchange failed!")
      return False

    key.data.key = dh1080_secret(dh)
    key.data.dh = pickle.dumps(dh)
    key.save()

    logging.debug("FiSH UserKey: %s Key: %s" % (ievent.txt[12:], key.data.key))
    ievent.bot.notice(ievent.nick, dh1080_pack(dh))

    return False

  if ievent.txt.startswith("DH1080_FINISH "):
    key = KeyStore(stripname(target))

    logging.warn("FiSH: DH1080_FINISH")
    dh = pickle.loads(key.data.dh)
    if dh1080_unpack(ievent.txt, dh) != True:
      logging.warn("FiSH Key exchange failed!")
      return False

    key.data.key = dh1080_secret(dh)
    key.save()
    
    logging.debug("FiSH: Key set for %s to %s" % (target, key.data.key)) 
    return False

  return True

## fish command

def handle_fish(bot, event):
  """ Handles the fish command """
  args = event.rest.rsplit(" ")
  if not args[0]: event.missing("<commands> [options,...]") ; return

  command = args[0]
  if command == 'help':
    event.reply("help                      -- shows this text")
    event.reply("keyx <nick>               -- Exchanges key")
    event.reply("key  <user|channel> <key> -- Set the key")
    event.reply("del  <user|channel>       -- Removes the key")
    return False

  if command == 'keyx':
    if len(args) != 2: event.missing("keyx <nick>"); return

    userhost = getwho(bot, args[1])
    if userhost == None: return

    user = users.getuser(userhost)
    if user == None:
        event.reply("Unable to exchange key with an unknown user")
        return 

    target = user.data.name
    if target == None: return

    logging.warn("FiSH: Key exchange with  %s (%s)" % (args[1], target))
    dh = DH1080Ctx()
    bot.notice(args[1], dh1080_pack(dh))

    key = KeyStore(stripname(target))
    key.data.dh = pickle.dumps(dh)
    key.save()
    
  if command == 'key':
    if len(args) != 3: event.missing("key <user|channel> <key>"); return
    key = KeyStore(stripname(args[1]))
    key.data.key = args[2]
    key.save()
    event.reply("Stored key for %s" % args[1])

  if command == 'del':
    if len(args) != 2: event.missing("del <user|channel>"); return
    key = KeyStore(stripname(args[1]))

    if not key.data.key: 
      event.reply("No key found for %s" % args[1]); return

    key.data.key=""
    key.data.dh=""
    key.save()
    event.reply("Deleted key %s" % args[1])

from tl.contrib import irccrypt
  
