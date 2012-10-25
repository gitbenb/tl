# tl/db/__init__.py
#
#

""" database interface """

__copyright__ = 'this file is in the public domain'

## tl imports

from tl.lib.config import getmainconfig
from tl.utils.locking import lockdec
from tl.utils.generic import tolatin1
from tl.utils.exception import handle_exception
from tl.lib.datadir import getdatadir
from tl.lib.errors import NoDbConnection, NoDbResult

## basic imports

import _thread
import os
import time
import logging
import sqlite3

## locks

dblock = _thread.allocate_lock()
dblocked = lockdec(dblock)

## Db class

class Db(object):

    """ this class implements a database connection. it connects to the 
        database on initialisation.
    """

    def __init__(self, dbname=None, dbhost=None, dbuser=None, dbpasswd=None, dbtype=None, ddir=None, doconnect=True):
        self.datadir = ddir or getdatadir()
        self.datadir = self.datadir + os.sep + "db" + os.sep
        if hasattr(os, 'mkdir'):
            if not os.path.isdir(self.datadir):
                try: os.mkdir(self.datadir)
                except OSError: pass
        cfg = getmainconfig()
        self.dbname = dbname or cfg.dbname
        if not self.dbname: raise Exception("no db name")
        self.dbhost = dbhost or cfg.dbhost or ""
        self.dbuser = dbuser or cfg.dbuser or ""
        self.dbpasswd = dbpasswd or cfg.dbpasswd or ""
        self.connection = None
        self.timeout = 15
        self.dbtype = dbtype or cfg.dbtype or 'sqlite'
        if doconnect: self.connect()

    def connect(self, timeout=15):
        """ connect to the database. """
        self.timeout = timeout
        logging.info("connecting to %s (%s)" % (self.dbname, self.dbtype))
        if self.dbtype == 'mysql':
            import MySQLdb
            self.connection = MySQLdb.connect(db=self.dbname, host=self.dbhost, user=self.dbuser, passwd=self.dbpasswd, connect_timeout=self.timeout, charset='utf8')
        elif 'sqlite' in self.dbtype:
             self.connection = sqlite3.connect(self.datadir + os.sep + self.dbname, check_same_thread=False)
        elif self.dbtype == 'postgres':
            import psycopg2
            logging.warn('NOTE THAT POSTGRES IS NOT FULLY SUPPORTED')
            self.connection = psycopg2.connect(database=self.dbname, host=self.dbhost, user=self.dbuser, password=self.dbpasswd)
        else:
            logging.error('unknown database type %s' % self.dbtype)
            return 0
        logging.info("%s ok" % self.dbname)
        return 1

    def reconnect(self):
        """ reconnect to the database server. """
        logging.warn('reconnecting')
        return self.connect()

    @dblocked
    def executescript(self, txt):
        cursor = self.cursor()
        cursor.executescript(txt)

    @dblocked
    def execute(self, execstr, args=None, retry=2):
        """ execute string on database. """
        time.sleep(0.001)
        result = None
        execstr = execstr.strip()
        if 'sqlite' in self.dbtype: execstr = execstr.replace('%s', '?')
        if self.dbtype == 'mysql':
            try: self.ping()
            except AttributeError: self.reconnect()                
            except Exception as ex:
                try: self.reconnect()
                except Exception as ex: logging.error('failed reconnect: %s' % str(ex)) ; return
        logging.debug('exec %s %s' % (execstr, args))
        for i in range(retry):
            if not self.connection: self.reconnect()
            if not self.connection: raise NoDbConnection()
            if "sqlite" in self.dbtype:
                try: result = self.doit(execstr, args) ; break
                except sqlite3.OperationalError as ex: logging.error(str(ex))
                except Exception as ex: handle_exception() ; logging.error(str(ex))
            else:
                try: result = self.doit(execstr, args) ; break
                except Exception as ex: logging.error(str(ex))
        return result

    def doit(self, execstr, args=None):
        logging.debug("%s/%s" % (execstr, str(args)))
        cursor = self.cursor()
        nr = 0
        try:
            if args != None:
                if type(args) == tuple or type(args) == list: nr = cursor.execute(execstr, args)
                else: nr = cursor.execute(execstr, (args, ))
            else: nr = cursor.execute(execstr)
        except Exception as ex:
            logging.warn(str(ex))
            if self.dbtype == 'postgres': cursor.execute(""" ROLLBACK """)
            if 'sqlite' in self.dbtype: cursor.close() ; del cursor
            raise 
        got = False
        if execstr.startswith('INSERT'): nr = cursor.lastrowid or nr ; got = True
        elif execstr.startswith('UPDATE'): nr = cursor.rowcount ; got = True
        elif execstr.startswith('DELETE'): nr = cursor.rowcount ; got = True
        if got: self.commit()
        if 'sqlite' in self.dbtype and not got and type(nr) != int():
            nr = cursor.rowcount or cursor.lastrowid
            if nr == -1: nr = 0
        result = None
        try:
            result = cursor.fetchall()
            if not result: result = nr
        except Exception as ex:
            if 'no results to fetch' in str(ex): logging.warn("no results to fetch")
            else: handle_exception()
            result = nr
        cursor.close()
        return result


    def cursor(self):
        """ return cursor to the database. """
        return self.connection.cursor()

    def commit(self):
        """ do a commit on the datase. """
        self.connection.commit()

    def ping(self):
        """ do a ping. """
        return self.connection.ping()

    def close(self):
        """ close database. """
        if 'sqlite' in self.dbtype: self.commit()
        self.connection.close()

    def define(self, definestr):
        try: self.executescript(definestr)
        except Exception as ex:
            if 'already exists' in str(ex): pass
            else: handle_exception()
